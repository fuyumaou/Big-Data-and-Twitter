var input = document.getElementById("pac-input");

var initializeMap = function() {
	//set up the map
	//----------------
	var styles = [{
		"featureType": "road",
		"elementType": "geometry",
		"stylers": [{
			"hue": "#cc00ff"
		}, {
			"saturation": -74
		}, {
			"lightness": 23
		}]
	}, {
		"featureType": "landscape",
		"stylers": [{
			"saturation": -100
		}, {
			"lightness": 50
		}]
	}, {
		"featureType": "poi",
		"elementType": "geometry",
		"stylers": [{
			"hue": "#55ff00"
		}, {
			"saturation": 67
		}]
	}, {
		"featureType": "water",
		"stylers": [{
			"hue": "#0077ff"
		}]
	}, {
		"featureType": "road",
		"elementType": "labels",
		"stylers": [{
			"visibility": "off"
		}]
	}, {
		"featureType": "road.highway",
		"stylers": [{
			"lightness": 21
		}]
	}];

	var mapOptions = {
		center: {
			lat: 46.78003,
			lng: 7.96637
		},
		zoom: 8,
		minZoom: 5,
		disableDefaultUI: true,
		styles: styles
	};

	map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

		overlay = new google.maps.OverlayView();
		overlay.draw = function() {};
		overlay.setMap(map);

	//Stuff used in the places tab
	//----------------------------

	//help from http://stackoverflow.com/a/24234818/1779797
	fx = google.maps.InfoWindow.prototype.setPosition;
	google.maps.InfoWindow.prototype.setPosition = function() {
		fx.apply(this, arguments);
		//this property isn"t documented, but as it seems
		//it"s only defined for InfoWindows opened on POI"s
		if (this.logAsInternal) {
			$("#places-account").text("");
			$("#places-title").text("");
			$("#places-content").html("<center><img width=\"150\" src=\"/static/img/loading.gif\" alt=\"Loading\" /></center>");

			var infoWindow = this;
			var name = infoWindow.getContent().firstChild.firstChild.nodeValue;
			var pos = infoWindow.position;
			var sentimentBar = $("#sentiment-canvas").sentimentBar();
			$("#places-bar").show();
			sentimentBar.hide();
			// console.log(name);
			// console.log(pos.lat() + ", " + pos.lng());
			$.get("/place/" + name + "/" + pos.lat() + "/" + pos.lng(), function(response) {
				// console.log(response);
				$("#places-title").text(name);
				if (response.account_id) {
					$("#places-account").html("<a class=\"twitter-timeline\" href=\"https://twitter.com/tcb1024\" data-widget-id=\"594975506904256512\"	 data-user-id=\"" + response.account_id + "\">Tweets by +" + response.account_name + "+</a>");
					twttr.widgets.load();
				} else {
					$("#places-account").html("No official account found");
				}
				$("#places-content").text("Twitter Users' Opinion");
				sentimentBar.setValue(response.average_sentiment);
				sentimentBar.show();
				// http://wbotelhos.com/raty
				//TODO: display thumbsup vs thumbsdown (imgs already on server)
			});
		}
	};

	//Stuff used for the languages tab
	//--------------------------------

	var flags = {
		"en": "/static/img/flag-en.png",
		"fr": "/static/img/flag-fr.png",
		"es": "/static/img/flag-es.png",
		"de": "/static/img/flag-de.png",
		"it": "/static/img/flag-it.png",
		"tr": "/static/img/flag-tr.png",
		"pt": "/static/img/flag-pt.png",
		"ru": "/static/img/flag-ru.png"
	};
	// From twitter:
	var languageCodes = {
		"ar": "Arabic",
		"bg": "Bulgarian",
		"bs": "Bosnian",
		"da": "Danish",
		"de": "German",
		"en": "English",
		"en-gb": "English UK",
		"es": "Spanish",
		"et": "Estonian",
		"fa": "Farsi",
		"fi": "Finnish",
		"fil": "Filipino",
		"fr": "French",
		"he": "Hebrew",
		"hi": "Hindi",
		"hr": "Croatian",
		"hu": "Hungarian",
		"id": "Indonesian",
		"it": "Italian",
		"ja": "Japanese",
		"ko": "Korean",
		"lt": "Lithuanian",
		"msa": "Malay",
		"nl": "Dutch",
		"no": "Norwegian",
		"pl": "Polish",
		"pt": "Portuguese",
		"ro": "Romanian",
		"ru": "Russian",
		"sl": "Slovene",
		"sr": "Serbian",
		"sv": "Swedish",
		"tl": "Tagalog",
		"th": "Thai",
		"tr": "Turkish",
		"uk": "Ukranian",
		"ur": "Urdu",
		"vi": "Vietnamese",
		"zh-cn": "Simplified Chinese",
		"zh-tw": "Traditional Chinese",
	};
	map.data.setStyle(function(feature) {
		var lang = feature.getProperty("language");
		var icon = "/static/img/dot.png";
		if (lang in flags) {
			icon = flags[lang];
		}
		return {
			"icon": icon
		};
	});
	//get all the tweets
	tweets = [];
	$.get("/allTweetLangs", function(response) {
		tweets = response.tweets;
		gj = [];
		for (var tweetn in tweets) {
			if (!tweets.hasOwnProperty(tweetn)) continue;
			tweet = tweets[tweetn];
			gj.push({
				type: "Feature",
				properties: {
					language: tweet[0]
				},
				geometry: {
					type: "Point",
					coordinates: tweet[1]
				}
			});
		}
		map.data.addGeoJson({
			type: "FeatureCollection",
			features: gj
		});
		updateLocation();
	});

	 var tweetsOnScreen = []; //a list of all tweets on the screen for faster searching


	updateCircle = function (x,y,r) {
		var p = overlay.getProjection();
		var bounds = map.getBounds();
		var topleft = new google.maps.LatLng(bounds.getNorthEast().lat(),bounds.getSouthWest().lng());
		var wrongby = p.fromLatLngToDivPixel(topleft);

		var countByLang = {};
		var tweetCount = 0;
		var circlePortions = [];
		var otherShare = 100;
		var minShareSize = 1.0;
		var shareLargeEnough = true;

		for (var i = 0; i < tweetsOnScreen.length; i++) {
			var tweet = tweetsOnScreen[i];
			var lang = tweet[0];
			var loc = tweet[1];
			loc = new google.maps.LatLng(loc[1], loc[0]);
			pos = p.fromLatLngToDivPixel(loc);
			a = pos.x - x - wrongby.x;
			b = pos.y - y - wrongby.y;

			if (a*a + b*b < r*r) {
				if (!(lang in countByLang)) countByLang[lang] = 0;
				countByLang[lang] += 1;
				tweetCount += 1;
			}
		}

		var langs = Object.keys( countByLang );
		langs.sort(function(a, b) {
			return countByLang[b] - countByLang[a];
		});

		var languageShareHtml = "";
		for (var i = 0; i < langs.length; i++) {
			var lang = langs[i];
			var languageTweetCount = countByLang[lang];
			var languageTweetShare = (languageTweetCount * 100 / tweetCount).toFixed(1);

			if (languageTweetShare >= minShareSize) {
				// (1 + (i % 5)) is hackish. we probably want more colours or something anyway...
				var dotImg = "<td><img class=\"dot\" src=\"/static/img/dot" + (1 + (i % 5)) + ".png\"></img></td>";
				var langName = (lang in languageCodes) ? languageCodes[lang] : lang;
				languageShareHtml += "<tr class=\"lang-stat\"><td class=\"lang-name\">" + langName +"</td>"+ dotImg +"<td class=\"percent-column\">"+ languageTweetShare + "%</td></tr>\n";

				circlePortions.push(parseFloat(languageTweetShare));
				otherShare -= parseFloat(languageTweetShare);
			}
		}
		if (otherShare > 1 && otherShare < 100) {
			circlePortions.push(otherShare);
			languageShareHtml += "<tr class=\"lang-stat\"><td class=\"lang-name\">Others</td><td>&#8212</td><td class=\"percent-column\">"+ otherShare.toFixed(1) + "%</td></tr>\n";
			drawLangaugeSegments(circlePortions, true);
		} else {
			drawLangaugeSegments(circlePortions, false);
		}
		$("#languages").html("<table>\n" + languageShareHtml + "\n</table>");
	};


	var updateLocation = function() {
		var bounds = map.getBounds();
		tweetsOnScreen=[];
		for (var i = 0; i < tweets.length; i++) {
			var tweet = tweets[i];
			var lang = tweet[0];
			var loc = tweet[1];
			if (bounds.contains(new google.maps.LatLng(loc[1], loc[0]))) {
				tweetsOnScreen.push(tweet)
			}
		}

		//Word cloud
		var bounds_sw = bounds.getSouthWest();
		var bounds_ne = bounds.getNorthEast();
		$.get( "/words/" + bounds_sw.lng() + "/" + bounds_sw.lat() + "/" + bounds_ne.lng() + "/" + bounds_ne.lat() + "/10", function( response ) {
			var words = [];
			$("#wordcloud").html("");
			if (response.words.length > 0) {
				words = response.words;
				// console.log(words);
				for (var i = 0; i < words.length; i++) {
					var word = words[i].word;
					var count = words[i].count;
					words[i] = {
						text: word,
						weight: count
					};
				}

				$("#wordcloud").jQCloud(words, {
					width: 250,
					height: 300,
					shape: "rectangular"
				});
			} else {
				$("#wordcloud").html("No word cloud for this area");
			}
		} );

	};

	//updateLocation()
	google.maps.event.addListener(map, "idle", updateLocation);

	//temporarily ignore the sheer number of requests that would get sent here

	//Search box, code from https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete

	var autocomplete = new google.maps.places.Autocomplete(input);
	autocomplete.bindTo("bounds", map);

	var infowindow = new google.maps.InfoWindow();
	var marker = new google.maps.Marker({
		map: map
	});
	google.maps.event.addListener(marker, "click", function() {
		infowindow.open(map, marker);
	});

	google.maps.event.addListener(autocomplete, "place_changed", function() {
		infowindow.close();
		var place = autocomplete.getPlace();
		if (!place.geometry) {
			return;
		}

		// If the place has a geometry, then present it on a map.
		if (place.geometry.viewport) {
			map.fitBounds(place.geometry.viewport);
		} else {
			map.setCenter(place.geometry.location);
		}
		map.setZoom(15);
	});

};

google.maps.event.addDomListener(window, "load", initializeMap);
