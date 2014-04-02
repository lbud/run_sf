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



function render(stops) {

    var rendererOptions = {
        map: map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: "#ff620c",
            strokeWeight: 7,
            strokeOpacity: .75
        }
    };
    directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);

    directionsService = new google.maps.DirectionsService();

    var batches = [];
    var itemsPerBatch = 10; // google API max - 1 start, 1 stop, and 8 waypoints
    var itemsCounter = 0;
    var wayptsExist = stops.length > 0;
     
    while (wayptsExist) {
        var subBatch = [];
        var subitemsCounter = 0;
     
        for (var j = itemsCounter; j < stops.length; j++) {
            subitemsCounter++;
            subBatch.push({
                location: new window.google.maps.LatLng(stops[j][0], stops[j][1]),
                stopover: false
            });
            if (subitemsCounter == itemsPerBatch)
                break;
        }
     
        itemsCounter += subitemsCounter;
        batches.push(subBatch);
        wayptsExist = itemsCounter < stops.length;
        // If it runs again there are still points. Minus 1 before continuing to 
        // start up with end of previous tour leg
        itemsCounter--;
    }


    // function calcRoute(batches, directionsService, directionsDisplay) { 
    var combinedResults;
    var unsortedResults = [{}]; // to hold the counter and the results themselves as they come back, to later sort
    var directionsResultsReturned = 0;
     
    for (var k = 0; k < batches.length; k++) {
        var lastIndex = batches[k].length - 1;
        var start = batches[k][0].location;
        var end = batches[k][lastIndex].location;
         
        // trim first and last entry from array
        var waypts = [];
        waypts = batches[k];
        waypts.splice(0, 1);
        waypts.splice(waypts.length - 1, 1);
         
        var request = {
            origin : start,
            destination : end,
            waypoints : waypts,
            travelMode : window.google.maps.TravelMode.WALKING
        };
        (function (kk) {
            directionsService.route(request, function (result, status) {
                if (status == window.google.maps.DirectionsStatus.OK) {
                     
                    var unsortedResult = {
                        order : kk,
                        result : result
                    };
                    unsortedResults.push(unsortedResult);
                     
                    directionsResultsReturned++;

                    if (directionsResultsReturned == batches.length || directionsResultsReturned == 10) // we've received all the results. put to map
                    {
                        // sort the returned values into their correct order
                        unsortedResults.sort(function (a, b) {
                            return parseFloat(a.order) - parseFloat(b.order);
                        });
                        var count = 0;
                        for (var key in unsortedResults) {
                            if (unsortedResults[key].result != null) {
                                if (unsortedResults.hasOwnProperty(key)) {
                                    if (count == 0) // first results. new up the combinedResults object
                                        combinedResults = unsortedResults[key].result;
                                    else {
                                        // only building up legs, overview_path, and bounds in my consolidated object. This is not a complete
                                        // directionResults object, but enough to draw a path on the map, which is all I need
                                        combinedResults.routes[0].legs = combinedResults.routes[0].legs.concat(unsortedResults[key].result.routes[0].legs);
                                        combinedResults.routes[0].overview_path = combinedResults.routes[0].overview_path.concat(unsortedResults[key].result.routes[0].overview_path);
                                         
                                        combinedResults.routes[0].bounds = combinedResults.routes[0].bounds.extend(unsortedResults[key].result.routes[0].bounds.getNorthEast());
                                        combinedResults.routes[0].bounds = combinedResults.routes[0].bounds.extend(unsortedResults[key].result.routes[0].bounds.getSouthWest());
                                    }
                                    count++;
                                }
                            }
                        }
                        directionsDisplay.setDirections(combinedResults);
                    }
                }
            });
        })(k);
    }
};
