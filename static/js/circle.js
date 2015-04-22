var LINE_GAP = 1.5; // Degrees
var LINE_WIDTH = 6;

var LINE_OPACITY = 1.0;
var OTHERS_LINE_COLOUR = "rgba( 255, 255, 255, " + LINE_OPACITY + " )";
var segColourPalette = [
	"rgba( 61, 232, 50, 1.0 )",
	"rgba( 0, 178, 255, 1.0 )",
	"rgba( 195, 98, 235, 1.0 )",
	"rgba( 0, 221, 245, 1.0 )",
	"rgba( 255, 72, 190, 1.0 )"
];

// Shadow contributes to this so it might be more opaque than expected if using shadow
var CIRCLE_OPACITY = 0.1;

// Warning: too much blur might lead to clipping at edges of canvas element
var SHADOW_BLUR = 10;
var SHADOW_OPACITY = 0.5;

//------------------------------------------------------------------------------

var canvas = document.getElementById( "circle-canvas" );
var ctx = canvas.getContext( "2d" );

ctx.shadowColor = "rgba( 0, 0, 0, " + SHADOW_OPACITY + " )";
ctx.shadowBlur = SHADOW_BLUR;

// different centre and radius to allow for buffer around circle for shadow etc
var c = canvas.width / 2;
var r = ( canvas.width - 60 ) / 2;

// Usage eg: var circle = $( "#circle-canvas" ).circle();
//					 circle.drawLangaugeSegments( [30, 25, 20, 15, 10] );
$.fn.circle = function() {

	var $circle = this;

  $circle.drawLangaugeSegments = function( circlePortions ) {
		var ctx = canvas.getContext( "2d" );
		ctx.clearRect( 0, 0, canvas.width, canvas.height );

		ctx.beginPath();
		ctx.fillStyle = "rgba( 0, 0, 0, " + CIRCLE_OPACITY + " )";
		ctx.arc( c, c, r, 0, 2 * Math.PI );
		ctx.fill();

		ctx.save();
		ctx.translate( 0, c * 2 );
		ctx.rotate( 3 * Math.PI / 2 );
		ctx.lineWidth = LINE_WIDTH;
		var lastAngle = 0;
		var numOfSegs = circlePortions.length;
		var gap = LINE_GAP * 2 * Math.PI / 360;

		for ( var i = 0; i < numOfSegs; i++ ) {
			/*var shade = Math.floor( 255 * ( numOfSegs - i ) / numOfSegs );
			ctx.strokeStyle = "rgb(" + shade + "," + shade + "," + shade + ")";*/
			if ( i === numOfSegs - 1 ) {
				ctx.strokeStyle = OTHERS_LINE_COLOUR;
			} else {
				ctx.strokeStyle = segColourPalette[i % segColourPalette.length];
			}
			ctx.beginPath();
			var endAngle = lastAngle + 2 * Math.PI * circlePortions[i] / 100 - gap;
			ctx.arc( c, c, r, lastAngle, endAngle );
			ctx.stroke();
			lastAngle = endAngle + gap;
		}

		ctx.restore();
	};

	return $circle;
};

$( document ).on( "mousemove", function( e ) {
	$( "#circle-canvas" ).css( {
		left: e.pageX - c,
		top: e.pageY - c
	} );
} );
