# the unopinionated itemset generator

![](http://s10.postimg.org/4ut7ll3mx/Demo1.png)

The other item sets on the market nowadays generally intend to provide their own recommendations usually off high profile players or high ranked players; this is intended to reflect the user's own buy decisions and simplify their in-game shop clickstream as opposed to making them conform to someone else's idea of a meta. This project is probably not very Pythonic, it was more or less a "learn Python" project for me, because I wanted to try something new for the Challenge.

Was originally going to use SciPy/NumPy and look at win rates by items, but since most people have less than 100 matches for any specific champion, the n-size seems far too low to be tolerable. Maybe it'd come in handy for things like aggregating large-scale data, but a player's 40 games is overkill or unusable.

I guess you can also copy your favourite pro player's builds or something, in addition to your own. 

## Caching
`requests_cache` is used. This defaults to `sqlite`. If you plan on actually deploying this, you will probably want to not use sqlite.  Or don't, that's up to you.

## Rate limiting
To not go over rate limits, a job queue is used. A worker will process requests at a determined speed. If you are using a higher limit key, you can just run additional workers to process multiple grabs at the same time. Jobs will not be processed at all until you have a worker process running.

## Running
* Have a redis server running.
* `pip install requests flask requests_cache simplejson dataset redis rq`
* Edit `Constants.py` with your API key and DSN for database support.
* `python main.py` (or hook it up to WSGI/nginx/something; it's a standard Flask application)
* http://localhost:5000
