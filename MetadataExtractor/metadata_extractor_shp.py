import geopandas as gpd
import pandas as pd
import os
from datetime import datetime

# Prompt for Project ID
project_id = input("Please enter the Project ID: ")

# Function to extract metadata from a shapefile
def extract_shp_metadata(shp_path, project_id):
    try:
        # Read the shapefile
        gdf = gpd.read_file(shp_path)

        # Get the file creation date from the file metadata (this may not be reliable for actual data creation date)
        file_creation_date = datetime.fromtimestamp(os.path.getctime(shp_path)).strftime('%Y-%m-%d')

        # Extracting CRS details
        pcs = gdf.crs.to_string() if gdf.crs else 'Unknown'
        gcs = gdf.crs.geodetic_crs.to_string() if gdf.crs and gdf.crs.geodetic_crs else 'Unknown'

        # Return the extracted metadata
        return {
            'FILE_SCALE': '',  # Placeholder for manual entry
            'FILE_METHOD': '',  # Placeholder for manual entry
            'FILE_DATES': file_creation_date,
            'FILE_PROJECTID': project_id,  # Use the provided Project ID
            'FILE_COVERAGE': '',  # Placeholder for manual entry
            'FILE_PCS': pcs,
            'FILE_GCS': gcs,
        }
    except Exception as e:
        # If there's an error reading the shapefile, return None
        print(f"Error reading {shp_path}: {e}")
        return None

# Function to recursively search for .shp files
def search_shp_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.shp'):
                yield os.path.join(root, file)

# Directory to start the search for shapefiles
start_dir = input("Please enter the directory to search for shapefiles: ")

# List of dictionaries to keep all metadata records
metadata_records = []

# Search for all .shp files within the directory and subdirectories
for shp_path in search_shp_files(start_dir):
    # Extract metadata from the shapefile
    metadata = extract_shp_metadata(shp_path, project_id)
    if metadata:
        # Add filename to the metadata
        metadata['FILENAME'] = os.path.basename(shp_path)
        # Add the full path to the metadata for reference
        metadata['FILEPATH'] = shp_path
        # Add the metadata to the list of records
        metadata_records.append(metadata)

# Convert the list of dictionaries to a DataFrame
metadata_df = pd.DataFrame(metadata_records)

# Path to the output CSV file
csv_output_path = os.path.join(start_dir, 'shapefile_metadata.csv')

# Write the DataFrame to a CSV file
metadata_df.to_csv(csv_output_path, index=False)

print(f"The metadata CSV file has been created at: {csv_output_path}")
