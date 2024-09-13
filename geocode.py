import requests
import folium
from folium.plugins import MarkerCluster
from IPython.display import IFrame

def generate_map(postal_code, api_key):
    # URL for the Geocoding API
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # Parameters to be sent in the GET request
    geocode_params = {
        'address': postal_code,  # The postal code you're querying
        'key': api_key  # Your API key
    }

    # Make the GET request
    response = requests.get(url, params=geocode_params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extracting latitude and longitude
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']

        print(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        print(f"Error: {response.status_code}")
        return None

    # Function to search for places based on type or name
    def search_places(lat, lng, radius, search_type=None, search_name=None):
        nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            'location': f'{lat},{lng}',  # Latitude and Longitude
            'radius': radius,  # Radius in meters
            'key': api_key  # Your API key
        }
        
        # Add search parameters based on type or name
        if search_type:
            places_params['type'] = search_type
        if search_name:
            places_params['keyword'] = search_name

        # Make the GET request to Google Places API
        response = requests.get(nearby_url, params=places_params)
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            print(f"Error: {response.status_code}")
            return []

    # Create a map centered on the queried location
    map = folium.Map(location=[latitude, longitude], zoom_start=13)

    # Create a marker cluster for supermarkets and stores
    marker_cluster = MarkerCluster().add_to(map)

    # Add a triangle marker (using DivIcon) for the input postal code
    folium.map.Marker(
        [latitude, longitude],
        icon=folium.DivIcon(
            html=f"""
            <div style="position: relative;">
                <div style="position: absolute; width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 20px solid green;"></div>
            </div>"""
        ),
        popup="Input Postal Code"
    ).add_to(map)

    # List to store the coordinates for adjusting the zoom level
    locations = [[latitude, longitude]]  # Add the initial postal code location

    # Set to track already added places by their latitude and longitude
    added_places = set()

    # Function to add a place to the map if it hasn't been added already
    def add_place_to_map(lat, lng, name, address, color, popup, added_places):
        location_key = (lat, lng)  # Create a unique key based on lat/lng
        if location_key not in added_places:
            folium.Marker(
                [lat, lng],
                popup=f"{popup}\n{name}\n{address}",
                icon=folium.Icon(color=color)
            ).add_to(marker_cluster)
            locations.append([lat, lng])  # Add to the location list for zoom fitting
            added_places.add(location_key)  # Mark this place as added

    # Search for major supermarket chains within 5 km radius
    major_supermarkets = ['Lidl', 'Jumbo', 'Aldi', 'Albert Heijn', 'Dirk', 'Spar']
    for supermarket in major_supermarkets:
        results = search_places(latitude, longitude, radius=5000, search_name=supermarket)
        for result in results:
            name = result['name']
            address = result.get('vicinity', 'No address provided')
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']

            # Add orange markers for major supermarkets, ensuring no duplicates
            add_place_to_map(lat, lng, name, address, "orange", "Supermarket", added_places)

    # Search for small stores like Toko, Asian, Turkish supermarkets within 5 km radius
    small_store_keywords = ['Toko', 'Asian supermarket', 'Turkish supermarket', 'Die Grenze']
    for keyword in small_store_keywords:
        results = search_places(latitude, longitude, radius=5000, search_name=keyword)
        for result in results:
            name = result['name']
            address = result.get('vicinity', 'No address provided')
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']

            # Add blue markers for small stores, ensuring no duplicates
            add_place_to_map(lat, lng, name, address, "blue", "Small Store", added_places)

    # Search for market areas within 3 km radius
    market_area_keywords = ['market', 'open-air market', 'bazaar']
    for keyword in market_area_keywords:
        results = search_places(latitude, longitude, radius=3000, search_name=keyword)
        for result in results:
            name = result['name']
            address = result.get('vicinity', 'No address provided')
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']

            # Add red markers for market areas, ensuring no duplicates
            add_place_to_map(lat, lng, name, address, "red", "Market Area", added_places)

    # Auto-adjust the map to cover all markers (postal code and stores)
    map.fit_bounds(locations)

    # Save the map as an HTML file in-memory
    map_html = "supermarkets_map.html"
    map.save(map_html)