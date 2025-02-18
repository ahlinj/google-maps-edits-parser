import os
import json
import tkinter as tk
from tkinter import filedialog
from xml.etree.ElementTree import Element, SubElement, ElementTree

def extract_coordinates(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if "instructions" in data:
            for instruction in data["instructions"]:
                if "roadNetworkUpdate" in instruction and "before" in instruction["roadNetworkUpdate"]:
                    segments = instruction["roadNetworkUpdate"]["before"].get("segments", [])
                    if segments and "polyline" in segments[0] and "vertices" in segments[0]["polyline"]:
                        first_vertex = segments[0]["polyline"]["vertices"][0]
                        lat = first_vertex["latE7"] / 1e7
                        lng = first_vertex["lngE7"] / 1e7
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
    
    
def split_kml_file(coordinates, input_kml_path, total_coordinates, output_folder, max_coordinates=2000):
    # Calculate the number of chunks needed
    num_chunks = (total_coordinates + max_coordinates - 1) // max_coordinates

    output_files = []

    for i in range(num_chunks):
        chunk_coordinates = coordinates[i * max_coordinates: (i + 1) * max_coordinates]
        output_filename = os.path.join(output_folder, f"coordinates_chunk_{i + 1}.kml")
        create_kml(chunk_coordinates, output_filename)
        output_files.append(output_filename)
    return output_files

def main():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Folder Containing JSON Files")

    if not folder_selected:
        print("No folder selected. Exiting...")
        return

    print(f"Processing JSON files in: {folder_selected}")

    coordinates = []

    # Loop through JSON files in the selected directory
    for filename in os.listdir(folder_selected):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_selected, filename)
            result = extract_coordinates(file_path)
            if result:
                coordinates.append(result)
                
    print(f"Total coordinates extracted: {len(coordinates)}")

    if coordinates:
        kml_file_path = os.path.join(folder_selected, "coordinates.kml")
        create_kml(coordinates, kml_file_path)
        
    if len(coordinates) > 2000:
        split_kml_file(coordinates, kml_file_path, len(coordinates), folder_selected)
    
    print("Processing complete!")

if __name__ == "__main__":
    main()
