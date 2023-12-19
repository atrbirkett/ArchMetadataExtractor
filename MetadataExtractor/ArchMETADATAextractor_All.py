import os
import rasterio
import geopandas as gpd
from datetime import datetime
import xml.etree.ElementTree as ET

def extract_file_metadata(file_path, file_name, file_size_mb, data_description, geometry_type, feature_count, file_creation_date, pcs, gcs):
    # Extract the file extension and format
    file_extension = os.path.splitext(file_name)[1]
    file_format = file_extension.strip('.').upper()

    # Get file creation and modification times
    file_stats = os.stat(file_path)
    created = datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')  # Use datetime
    updated = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')  # Use datetime

    # Check if it's a .csv file with "_G_" in the file name
    if file_extension.lower() == '.csv' and "_G_" in file_name:
        # Extract the metadata for this special case
        return {
            'FILE_PROJECTID': '',  # Placeholder for manual entry
            'FILE_NAME': os.path.splitext(file_name)[0],  # Remove the file extension
            'FILE_EXTENSION': file_extension,
            'FILE_SIZE_MB': file_size_mb,  # File size in MB
            'FILE_DESCRIPTION': '',  # Placeholder for manual entry
            'FILE_TYPE': '',  # Placeholder for manual entry
            'FILE_FEATURECOUNT': '',  # Placeholder for manual entry
            'FILE_METHOD': '',  # Placeholder for manual entry
            'FILE_DATES': file_creation_date,
            'FILE_COVERAGE': '',  # Placeholder for manual entry
            'FILE_PCS': '',  # Placeholder for manual entry
            'FILE_GCS': '',  # Placeholder for manual entry
            'FILE_SCALE': '',  # Placeholder for manual entry
            'FILE_RELATED': '',  # Placeholder for manual entry
        }

    # For other cases, return the standard metadata
    return {
        'FILE_NAME': os.path.splitext(file_name)[0],  # Remove the file extension
        'FILE_EXTENSION': file_extension,
        'FILE_SIZE_MB': file_size_mb,  # File size in MB
        'FILE_FORMAT': file_format,
        'FILE_SOFTWARE': '',  # Placeholder for manual entry
        'FILE_HARDWARE': '',  # Placeholder for manual entry
        'FILE_OPSYS': '',  # Placeholder for manual entry
        'FILE_CREATED': created,
        'FILE_UPDATED': updated,
        'FILE_LINKED': '',  # Placeholder for manual entry
        'FILE_IDENTIFIER': '',  # Placeholder for manual entry
        'FILE_CREATORS': '',  # Placeholder for manual entry
    }

def search_files(start_dir):
    # Function to recursively search for both .shp and .tif/.tiff files
    shp_files = []
    geotiff_files = []
    other_files = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.lower().endswith('.shp'):
                shp_files.append(os.path.join(root, file))
            elif file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                geotiff_files.append(os.path.join(root, file))
            elif any(file.lower().endswith(ext) for ext in ['.txt', '.pdf', '.csv', '.dwg', '.dxf']):
                other_files.append(os.path.join(root, file))

    return shp_files, geotiff_files, other_files

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

def search_other_files(start_dir):
    # Supported file extensions
    file_extensions = ['.txt', '.pdf', '.csv', '.dwg', '.dxf']

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

        # Return the extracted metadata as a dictionary
        return {
            'FILE_NAME': file_name,
            'FILE_EXTENSION': file_extension,
            'FILE_FORMAT': file_format,
            'FILE_SOFTWARE': '',  # Placeholder for manual entry
            'FILE_HARDWARE': '',  # Placeholder for manual entry
            'FILE_OPSYS': '',  # Placeholder for manual entry
            'FILE_CREATED': created,
            'FILE_UPDATED': updated,
            'FILE_LINKED': '',  # Placeholder for manual entry
            'FILE_IDENTIFIER': '',  # Placeholder for manual entry
            'FILE_CREATORS': '',  # Placeholder for manual entry
        }

    # List to keep all metadata records
    metadata_records = []

    # Search for all files within the directory and subdirectories
    for path, name in search_files(start_dir, file_extensions):
        # Extract metadata from the file
        metadata = extract_file_metadata(path, name)
        metadata_records.append(metadata)

    # Check if we found any files
    if not metadata_records:
        print("No files found.")
    else:
        # Create an XML root element
        root = ET.Element("OtherFilesMetadata")

        for metadata in metadata_records:
            # Create an XML element for each file
            file_element = ET.SubElement(root, "File")
            for key, value in metadata.items():
                ET.SubElement(file_element, key).text = str(value)

        # Path to the output XML file
        xml_output_path = os.path.join(start_dir, 'METADATA_Other.xml')

        # Write the XML tree to the output file
        tree = ET.ElementTree(root)
        tree.write(xml_output_path, encoding='utf-8', xml_declaration=True)

        print(f"The metadata XML file has been created at: {xml_output_path}")

def search_files(start_dir, extensions=None):
    shp_files = []
    geotiff_files = []
    other_files = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.lower().endswith('.shp'):
                shp_files.append(os.path.join(root, file))
            elif file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                geotiff_files.append(os.path.join(root, file))
            elif extensions and any(file.lower().endswith(ext) for ext in extensions):
                other_files.append(os.path.join(root, file))

    return shp_files, geotiff_files, other_files

if __name__ == "__main__":
    start_dir = input("Please enter the directory to search for files: ")

    shp_files, geotiff_files, other_files = search_files(start_dir, ['.txt', '.pdf', '.csv', '.dwg', '.dxf'])

    metadata_records = []

    if shp_files:
        metadata_records.extend([extract_metadata(file, '.shp') for file in shp_files])

    if geotiff_files:
        metadata_records.extend([extract_metadata(file, '.tif') for file in geotiff_files])
        metadata_records.extend([extract_metadata(file, '.tiff') for file in geotiff_files])

    if other_files:
        # Call search_files and iterate over the results
        for path, name in search_files(start_dir, ['.txt', '.pdf', '.csv', '.dwg', '.dxf']):
            # Extract metadata from each file
            metadata = extract_file_metadata(path, name, file_size_mb, file_creation_date,)
            metadata_records.append(metadata)


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