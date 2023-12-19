
import os
import csv
import datetime
import geopandas as gpd
import pandas as pd
import rasterio
from PIL import Image
from datetime import datetime

# Functions from metadata_project.py
def get_project_metadata():
    # Prompting for project metadata
    project_metadata = {
        'PROJECT_TITLE': input("Enter the PROJECT_TITLE: "),
        'PROJECT_DESCRIPTION': input("Enter the PROJECT_DESCRIPTION: "),
        'PROJECT_SUBJECT': input("Enter the PROJECT_SUBJECT: "),
        'PROJECT_COVERAGE': input("Enter the PROJECT_COVERAGE: "),
        'PROJECT_PCS': input("Enter the PROJECT_PCS: "),  # Projected Coordinate System
        'PROJECT_GCS': input("Enter the PROJECT_GCS: ")   # Geographic Coordinate System
    }
    return project_metadata

def create_file_tree(start_dir):
    # Prepare the header for the CSV
    headers = ['TREE_FOLDERNAME', 'TREE_SIZEMB', 'TREE_FILECOUNT']

    # Function to get folder size and file count
    def get_folder_details(folder_path):
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(folder_path, topdown=True):
            # Skip folders that end with '.files' and '.zip' files
            dirs[:] = [d for d in dirs if not d.endswith('.files')]
            for file in files:
                if not file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        return total_size / (1024 * 1024), file_count  # Convert size to MB

    # List to store folder tree data
    folder_tree_data = []

    # Traversing the directory
    for root, dirs, files in os.walk(start_dir, topdown=True):
        size_mb, file_count = get_folder_details(root)
        folder_tree_data.append([root, size_mb, file_count])

    # Returning the data
    return folder_tree_data, headers

    pass

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
            # Metadata fields extracted from the shapefile
        }
    except Exception as e:
        # Error handling
        return None

def search_image_files(directory):
    # Supported image file extensions
    image_extensions = ['.tiff', '.tif', '.png', '.jpg']
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                yield os.path.join(root, file)

# Function to extract metadata from an image file
def extract_image_metadata(image_path):
    file_size_bytes = os.path.getsize(image_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
    file_name, file_extension = os.path.splitext(os.path.basename(image_path))

    with Image.open(image_path) as img:
        # Determine bit depth based on image mode
        if img.mode == 'RGB':
            bit_depth = 24  # 8 bits per channel
        elif img.mode == 'L':
            bit_depth = 8   # 8 bits for grayscale
        else:
            bit_depth = None  # Undefined or varies for other modes

        return {
            # Metadata fields extracted from the image
        }
    
def search_geotiff_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                yield os.path.join(root, file)

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


def search_other_files(start_dir):
    # Supported file extensions
    file_extensions = ['.txt', '.pdf', '.csv', '.xml', '.dwg', '.dxf']

    # Function to recursively search for files
    def search_files(directory, extensions):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    yield os.path.join(root, file), file

    # Function to extract metadata from a file
    def extract_file_metadata(file_path, file_name):
        # Extract the file extension and format
        file_extension = os.path.splitext(file_name)[1]
        file_format = file_extension.strip('.').upper()

        # Get file creation and modification times
        file_stats = os.stat(file_path)
        created = datetime.datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        updated = datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

        # Return the extracted metadata
        return {
            # Metadata fields extracted from the file
        }

# Main function to orchestrate the metadata extraction and XML file creation
import xml.etree.ElementTree as ET

def main(): 
    # Get project metadata
    project_metadata = get_project_metadata()

    # Initialize a list to collect all metadata
    all_metadata = []

    # Prompt the user for the directory path
    directory = input("Enter the path to the directory: ")

    # Gather folder tree metadata
    folder_tree_data, _ = create_file_tree(directory)
    all_metadata.extend(folder_tree_data)

    # Search and extract metadata from image files
    image_files = list(search_image_files(directory))
    if image_files:
        for image_file in image_files:
            image_metadata = extract_image_metadata(image_file)
            if image_metadata:
                all_metadata.append(image_metadata)

    # Search and extract metadata from GeoTIFF files
    geotiff_files = list(search_geotiff_files(directory))
    if geotiff_files:
        for geotiff_file in geotiff_files:
            geotiff_metadata = extract_geotiff_metadata(geotiff_file)
            if geotiff_metadata:
                all_metadata.append(geotiff_metadata)

    # Search and extract metadata from other file types
    other_files = list(search_other_files(directory))
    if other_files:
        for other_file, _ in other_files:
            file_metadata = extract_file_metadata(other_file)
            if file_metadata:
                all_metadata.append(file_metadata)

    # Create XML file
    root = ET.Element("Metadata")
    for item in all_metadata:
        if item:  # Check if item is not None
            entry = ET.SubElement(root, "Item")
            for key, value in item.items():
                ET.SubElement(entry, key).text = str(value)

    # Add project metadata
    project = ET.SubElement(root, "Project")
    for key, value in project_metadata.items():
        ET.SubElement(project, key).text = value

    tree = ET.ElementTree(root)
    tree.write("output_metadata.xml")

if __name__ == "__main__":
    main()

