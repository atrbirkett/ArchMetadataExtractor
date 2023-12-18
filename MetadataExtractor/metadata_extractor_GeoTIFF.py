import os
import csv
import rasterio
from datetime import datetime

# Prompt for directory to search for GeoTIFF files
start_dir = input("Please enter the directory to search for GeoTIFF files: ")

# Function to recursively search for GeoTIFF files
def search_geotiff_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                yield os.path.join(root, file)

# Function to extract metadata from a GeoTIFF file
def extract_geotiff_metadata(geotiff_path):
    try:
        with rasterio.open(geotiff_path) as src:
            # Check if the GeoTIFF file is georeferenced
            if src.crs:
                # Extract geospatial metadata
                return {
                    'FILE_COVERAGE': str(src.bounds),  # This will give the bounding box. You can format it as needed.
                    'FILE_PCS': src.crs.to_string() if src.crs else 'Unknown',
                    'FILE_GCS': src.crs.to_epsg() if src.crs else 'Unknown',  # Assumes EPSG code is sufficient for GCS
                }
            else:
                # File is not georeferenced, return None
                return None
    except rasterio.errors.RasterioIOError:
        # Handle files that are not valid raster files
        return None

# List to keep all metadata records
metadata_records = []

# Search for all GeoTIFF files within the directory and subdirectories
for geotiff_path in search_geotiff_files(start_dir):
    # Extract metadata from the GeoTIFF file
    metadata = extract_geotiff_metadata(geotiff_path)
    if metadata:
        metadata_records.append(metadata)

# Check if there are any georeferenced records before proceeding
if not metadata_records:
    print("No georeferenced TIFF files found.")
else:
    # Convert the list of dictionaries to a list of rows including headers
    headers = ['FILE_COVERAGE', 'FILE_PCS', 'FILE_GCS']
    rows = [[record[header] for header in headers] for record in metadata_records]

    # Path to the output CSV file
    csv_output_path = os.path.join(start_dir, f'geotiff_metadata_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv')

    # Write the rows to a CSV file
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)

    print(f"The GeoTIFF metadata CSV file has been created at: {csv_output_path}")
