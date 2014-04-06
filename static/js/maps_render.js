var latlng = new google.maps.LatLng(37.780278, -122.414060)
var mapStyle = [
    {"featureType": "water","elementType": "geometry","stylers": [{ "hue": "#0066ff" },{ "lightness": -20 },{ "saturation": -33 },{ "gamma": 0.77 }]},
    {"featureType": "water","elementType": "labels","stylers": [{ "visibility": "off" }]},
    {"featureType": "poi.park","elementType": "geometry","stylers": [{ "hue": "#00ff00" },{ "lightness": 58 },{ "gamma": 0.3 },{ "saturation": 4 }]},
    {"featureType": "transit","stylers": [{ "visibility": "off" }]},
    {"featureType": "poi.business", "elementType": "labels", "stylers": [{ "visibility": "off" }]},
    {"featureType": "road","elementType": "geometry.stroke","stylers": [{ "visibility": "off" }]},
    {"featureType": "road.highway.controlled_access","stylers": [{ "visibility": "simplified" }]},
    {"featureType": "road.highway","elementType": "geometry","stylers": [{ "hue": "#ffbb00" },{ "saturation": -5 },{ "lightness": 47 }, { "gamma":.49 }]},
    {"featureType": "road.highway.controlled_access","elementType": "geometry","stylers": [{ "hue": "#ffbb00" },{ "saturation": -5 },{ "lightness": 47 }, { "gamma":1 }]},
    {"featureType": "road.highway.controlled_access","elementType": "labels","stylers": [{ "visibility": "off" }]},
    {"featureType": "poi.park","stylers": [{"visibility": "simplified"}]},
    {"featureType": "poi.school","stylers": [{"visibility": "simplified"}]},
    {"featureType": "administrative.neighborhood","stylers": [{"visibility": "off"}]},
];
var mapOptions = {
    zoom: 13,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    styles: mapStyle
};
var map = new google.maps.Map(document.getElementById("map-canvas"),
    mapOptions);

var routeLine = null;

function render(stops) {

    var nodeList = [];
    for (var j = 0; j < stops.length; j++) {
        point = new window.google.maps.LatLng(stops[j][0], stops[j][1]);
        nodeList.push(point);
    }

    routeLine = new google.maps.Polyline({
        path: nodeList,
        strokeColor: "#ff620c",
        strokeWeight: 7,
        strokeOpacity: .75 
    });

    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < nodeList.length; i++) {
        bounds.extend(nodeList[i]);
    }

    routeLine.setMap(map);
    map.fitBounds(bounds);

}


function clearRoute() {
    routeLine.setMap(null);
}
