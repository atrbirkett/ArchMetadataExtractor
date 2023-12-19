import geopandas as gpd
import pandas as pd
import os
from datetime import datetime

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

        # Extract file name without extension and file extension
        file_name_without_extension, file_extension = os.path.splitext(os.path.basename(shp_path))

        # Return the extracted metadata
        return {
            'FILE_NAME': file_name_without_extension,
            'FILE_PATH': os.path.dirname(shp_path),
            'FILE_EXTENSION': file_extension,
            'FILE_SCALE': '',  # Placeholder for manual entry
            'FILE_METHOD': '',  # Placeholder for manual entry
            'FILE_DATES': file_creation_date,
            'FILE_PROJECTID': '',  # Placeholder for manual entry
            'FILE_COVERAGE': '',  # Placeholder for manual entry
            'FILE_PCS': pcs,
            'FILE_GCS': gcs,
        }
    except Exception as e:
        print(f"Error reading {shp_path}: {e}")
        return None

# Prompt for the directory containing the shapefiles
shp_dir = input("Please enter the directory to search for shapefiles: ")

# List of dictionaries to keep all metadata records
metadata_records = []

# Recursively walk through the directory and its subdirectories
for root, dirs, files in os.walk(shp_dir):
    for filename in files:
        if filename.endswith('.shp'):
            # Full path to the shapefile
            shp_path = os.path.join(root, filename)

            # Extract metadata from the shapefile
            metadata = extract_shp_metadata(shp_path)
            if metadata:
                # Add filename to the metadata
                metadata['FILENAME'] = filename
                # Add the metadata to the list of records
                metadata_records.append(metadata)

# Convert the list of dictionaries to a DataFrame
metadata_df = pd.DataFrame(metadata_records)

# Path to the output CSV file
csv_output_path = os.path.join(shp_dir, 'METADATA_Shapefiles.csv')

# Write the DataFrame to a CSV file
metadata_df.to_csv(csv_output_path, index=False)

print(f"The metadata CSV file has been created at: {csv_output_path}")
