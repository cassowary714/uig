from flask import Flask, session, escape, flash, redirect, render_template, make_response, request, url_for, Response
import dataset
import shiv.Summoner as Summoner
import shiv.Champion as Champion
import shiv.Item as Item
import shiv.Build as Build
import Constants
import simplejson as json
from rq import Queue
from redis import Redis
import Worker

# Setup
app = Flask(__name__)
app.secret_key = b'\x0f7\xe9>\x85\x19\xb5N0NG\xc7\x93/$\xb5\xb2\x0e`F\\\xf1\xbd\x98'
redis_conn = Redis()
q = Queue(connection=redis_conn, default_timeout=86400)


@app.route('/', methods=['GET'])
def index():
    with open('data/champion.json') as c:
        heroes = json.load(c)
    return render_template('index.html', heroes=heroes['data'], regions=Constants.REGIONS)


@app.route('/itemsets/<uuid>', methods=['GET'])
def get_results_json(uuid):
    job = q.fetch_job(uuid)
    if not job or not job.id or job.id is not uuid:
        flash("This result does not exist.")
        return redirect(url_for('index'))

    region = job.kwargs['region']
    summoner_id = job.kwargs['sumid']
    champion_id = job.kwargs['hero']

    query = 'SELECT *, itemId, AVG(timestamp) as ts, COUNT(itemid) as ct FROM events WHERE championId={0} AND summonerId={1} AND region="{2}" GROUP BY itemId ORDER BY ts ASC;'
    db = dataset.connect(Constants.DSN)
    result = db.query(query.format(int(champion_id), int(summoner_id), region))

    loadout = {'starting': [], 'consumable': [], 'early': [], 'core': [], 'situational': []}
    loadout_names = {'starting': 'Starting items', 'consumable': 'Consumable items', 'early': 'Early game and first back items', 'core': 'Core items', 'situational': 'Situational'}

    for row in result:
        ts = int(row['ts'])
        if Item.Consumable(row['itemId']):
            loadout['consumable'].append(row['itemId'])
        elif ts < 250000:
            loadout['starting'].append(row['itemId'])
        elif ts < 500000 and ts > 250000:
            loadout['early'].append(row['itemId'])
        elif ts < 1000000 and ts > 500000 and Item.Basic(row['itemId']):
            loadout['early'].append(row['itemId'])
        elif ts < 1500000 and ts > 500000 and not Item.Basic(row['itemId']):
            loadout['core'].append(row['itemId'])
        elif ts > 1500000 and not Item.Basic(row['itemId']):
            loadout['situational'].append(row['itemId'])

    for key in loadout:
        loadout[key].sort()

    S = Summoner.GetSummonerById(region, summoner_id)
    json_data = Build.Output(loadout_names=loadout_names, loadout=loadout, summoner=S)  # json.dumps(loadout, use_decimal=True)

    try:
        is_json = request.args.get('json', '')
        if is_json:
            return json_data
    except KeyError:
        pass
    return render_template('acquire.html', json=json_data, data=loadout, summoner=S, champion=Champion.Id(champion_id), loadout_names=loadout_names)


@app.route('/queue/<uuid>', methods=['GET'])
def get_wait_page(uuid):
    job = q.fetch_job(uuid)
    if not job or not job.id or job.id is not uuid:
        flash("This result does not exist.")
        return redirect(url_for('index'))
    status = job.get_status()
    if status == 'failed':
        flash("Unfortunately, your job has failed (this could be due to rate limit limitations or taking far too long, or general service instability. Please try again.")
        return redirect(url_for('index'))
    if status == 'started':
        status = 'running'
    if status == 'finished':
        return redirect('/itemsets/{job}'.format(job=job.id))
    return render_template('process.html', id=job.id, result_status=status)


@app.route('/', methods=['POST'])
def acquire():
    error = None
    if request.method == 'POST' and request.form['hero'] and request.form['hero'] in Constants.HEROES and request.form['name'] and request.form['region'] and request.form['region'] in Constants.REGIONS and len(request.form['name']) > 3:
        # Worth a try, looks like all fields are filled in
        S = Summoner.GetSummonerByName(region=request.form['region'], ign=request.form['name'])
        if not S or not S['summonerLevel']:
            error = "There was a problem getting that summoner, or it does not exist. Double check your input."
        elif S['summonerLevel'] < 30:
            error = "Your summoner must be level 30."
        if error:
            flash(error)
            return redirect(url_for('index'))

        # Most bases should be covered now, hmu ml
        Matchlist = Summoner.GetSummonerMatchlist(region=request.form['region'], sumid=S['id'], hero=request.form['hero'])
        if Matchlist and Matchlist is not None:
            total_games = Matchlist['totalGames']
            if total_games < 50:
                error = "You don't have enough ranked games for this champion for a useful result."
                pass
            if not error:
                # Looks good by now, at least 50 games and ranked is valid response
                # Push job to queue worker to pick up matches
                # def get_user_matches(matchlist, region, sumid, hero):
                try:
                    job = q.enqueue_call(func=Worker.get_user_matches, kwargs={'matchlist': Matchlist, 'region': request.form['region'], 'sumid': S['id'], 'hero': request.form['hero']}, timeout=86400, result_ttl=604800)
                    job_id = job.id
                    return redirect('/queue/{job}'.format(job=job_id))
                except:
                    flash("There was an error trying to process your games.")
                    return redirect(url_for('index'))
        else:
            error = "We couldn't find your games: did you play ranked this season?"

        if error:
            flash(error)
            return redirect(url_for('index'))
        return render_template('acquire.html', content=json.dumps(S), summoner=S, champion=Champion.Id(request.form['hero']))

    else:
        error = "Invalid: summoner does not exist."


    if error:
        flash(error)
        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
