mapboxgl.accessToken = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazNscmN1czcwOHRsM29sanhzcm95ZmlxIn0.pRSXcRGiHLQfxj4AH1_lGg';

// Parse list of (lat, long) coordinates and create points with
// those coordinates
var location_list = JSON.parse($("#location_list").text());
var location_geocodes = JSON.parse($("#location_geocodes").text());
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

// Create geojson object
var geojson = {
type: 'FeatureCollection',
features : feature_list
};

// Create a mapbox map
var map = new mapboxgl.Map({
  container: "map", // container id
  style: "mapbox://styles/mapbox/streets-v10", // stylesheet location
  center: [location_geocodes[location_geocodes.length - 1][1], location_geocodes[location_geocodes.length - 1][0]],
  zoom: 8
});

// Create markers, making the meeting point a different color than the others
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
