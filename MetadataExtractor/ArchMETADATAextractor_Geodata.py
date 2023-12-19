import os
import rasterio
import geopandas as gpd
from datetime import datetime
import xml.etree.ElementTree as ET

def search_files(start_dir):
    # Function to recursively search for both .shp and .tif/.tiff files
    shp_files = []
    geotiff_files = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.lower().endswith('.shp'):
                shp_files.append(os.path.join(root, file))
            elif file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                geotiff_files.append(os.path.join(root, file))

    return shp_files, geotiff_files

def extract_metadata(file_path, file_extension):
    try:
        if file_extension.lower() in ['.tif', '.tiff']:
            # For GeoTIFF files
            with rasterio.open(file_path) as src:
                tags = src.tags()
                file_size_bytes = os.path.getsize(file_path)
                file_size_mb = file_size_bytes / 1048576  # Convert bytes to megabytes
                return {
                    'FILE_NAME': os.path.splitext(os.path.basename(file_path))[0],
                    'FILE_LOCATION': os.path.dirname(file_path),
                    'FILE_EXTENSION': os.path.splitext(file_path)[1],
                    'FILE_DESCRIPTION': tags.get('Description', 'Unknown'),
                    'FILE_KEYWORDS': tags.get('Keywords', 'Unknown'),
                    'FILE_VERSION': tags.get('Version', src.driver),
                    'FILE_SIZE_MB': str(file_size_mb),  # Store file size in MB
                    'FILE_BANDS': str(src.count),
                    'FILE_CELLSIZE': str(src.res),
                    'FILE_COVERAGE': str(src.bounds),
                    'FILE_PCS': src.crs.to_string() if src.crs else 'Unknown',
                    'FILE_GCS': src.crs.to_epsg() if src.crs else 'Unknown',
                }
        elif file_extension.lower() == '.shp':
            # For shapefiles
            gdf = gpd.read_file(file_path)
            geometry_type = gdf.geometry.geom_type.unique()[0] if len(gdf) > 0 else 'Unknown'
            feature_count = len(gdf)
            file_creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d')
            pcs = gdf.crs.to_string() if gdf.crs else 'Unknown'
            gcs = gdf.crs.geodetic_crs.to_string() if gdf.crs and gdf.crs.geodetic_crs else 'Unknown'
            file_name_without_extension, _ = os.path.splitext(os.path.basename(file_path))
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / 1024 / 1024  # Convert bytes to MB
            associated_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(file_name_without_extension)]
            data_description = "No Description"

            return {
                'FILE_PROJECTID': '',  # Placeholder for manual entry
                'FILE_NAME': file_name_without_extension,
                'FILE_PATH': os.path.dirname(file_path),
                'FILE_EXTENSION': file_extension,
                'FILE_SIZE_MB': file_size_mb,  # File size in MB
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
        print(f"Error reading {file_path}: {e}")
        return None

def create_xml(metadata_records, output_path, root_element_name):
    root = ET.Element(root_element_name)

    for metadata in metadata_records:
        element = ET.SubElement(root, "Item")
        for key, value in metadata.items():
            ET.SubElement(element, key).text = str(value)

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    start_dir = input("Please enter the directory to search for files: ")

    shp_files, geotiff_files = search_files(start_dir)

    metadata_records = []

    if shp_files:
        metadata_records.extend([extract_metadata(file, '.shp') for file in shp_files])

    if geotiff_files:
        metadata_records.extend([extract_metadata(file, '.tif') for file in geotiff_files])
        metadata_records.extend([extract_metadata(file, '.tiff') for file in geotiff_files])

    # Remove None values from metadata_records
    metadata_records = [metadata for metadata in metadata_records if metadata is not None]

    if metadata_records:
        # Path to the output XML file
        xml_output_path = os.path.join(start_dir, 'METADATA_AllFiles.xml')

        # Write the metadata to an XML file
        create_xml(metadata_records, xml_output_path, "AllFilesMetadata")

        print(f"The metadata XML file has been created at: {xml_output_path}")
    else:
        print("No supported files found in the specified directory.")
