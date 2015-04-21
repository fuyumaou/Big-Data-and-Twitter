var input = document.getElementById( "pac-input" );

var initializeMap = function() {

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
			lat: 46.78003, //51.507222,
			lng: 7.96637 //-0.1275
		}, zoom: 8,
		disableDefaultUI: true,
		styles: styles
	};

	var map = new google.maps.Map( document.getElementById( "map-canvas" ), mapOptions );

	map.data.loadGeoJson( "/languageslocations/-180/-90/180/90" );

	var flags = {
		"en": "/static/img/flag-en.png",
		"fr": "/static/img/flag-fr.png",
		"es": "/static/img/flag-es.png",
		"de": "/static/img/flag-de.png",
		"it": "/static/img/flag-it.png"
	};

	map.data.setStyle( function( feature ) {
		var lang = feature.getProperty( "language" );
		var icon = "/static/img/dot.png";
		if ( lang in flags ) { icon = flags[lang]; }
		return { "icon": icon };
	} );

	map.controls[google.maps.ControlPosition.TOP_LEFT].push( input );

	var lastBounds = false;
	var updateLocation = function() {

		// AJAX(map.getBounds().toString(),loadData)
		// check its to the last time to avoid unnecessary loads
		// could also ignore small changes

		// do we need this check? it's only called after a "bounds_changed" event...
		if ( lastBounds != map.getBounds() ) {
			lastBounds = map.getBounds();
			var sw = lastBounds.getSouthWest();
			var ne = lastBounds.getNorthEast();

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

				var languageShareHtml = "";
				for ( i = 0; i < data.length; i++ ) {
					var languageId = data[i][0];
					var languageTweetCount = data[i][1];
					var languageTweetShare = ( languageTweetCount * 100 / tweetCount ).toFixed( 1 );

					var languageShareDisplay = "<div><img src=" + flags[languageId] + " alt=" +
								languageId + "></img>:" + languageTweetShare + "%</div>\n";

					if ( !( languageId in flags ) ) {
						languageShareDisplay = "<div>" + languageId + ": " + languageTweetShare +
							"%</div>\n";
					}

					languageShareHtml += languageShareDisplay;
				}
				$( "#languages" ).html( languageShareHtml );
			} );

			$.get( "/words/" + sw.lng() + "/" + sw.lat() + "/" + ne.lng() + "/" + ne.lat() + "/20",
							function( response ) {
				var words = response.words;
				var wordCloudHtml = "";
				for ( var i = 0; i < words.length; i++ ) {
					wordCloudHtml += "<div>" +  words[i].word + ": " + words[i].count + "</div>\n";
				}
				$( "#wordcloud" ).html( wordCloudHtml );
			} );

		}
	};

	//updateLocation()
	google.maps.event.addListener( map, "bounds_changed", updateLocation );

	//temporarily ignore the sheer number of requests that would get sent here

	//Search box, code from https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete

	var autocomplete = new google.maps.places.Autocomplete( input );
	autocomplete.bindTo( "bounds", map );

	var infowindow = new google.maps.InfoWindow();

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
		map.setZoom( 10 );
	} );

};

google.maps.event.addDomListener( window, "load", initializeMap );
