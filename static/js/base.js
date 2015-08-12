$(function() {
	// var pattern = Trianglify({cell_size: 200, width: window.innerWidth, height: window.innerHeight }); document.body.style['background-image'] = 'url('+pattern.png()+')';
	$(".resp-item").error(function() {
		if ($(this).attr("data-item")) {
			$(this).attr('src', '//ddragon.leagueoflegends.com/cdn/5.5.1/img/item/'+$(this).attr('data-item')+'.png');
		}
	});
});
