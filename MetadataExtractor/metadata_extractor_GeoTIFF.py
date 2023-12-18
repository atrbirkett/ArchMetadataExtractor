import os
import csv
import rasterio
from datetime import datetime

def search_geotiff_files(start_dir):
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
                if src.crs:
                    return {
                        'FILE_COVERAGE': str(src.bounds),
                        'FILE_PCS': src.crs.to_string() if src.crs else 'Unknown',
                        'FILE_GCS': src.crs.to_epsg() if src.crs else 'Unknown',
                    }
                else:
                    return None
        except rasterio.errors.RasterioIOError:
            return None

    # List to keep all metadata records
    metadata_records = []

    for geotiff_path in search_geotiff_files(start_dir):
        metadata = extract_geotiff_metadata(geotiff_path)
        if metadata:
            metadata_records.append(metadata)

    if not metadata_records:
        print("No georeferenced TIFF files found.")
    else:
        headers = ['FILE_COVERAGE', 'FILE_PCS', 'FILE_GCS']
        rows = [[record[header] for header in headers] for record in metadata_records]

        csv_output_path = os.path.join(start_dir, 'METADATA_GeoTIFF.csv')

        with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            csvwriter.writerows(rows)

        print(f"The GeoTIFF metadata CSV file has been created at: {csv_output_path}")

if __name__ == "__main__":
    start_dir = input("Please enter the directory to search for GeoTIFF files: ")
    search_geotiff_files(start_dir)
