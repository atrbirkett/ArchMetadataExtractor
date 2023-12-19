import geopandas as gpd
import pandas as pd
import os
from datetime import datetime
import xml.etree.ElementTree as ET

def extract_shp_metadata(shp_path):
    try:
        # Read the shapefile
        gdf = gpd.read_file(shp_path)

        # Get geometry type and feature count
        geometry_type = gdf.geometry.geom_type.unique()[0] if len(gdf) > 0 else 'Unknown'
        feature_count = len(gdf)

        # Get the file creation date
        file_creation_date = datetime.fromtimestamp(os.path.getctime(shp_path)).strftime('%Y-%m-%d')

        # Extract CRS details
        pcs = gdf.crs.to_string() if gdf.crs else 'Unknown'
        gcs = gdf.crs.geodetic_crs.to_string() if gdf.crs and gdf.crs.geodetic_crs else 'Unknown'

        # Extract file name without extension and file extension
        file_name_without_extension, file_extension = os.path.splitext(os.path.basename(shp_path))

        file_size_bytes = os.path.getsize(shp_path)
        file_size_mb = file_size_bytes / 1024 / 1024  # Convert bytes to MB

        # Find associated files (.dbf, .shx, .prj, etc.)
        associated_files = [f for f in os.listdir(os.path.dirname(shp_path)) if f.startswith(file_name_without_extension)]

        # Placeholder for data description - may require manual entry or another data source
        data_description = "No Description"

        # Return the extracted metadata
        return {
            'FILE_PROJECTID': '',  # Placeholder for manual entry
            'FILE_NAME': file_name_without_extension,
            'FILE_PATH': os.path.dirname(shp_path),
            'FILE_EXTENSION': file_extension,
            'FILE_SIZE': file_size_mb,  # File size in MB
            'FILE_DESCRIPTION': data_description,
            'FILE_TYPE': geometry_type,
            'FILE_FEATURECOUNT': str(feature_count),
            'FILE_METHOD': '',  # Placeholder for manual entry
            'FILE_DATES': file_creation_date,
            'FILE_COVERAGE': '',  # Placeholder for manual entry
            'FILE_PCS': pcs,
            'FILE_GCS': gcs,
            'FILE_SCALE': '',  # Placeholder for manual entry
            'FILE_RELATED': ', '.join(associated_files),
        }
    except Exception as e:
        print(f"Error reading {shp_path}: {e}")
        return None

def create_xml(metadata_records, output_path):
    root = ET.Element("ShapefilesMetadata")

    for metadata in metadata_records:
        shp_element = ET.SubElement(root, "Shapefile")
        for key, value in metadata.items():
            ET.SubElement(shp_element, key).text = str(value)

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

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

# Path to the output XML file
xml_output_path = os.path.join(shp_dir, 'METADATA_Shapefiles.xml')

# Write the metadata to an XML file
create_xml(metadata_records, xml_output_path)

print(f"The metadata CSV file has been created at: {csv_output_path}")
print(f"The metadata XML file has been created at: {xml_output_path}")
