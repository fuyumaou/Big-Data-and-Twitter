var LINE_GAP = 1.5, // Degrees
		LINE_WIDTH = 8;

var LINE_OPACITY = 1.0,
		OTHERS_LINE_COLOUR = "rgba( 255, 255, 255, " + LINE_OPACITY + " )",
		NO_DATA_STYLE = "rgba( 0, 0, 1, 0.5 )",
		segColourPalette = [
	"rgba( 61, 232, 50, 1.0 )",
	"rgba( 0, 178, 255, 1.0 )",
	"rgba( 195, 98, 235, 1.0 )",
	"rgba( 0, 221, 245, 1.0 )",
	"rgba( 255, 72, 190, 1.0 )"
];

// Shadow contributes to this so it might be more opaque than expected if using shadow
var CIRCLE_OPACITY = 0.1;

// Warning: too much blur might lead to clipping at edges of canvas element
var SHADOW_BLUR = 10,
		SHADOW_OPACITY = 0.5;

//------------------------------------------------------------------------------

var canvas = document.getElementById( "circle-canvas" );
var ctx = canvas.getContext( "2d" );

ctx.shadowColor = "rgba( 0, 0, 0, " + SHADOW_OPACITY + " )";
ctx.shadowBlur = SHADOW_BLUR;

// different centre and radius to allow for buffer around circle for shadow etc
var c = canvas.width / 2,
		r = ( canvas.width - 60 ) / 2;

// Usage eg: var circle = getCircle();
//           circle.drawLangaugeSegments( [30, 25, 20, 15, 10] );
function drawLangaugeSegments( circlePortions, drawOthers ) {
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

	if ( circlePortions.length === 0 ) {
		ctx.strokeStyle = NO_DATA_STYLE;
		ctx.beginPath();
		ctx.arc( c, c, r, 0, 2 * Math.PI );
		ctx.stroke();
	} else {
		for ( var i = 0; i < numOfSegs; i++ ) {
			/*var shade = Math.floor( 255 * ( numOfSegs - i ) / numOfSegs );
			ctx.strokeStyle = "rgb(" + shade + "," + shade + "," + shade + ")";*/
			if ( drawOthers && i === numOfSegs - 1 ) {
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
	}

	ctx.restore();
};


$( document ).on( "mousemove", function( e ) {
	// console.log(document.documentElement.clientWidth);
	$( "#circle-canvas" ).css( {
		left: Math.min(document.documentElement.clientWidth - 2 * c, e.pageX - c),
		top: Math.min(document.documentElement.clientHeight - 2 * c, e.pageY - c)
	} );
	updateCircle(e.pageX,e.pageY,r)
} );
