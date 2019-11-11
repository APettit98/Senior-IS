mapboxgl.accessToken = 'pk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazJwNWk4NjkwMHIyM29tdHZyaHo4dWE5In0.nzxAYUrqDJ3G6lojw62eMQ';
mapboxgl.privateToken = "sk.eyJ1IjoiYXBldHRpdCIsImEiOiJjazJwNWtodXgwMHQwM25ybXo1a3BmY295In0.7oyWAaqB1aJJJp9oGmZPug";

//console.log($("#location_list").text());
var location_list = JSON.parse($("#location_list").text());

var mapboxClient = mapboxSdk({ accessToken: mapboxgl.privateToken });
    mapboxClient.geocoding.forwardGeocode({
    query: location_list[0],
    autocomplete: false,
    limit: 1
}).send().then(function (response) {
    if (response && response.body && response.body.features && response.body.features.length) {
    var feature = response.body.features[0];
    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: feature.center,
        zoom: 10
    });

new mapboxgl.Marker()
    .setLngLat(feature.center)
    .addTo(map);
}
});
