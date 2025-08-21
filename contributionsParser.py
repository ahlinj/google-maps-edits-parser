import os
import json
import tkinter as tk
from tkinter import filedialog
from xml.etree.ElementTree import Element, SubElement, ElementTree
import re
import requests
import reverse_geocoder as rg
from collections import Counter

def extract_coordinates(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw = file.read()
            fixed_raw = fix_multiline_text_fields(raw)
            data = json.loads(fixed_raw)

        if "instructions" in data:
            for instruction in data["instructions"]:
                if "roadNetworkUpdate" in instruction:
                    rnu = instruction["roadNetworkUpdate"]
                    
                    before_segments = rnu.get("before", {}).get("segments", [])
                    after_segments = rnu.get("after", {}).get("segments", [])
                    
                    def get_first_vertex_coords(segments):
                        if segments and "polyline" in segments[0] and "vertices" in segments[0]["polyline"]:
                            first_vertex = segments[0]["polyline"]["vertices"][0]
                            lat = first_vertex["latE7"] / 1e7
                            lng = first_vertex["lngE7"] / 1e7
                            return lat, lng
                        return None
                    
                    coords = get_first_vertex_coords(before_segments)
                    if coords is None:
                        coords = get_first_vertex_coords(after_segments)
                    
                    if coords is not None:
                        return coords
                    
                if "userComments" in instruction:
                    for comment in instruction["userComments"]:
                        if "text" in comment:
                            coord_pattern = r'-?[0-9]+\.[0-9]+, -?[0-9]+\.[0-9]+'
                            text = comment["text"]
                            coord_match = re.search(coord_pattern, text)
                            if coord_match:
                                coordinates = coord_match.group(0)
                                lat = coordinates.split(",")[0]
                                lng = coordinates.split(",")[1].strip()
                                return lat, lng
                            link_pattern = r'https:\/\/maps.app.goo.gl\/[^\s]+'
                            link_match = re.search(link_pattern, text)
                            if link_match:
                                response = requests.get(link_match.group(0), allow_redirects=True)
                                coord_from_link = re.search(coord_pattern, response.url)
                                if coord_from_link:
                                    lat = coord_from_link.group(0).split(",")[0]
                                    lng = coord_from_link.group(0).split(",")[0].strip()
                                    return lat, lng
                
                if "location" in instruction and "points" in instruction["location"]:
                    first_point = instruction["location"]["points"][0]
                    lat = first_point["latE7"] / 1e7
                    lng = first_point["lngE7"] / 1e7
                    return lat, lng

        raise ValueError("Unrecognized JSON format")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None
    
def fix_multiline_text_fields(raw: str) -> str:
    pattern = r'"text"\s*:\s*"((?:[^"\\]|\\.|\\\n)*?)"'

    def replacer(match):
        original_text = match.group(1)
        fixed_text = original_text.replace('\n', ' ').replace('\r', '').strip()
        return f'"text": "{fixed_text}"'
    
    return re.sub(pattern, replacer, raw, flags=re.DOTALL)


def create_kml(coordinates, kml_file_path):
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = SubElement(kml, 'Document')
    
    for lat, lng in coordinates:
        placemark = SubElement(document, 'Placemark')
        point = SubElement(placemark, 'Point')
        coordinates_tag = SubElement(point, 'coordinates')
        coordinates_tag.text = f"{lng},{lat},0"
    
    tree = ElementTree(kml)
    tree.write(kml_file_path, encoding="utf-8", xml_declaration=True)
    
    
def split_kml_file(coordinates, output_folder, max_coordinates=2000):
    chunk = set()
    file_index = 1

    for coord in coordinates:
        chunk.add(coord)
        if len(chunk) == max_coordinates:
            output_filename = os.path.join(output_folder, f"coordinates_chunk_{file_index}.kml")
            create_kml(chunk, output_filename)
            file_index += 1
            chunk = set()

    # Write remaining coordinates
    if chunk:
        output_filename = os.path.join(output_folder, f"coordinates_chunk_{file_index}.kml")
        create_kml(chunk, output_filename)

def extract_countries(coordinates, folder_selected):
    coordinates_list = list(coordinates)
    results = rg.search(coordinates_list)
    
    country_codes = [result['cc'] for result in results]
    country_counts = Counter(country_codes)
    
    output_filename = os.path.join(folder_selected,"stats.txt")
    try:
        with open(output_filename, 'w') as f:
            for country, count in country_counts.most_common():
                f.write(f"{country}: {count}\n")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def main():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Folder Containing JSON Files")

    if not folder_selected:
        print("No folder selected. Exiting...")
        return

    print(f"Processing JSON files in: {folder_selected}")

    coordinates = set()

    # Loop through JSON files in the selected directory
    for filename in os.listdir(folder_selected):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_selected, filename)
            result = extract_coordinates(file_path)
            if result is not None and result not in coordinates:
                coordinates.add(result)
                
    print(f"Total coordinates extracted: {len(coordinates)}")

    extract_countries(coordinates, folder_selected)
    
    if coordinates:
        kml_file_path = os.path.join(folder_selected, "coordinates.kml")
        create_kml(coordinates, kml_file_path)
        
    if len(coordinates) > 2000:
        split_kml_file(coordinates, folder_selected)
    
    print("Processing complete!")

if __name__ == "__main__":
    main()
