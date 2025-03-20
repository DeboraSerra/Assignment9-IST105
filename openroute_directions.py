import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("API_KEY")
directions_api = "https://api.openrouteservice.org/v2/directions/driving-car"
geocode_api = "https://api.openrouteservice.org/geocode/search?"

try:
    origin = sys.argv[1]
    destination = sys.argv[2]
except IndexError:
    origin = input("Enter the origin address: ")
    destination = input("Enter the destination address: ")

paragraph = "<p>{text}</p>"
title = "<h1>{text}</h1>"
error = "<h2>{text}</h2>"
line = "<hr>"

if origin == destination:
    print(error.format(text="Error: Origin and destination addresses are the same."))
    sys.exit(1)

# origin and destination should contain only alphanumeric characters and spaces
if not origin.replace(" ", "").isalnum() or not destination.replace(" ", "").isalnum():
    print(
        error.format(
            text="Error: Origin and destination addresses should contain only alphanumeric characters and spaces."
        )
    )
    sys.exit(1)

print(title.format(text="OpenRouteService Directions"))
print(paragraph.format(text="Origin: " + origin))
print(paragraph.format(text="Destination: " + destination))


def geocode_address(address):
    url = f"{geocode_api}api_key={api_key}&text={address}"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()

        if json_data["features"]:
            coords = json_data["features"][0]["geometry"]["coordinates"]
            print(
                paragraph.format(text=f"Geocoded coordinates for '{address}': {coords}")
            )  # Debugging
            if -90 <= coords[1] <= 90 and -180 <= coords[0] <= 180:
                return coords
            else:
                print(
                    error.format(
                        text=f"Error: Invalid coordinates for address '{address}'"
                    )
                )
                return None
        else:
            print(error.format(text=f"Error: No results found for address '{address}'"))
            return None
    else:
        print(error.format(text=f"Error: {response.status_code} - {response.text}"))
        return None


orig_coords = geocode_address(origin)
dest_coords = geocode_address(destination)

if not orig_coords or not dest_coords:
    print(
        error.format(
            text="Unable to geocode one or both addresses. Please try again.\n"
        )
    )

# Construct the JSON body for the POST request
body = {"coordinates": [orig_coords, dest_coords]}

# Make the POST request
headers = {"Authorization": api_key, "Content-Type": "application/json"}
response = requests.post(directions_api, headers=headers, json=body)
json_data = response.json()
# print(json_data)


if response.status_code == 200:
    if "routes" in json_data and json_data["routes"]:
        route = json_data["routes"][0]

        if "segments" in route and route["segments"]:
            segment = route["segments"][0]
            print(line)
            print(f"Directions from {origin} to {destination}")

            # Extract trip duration and distance
            duration = segment.get("duration", "N/A")
            distance = segment.get("distance", "N/A")
            print(paragraph.format(text=f"Duration: {duration} seconds"))
            print(paragraph.format(text=f"Distance: {distance} meters"))
            print(line)

            # Extract and print step-by-step directions
            if "steps" in segment:
                for step in segment["steps"]:
                    instruction = step.get("instruction", "N/A")
                    step_distance = step.get("distance", "N/A")
                    print(
                        paragraph.format(text=f"{instruction} ({step_distance} meters)")
                    )
            else:
                print(error.format(text="No step-by-step directions available."))

        else:
            print(error.format(text="Error: No segments found in the response."))
    else:
        print(error.format(text="Error: No routes found in the response."))
else:
    print(error.format(text=f"Error: {response.status_code} - {response.text}"))
