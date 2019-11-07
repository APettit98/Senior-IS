import osmnx as ox

# Get road network via bounding box
north, south, east, west = 37.79, 37.78, -122.41, -122.43 # San Francisco

G1 = ox.graph_from_bbox(north, south, east, west, network_type="drive")
ox.project_graph(G1)
fix, ax = ox.plot_graph(G1)

# Road network from lat-long point - specified distance includes anything within the box formed by the distance
# define a point at the corner of California St and Mason St in SF
location_point = (37.791427, -122.410018)

# create network from point, inside bounding box of N, S, E, W each 750m from point
G2 = ox.graph_from_point(location_point, distance=750, distance_type='bbox', network_type='drive')
G2 = ox.project_graph(G2)
fig, ax = ox.plot_graph(G2, node_size=30, node_color='#66cc66')

# Distance now specifies network distance - nothing in the network is more than distance meters from any
# other point in the network
# same point again, but create network only of nodes within 500m along the network from point
G3 = ox.graph_from_point(location_point, distance=500, distance_type='network')
fig, ax = ox.plot_graph(G3)


# Road network from address w/ distance
# network from address, including only nodes within 1km along the network from the address
G4 = ox.graph_from_address(address='350 5th Ave, New York, NY',
                              distance=1000, distance_type='network', network_type='drive')

# you can project the network to UTM (zone calculated automatically)
G4_projected = ox.project_graph(G4)
fig, ax = ox.plot_graph(G4_projected)


# Road network from place name
# create the street network within the city of Piedmont's borders
G5 = ox.graph_from_place('Piedmont, California, USA')
G5_projected = ox.project_graph(G5)
fig, ax = ox.plot_graph(G5_projected)
