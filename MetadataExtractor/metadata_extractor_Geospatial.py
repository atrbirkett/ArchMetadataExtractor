import geopandas as gpd
import pandas as pd
import os
from datetime import datetime

def search_geospatial_files(start_dir):
    # Function to recursively search for .shp files
    def search_shp_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.shp'):
                    yield os.path.join(root, file)

    # Function to extract metadata from a shapefile
    def extract_shp_metadata(shp_path):
        try:
            # Read the shapefile
            gdf = gpd.read_file(shp_path)

            # Get the file creation date
            file_creation_date = datetime.fromtimestamp(os.path.getctime(shp_path)).strftime('%Y-%m-%d')

            # Extracting CRS details
            pcs = gdf.crs.to_string() if gdf.crs else 'Unknown'
            gcs = gdf.crs.geodetic_crs.to_string() if gdf.crs and gdf.crs.geodetic_crs else 'Unknown'

            # Return the extracted metadata
            return {
                'FILE_NAME': os.path.basename(shp_path),
                'FILE_PATH': shp_path,
                'FILE_EXTENSION': '.shp',
                'FILE_SCALE': '',  # Placeholder for manual entry
                'FILE_METHOD': '',  # Placeholder for manual entry
                'FILE_DATES': file_creation_date,
                'FILE_COVERAGE': '',  # Placeholder for manual entry
                'FILE_PCS': pcs,
                'FILE_GCS': gcs,
            }
        except Exception as e:
            print(f"Error reading {shp_path}: {e}")
            return None

    # List of dictionaries to keep all metadata records
    metadata_records = []

    # Search for all .shp files within the directory and subdirectories
    for shp_path in search_shp_files(start_dir):
        metadata = extract_shp_metadata(shp_path)
        if metadata:
            metadata_records.append(metadata)

    # Headers for the CSV file
    headers = ['FILE_NAME', 'FILE_PATH', 'FILE_EXTENSION', 'FILE_SCALE', 'FILE_METHOD', 'FILE_DATES',
               'FILE_COVERAGE', 'FILE_PCS', 'FILE_GCS']

    # Convert the list of dictionaries to a list of rows including headers
    rows = [[record[header] for header in headers] for record in metadata_records]

    # Path to the output CSV file
    csv_output_path = os.path.join(start_dir, 'METADATA_Shapefiles.csv')

    # Write the rows to a CSV file
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)

    print(f"The metadata CSV file for shapefiles has been created at: {csv_output_path}")

if __name__ == "__main__":
    # Prompt for the directory to search for shapefiles
    start_dir = input("Please enter the directory to search for shapefiles: ")
    search_geospatial_files(start_dir)
