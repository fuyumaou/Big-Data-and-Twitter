var canvas = document.getElementById( "circle-canvas" );
var ctx = canvas.getContext( "2d" );

ctx.shadowColor = "rgba( 0, 0, 0, 0.5 )";
ctx.shadowBlur = 10;

// different centre and radius to allow for buffer around circle for shadow etc
var c = canvas.width / 2;
var r = ( canvas.width - 60 ) / 2;

ctx.beginPath();
ctx.fillStyle = "rgba( 0, 0, 0, 0.1 )";
ctx.arc( c, c, r, 0, 2 * Math.PI );
ctx.fill();

ctx.lineWidth = 4;
ctx.strokeStyle = "rgb( 255, 255, 255 )";
ctx.beginPath();
ctx.arc( c, c, r, 0, 2 * Math.PI );
ctx.stroke();

var getRndColor = function() {
	var r = 255 * Math.random() | 0,
			g = 255 * Math.random() | 0,
			b = 255 * Math.random() | 0;
	return "rgb(" + r + "," + g + "," + b + ")";
};

var segColourPalette = [
	"rgba( 61, 232, 50, 1.0 )",
	"rgba( 0, 178, 255, 1.0 )",
	"rgba( 195, 98, 235, 1.0 )",
	"rgba( 0, 221, 245, 1.0 )",
	"rgba( 255, 72, 190, 1.0 )"
];

$.fn.circle = function() {
	var $circle = this;
	$circle.drawLangaugeSegments = function( circlePortions ) {
		var ctx = canvas.getContext( "2d" );
		ctx.clearRect( 0, 0, canvas.width, canvas.height );

		ctx.beginPath();
		ctx.fillStyle = "rgba( 0, 0, 0, 0.1 )";
		ctx.arc( c, c, r, 0, 2 * Math.PI );
		ctx.fill();

		ctx.save();
		ctx.translate( 0, c * 2 );
		ctx.rotate( 3 * Math.PI / 2 );
		ctx.lineWidth = 4;
		var lastAngle = 0;
		var numOfSegs = circlePortions.length;
		var gap = 0.003 * 2 * Math.PI;
		for ( var i = 0; i < numOfSegs; i++ ) {
			/*var shade = Math.floor( 255 * ( numOfSegs - i ) / numOfSegs );
			ctx.strokeStyle = "rgb(" + shade + "," + shade + "," + shade + ")";*/
			if ( i === numOfSegs - 1 ) {
				ctx.strokeStyle = "white";
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
		left:	e.pageX - c,
		top:	 e.pageY - c
	} );
} );
