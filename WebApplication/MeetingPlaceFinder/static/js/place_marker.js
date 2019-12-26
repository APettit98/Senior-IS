mapboxgl.accessToken = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg';

var location_list = JSON.parse($("#location_list").text());
var location_geocodes = JSON.parse($("#location_geocodes").text());
console.log(location_geocodes)
var feature_list = [];
for(var i = 0; i < location_geocodes.length; i++){
    feature_list.push({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [location_geocodes[i][1], location_geocodes[i][0]]
        },
        properties: {
            title: location_list[i]
        }
    });
}
//
var geojson = {
type: 'FeatureCollection',
features : feature_list
};

var map = new mapboxgl.Map({
  container: "map", // container id
  style: "mapbox://styles/mapbox/streets-v10", // stylesheet location
  center: [location_geocodes[0][1], location_geocodes[0][0]], // starting position [lng, lat]
  zoom: 8 // starting zoom
});

markers = []
geojson.features.forEach(function(marker) {
    markers.push(new mapboxgl.Marker()
     .setLngLat(marker.geometry.coordinates)
     .addTo(map));
});

//for(i = 0; i < location_list.length; i++){
//    var mapboxClient = mapboxSdk({ accessToken: mapboxgl.privateToken });
//    var geocode = mapboxClient.geocoding.forwardGeocode({
//        query: location_list[i],
//        autocomplete: false,
//        limit: 1
//        });
//        console.log(geocode);
//    }).send().then(function (response) {
//        if (response && response.body && response.body.features && response.body.features.length) {
//        var feature = response.body.features[0];
//
//        new mapboxgl.Marker()
//            .setLngLat(feature.center)
//            .addTo(map);
//        }
//    });
//}


