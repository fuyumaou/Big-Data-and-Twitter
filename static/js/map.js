var input = document.getElementById( "pac-input" );

var initializeMap = function() {
	//help from http://stackoverflow.com/a/24234818/1779797

	fx = google.maps.InfoWindow.prototype.setPosition
	google.maps.InfoWindow.prototype.setPosition = function() {
		fx.apply(this, arguments);
		//this property isn't documented, but as it seems
		//it's only defined for InfoWindows opened on POI's
		var sentimentBar = $( "sentiment-canvas" ).sentimentBar();
		if (this.logAsInternal) {
			$("#places-account").text('');
			$("#places-content").html('<center><img width="150" src="/static/img/loading.gif" alt="Loading" /></center>');

			var infoWindow = this;
			var name = infoWindow.getContent().firstChild.firstChild.nodeValue;
			var pos = infoWindow.position;
			console.log(name);
			console.log(pos.lat() + ", " + pos.lng())
			$.get("/place/" + name + "/" + pos.lat() + "/" + pos.lng(), function(response) {
				console.log(response);
				if(response.account_id){
					$("#places-account").html('<a class="twitter-timeline" href="https://twitter.com/tcb1024" data-widget-id="594975506904256512"   data-user-id="'+response.account_id+'">Tweets by +'+response.account_name+'+</a>')
					twttr.widgets.load()
				}
				else {
					$("#places-account").html('');
				}

				$("#places-content").html('Average Tweet Sentiment: ' + Math.round(response.average_sentiment * 100) /100 +' / 10');
				sentimentBar.setValue( response.average_sentiment );
				//TODO: make this red to green rather than a number
				// http://wbotelhos.com/raty
				//TODO: display thumbsup vs thumbsdown (imgs already on server)
			})
		}
	}

	var styles = [
		{
			"featureType": "road",
			"elementType": "geometry",
			"stylers": [
				{ "hue": "#cc00ff" },
				{ "saturation": -74 },
				{ "lightness": 23 }
			]
		}, {
			"featureType": "landscape",
			"stylers": [
				{ "saturation": -100 },
				{ "lightness": 50 }
			]
		}, {
			"featureType": "poi",
			"elementType": "geometry",
			"stylers": [
				{ "hue": "#55ff00" },
				{ "saturation": 67 }
			]
		}, {
			"featureType": "transit",
			"stylers": [
				{ "visibility": "off" }
			]
		}, {
			"featureType": "water",
			"stylers": [
				{ "hue": "#0077ff" }
			]
		}, {
			"featureType": "road",
			"elementType": "labels",
			"stylers": [
				{ "visibility": "off" }
			]
		}, {
			"featureType": "road.highway",
			"stylers": [
				{ "lightness": 21 }
			]
		}
	];

	var mapOptions = {
		center: {
			lat: 46.78003,
			lng: 7.96637
		}, zoom: 8,
		minZoom: 5,
		disableDefaultUI: true,
		styles: styles
	};

	var map = new google.maps.Map( document.getElementById( "map-canvas" ), mapOptions );

	var flags = {
		"en": "/static/img/flag-en.png",
		"fr": "/static/img/flag-fr.png",
		"es": "/static/img/flag-es.png",
		"de": "/static/img/flag-de.png",
		"it": "/static/img/flag-it.png"
	};

	// Leaving this here for nostalgia & in case the new way is too slow
	/* $.get( "/languageslocations/-180/-90/180/90", function( response ) {
		map.data.addGeoJson( response );

		map.data.setStyle( function( feature ) {
			var lang = feature.getProperty( "language" );
			var icon = "/static/img/dot.png";
			if ( lang in flags ) { icon = flags[lang]; }
			return { "icon": icon };
		} );
	} ); */

	//map.controls[google.maps.ControlPosition.TOP_LEFT].push( input );

	var circle = $( "circle-canvas" ).circle();

	var lastBounds = false;
	var updateLocation = function() {

		// AJAX(map.getBounds().toString(),loadData)

		// ignore changes smaller than 5%
		change = 0.05;
		var update = true;
		var bounds = map.getBounds();
		if ( lastBounds ) {
			var width = lastBounds.getSouthWest().lng() - lastBounds.getNorthEast().lng();
			var height = lastBounds.getSouthWest().lat() - lastBounds.getNorthEast().lat();
			update = Math.abs( ( lastBounds.getSouthWest().lng() - bounds.getSouthWest().lng() ) / width ) > change ||
							 Math.abs( ( lastBounds.getNorthEast().lng() - bounds.getNorthEast().lng() ) / width ) > change ||
							 Math.abs( ( lastBounds.getSouthWest().lat() - bounds.getSouthWest().lat() ) / height ) > change ||
							 Math.abs( ( lastBounds.getNorthEast().lat() - bounds.getNorthEast().lat() ) / height ) > change
		}

		if ( update ) {
			var sw = bounds.getSouthWest();
			var ne = bounds.getNorthEast();

			// create a closure so that when the server replies we use the right lastBounds, bounds etc.
			( function( lastBounds, bounds, sw, ne ) {
			$.get( "/languageslocations/" + sw.lng() + "/" + sw.lat() + "/" + ne.lng() + "/" + ne.lat(),
			function( response ) {

				// Only add features that weren't in lastBounds (ie new ones)
				var filteredFeatures = response.features.filter( function( feature ) {
					var coords = feature.geometry.coordinates;
					var featureLatLng = new google.maps.LatLng( coords[1], coords[0] );
					return lastBounds ? !lastBounds.contains( featureLatLng ) : true;
				} );
				var filteredResponse = { "type": "FeatureCollection", "features": filteredFeatures };
				map.data.addGeoJson( filteredResponse );

				// Remove all feautures which aren't on the screen
				map.data.forEach( function( feature ) {
					var featureLatLng = feature.getGeometry().get();
					if ( !bounds.contains( featureLatLng ) ) {
						map.data.remove( feature );
					}
				} );
				map.data.setStyle( function( feature ) {
					var lang = feature.getProperty( "language" );
					var icon = "/static/img/dot.png";
					if ( lang in flags ) { icon = flags[lang]; }
					return { "icon": icon };
				} );
			} ); } )( lastBounds, bounds, sw, ne );

			$.get( "/languages/" + sw.lng() + "/" + sw.lat() + "/" + ne.lng() + "/" + ne.lat(),
			function( response ) {
				var data = response.data;

				// Sort by tweet count
				data.sort( function( a, b ) {
					return b[1] - a[1];
				} );

				var tweetCount = 0;
				for ( var i = 0; i < data.length; i++ ) {
					tweetCount += data[i][1];
				}

				// # of segs not including "other"
				var circlePortions = [];
				var otherShare = 100;
				var minShareSize = 1.0;
				var shareLargeEnough = true;

				var languageShareHtml = "";
				for ( i = 0; i < data.length; i++ ) {
					var languageId = data[i][0];
					var languageTweetCount = data[i][1];
					var languageTweetShare = ( languageTweetCount * 100 / tweetCount ).toFixed( 1 );

					if ( languageTweetShare >= minShareSize ) {
						var languageShareDisplay = "<div><img src=" + flags[languageId] + " alt=" +
									languageId + "></img>: " + languageTweetShare + "%</div>\n";

						if ( !( languageId in flags ) ) {
							languageShareDisplay = "<div>" + languageId + ": " + languageTweetShare +
								"%</div>\n";
						}

						languageShareHtml += languageShareDisplay;

						circlePortions.push( parseFloat( languageTweetShare ) );
						otherShare -= parseFloat( languageTweetShare );
					}
				}
				$( "#languages" ).html( languageShareHtml );
				if ( otherShare > 1 && otherShare < 100 ) {
					circlePortions.push( otherShare );
					circle.drawLangaugeSegments( circlePortions, true );
				} else {
					circle.drawLangaugeSegments( circlePortions, false );
				}
			} );

			$.get( "/words/" + sw.lng() + "/" + sw.lat() + "/" + ne.lng() + "/" + ne.lat() + "/15", function( response ) {
				if (response.words.length > 0) {
					var words = response.words;
					console.log(words);
					for (var i = 0; i < words.length; i++) {
						var word = words[i].word;
						var count = words[i].count;
						words[i] = {
							text: word,
							weight: count
						}
					}
					$("#wordcloud").html("");
					$("#wordcloud").jQCloud(words, {
					  width: 180,
					  height: 200,
					  shape: "rectangular"
					});
				}
			} );

			lastBounds = bounds;
		}

	};

	//updateLocation()
	google.maps.event.addListener( map, "idle", updateLocation );

	//temporarily ignore the sheer number of requests that would get sent here

	//Search box, code from https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete

	var autocomplete = new google.maps.places.Autocomplete( input );
	autocomplete.bindTo( "bounds", map );

	var infowindow = new google.maps.InfoWindow();
	var marker = new google.maps.Marker({
		map: map
	});
	google.maps.event.addListener(marker, 'click', function() {
		infowindow.open(map, marker);
	});

	google.maps.event.addListener( autocomplete, "place_changed", function() {
		infowindow.close();
		var place = autocomplete.getPlace();
		if ( !place.geometry ) {
			return;
		}

		// If the place has a geometry, then present it on a map.
		if ( place.geometry.viewport ) {
			map.fitBounds( place.geometry.viewport );
		} else {
			map.setCenter( place.geometry.location );
		}
		map.setZoom(15);
	});

};

google.maps.event.addDomListener( window, "load", initializeMap );
