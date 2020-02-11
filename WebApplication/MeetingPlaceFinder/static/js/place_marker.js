mapboxgl.accessToken = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg';

var location_list = JSON.parse($("#location_list").text());
var location_geocodes = JSON.parse($("#location_geocodes").text());
var feature_list = [];
for(var i = 0; i < location_geocodes.length - 1; i++){
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
var i = location_geocodes.length - 1;
feature_list.push({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [location_geocodes[i][1], location_geocodes[i][0]]
        },
        properties: {
            title: location_list[i],
        }
    });
//
var geojson = {
type: 'FeatureCollection',
features : feature_list
};

var map = new mapboxgl.Map({
  container: "map", // container id
  style: "mapbox://styles/mapbox/streets-v10", // stylesheet location
  center: [location_geocodes[location_geocodes.length - 1][1], location_geocodes[location_geocodes.length - 1][0]],
  zoom: 12
});

markers = []
geojson.features.forEach(function(marker, idx, array) {
    var color;
    if (idx === array.length - 1){
       color = "#00FF17";
    }
    else{
       color = "#1700FF";
    }
    markers.push(new mapboxgl.Marker({"color": color})
    .setLngLat(marker.geometry.coordinates)
     .setPopup(new mapboxgl.Popup({ offset: 25 })
        .setHTML('<p>' + marker.properties.title + '</p>'))
     .addTo(map));
});

//$(document).ready(function(){
//    map.fitBounds(location_geocodes)
//})

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


