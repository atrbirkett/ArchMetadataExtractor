import os
from PIL import Image
import rasterio
import geopandas as gpd
from datetime import datetime
import xml.etree.ElementTree as ET

##################
##################
######
####### Project Metadata
######
##################
##################

# Function to prompt for project metadata and return it as a dictionary
def get_project_metadata():
    return {
        'PROJECT_TITLE': input("Enter the PROJECT_TITLE: "),
        'PROJECT_DESCRIPTION': input("Enter the PROJECT_DESCRIPTION: "),
        'PROJECT_SUBJECT': input("Enter the PROJECT_SUBJECT: "),
        'PROJECT_COVERAGE': input("Enter the PROJECT_COVERAGE: "),
        'PROJECT_PCS': input("Enter the PROJECT_PCS: "),
        'PROJECT_GCS': input("Enter the PROJECT_GCS: "),
        'PROJECT_CREATORS': input("Enter the PROJECT_CREATORS: "),
        'PROJECT_PUBLISHER': input("Enter the PROJECT_PUBLISHER: "),
        'PROJECT_CONTRIBUTORS': input("Enter the PROJECT_CONTRIBUTORS: "),
        'PROJECT_PROJECTID': input("Enter the PROJECT_PROJECTID: "),
        'PROJECT_DATES': input("Enter the PROJECT_DATES: "),
        'PROJECT_COPYRIGHT': input("Enter the PROJECT_COPYRIGHT: "),
    }

def process_project_metadata(save_directory, output_xml_name="METADATA_Project.xml"):
    project_metadata = get_project_metadata()
    root = ET.Element("ProjectMetadata")
    
    for key, value in project_metadata.items():
        ET.SubElement(root, key).text = value

    output_xml_path = os.path.join(save_directory, output_xml_name)
    
    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    tree = ET.ElementTree(root)
    tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)
    print(f"Project metadata has been saved to {output_xml_path}")

def get_folder_size_and_file_count(folder_path):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):  # Skip symbolic links
                total_size += os.path.getsize(file_path)
                file_count += 1
    size_mb = total_size / (1024 * 1024)  # Convert bytes to megabytes
    return round(size_mb, 2), file_count  # Round to 2 decimal places

def create_folder_element(folder_path, parent_xml_element):
    folder_name = os.path.basename(folder_path)
    folder_size, file_count = get_folder_size_and_file_count(folder_path)
    folder_element = ET.SubElement(parent_xml_element, 'FOLDER', {
        'FOLDER_Name': folder_name,
        'FOLDER_SizeMB': str(folder_size),
        'FOLDER_FileCount': str(file_count)
    })

    for item in os.listdir(folder_path):
        item_full_path = os.path.join(folder_path, item)
        if os.path.isdir(item_full_path):
            create_folder_element(item_full_path, folder_element)
        else:
            file_element = ET.SubElement(folder_element, 'FILE', {'FILE_Name': item})
            # Optionally, add file details here

##################
##################
######
###### File Tree creation
######
##################
##################

def get_folder_size_and_file_count(folder_path):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):  # Skip symbolic links
                total_size += os.path.getsize(file_path)
                file_count += 1
    size_mb = total_size / (1024 * 1024)  # Convert bytes to megabytes
    return round(size_mb, 2), file_count  # Round to 2 decimal places

def create_folder_element(folder_path, parent_xml_element):
    folder_name = os.path.basename(folder_path)
    folder_size, file_count = get_folder_size_and_file_count(folder_path)
    folder_element = ET.SubElement(parent_xml_element, 'FOLDER', {
        'FOLDER_Name': folder_name,
        'FOLDER_SizeMB': str(folder_size),
        'FOLDER_FileCount': str(file_count)
    })

    for item in os.listdir(folder_path):
        item_full_path = os.path.join(folder_path, item)
        if os.path.isdir(item_full_path):
            create_folder_element(item_full_path, folder_element)
        else:
            file_element = ET.SubElement(folder_element, 'FILE', {'FILE_Name': item})
            # Optionally, add file details here

def create_folder_tree_xml(start_dir):
    root = ET.Element('FolderTree')
    create_folder_element(start_dir, root)

    # Write the XML tree to a file
    tree = ET.ElementTree(root)
    xml_output_path = os.path.join(start_dir, 'METADATA_FolderTree.xml')
    tree.write(xml_output_path, encoding='utf-8', xml_declaration=True)

    print(f"XML file tree has been saved to {xml_output_path}")

##################
##################
######
####### Raster/Vector Metadata
######
##################
##################

# Function to recursively search for image files
def search_image_files(directory):
    # Supported image file extensions
    image_extensions = ['.tiff', '.tif', '.png', '.jpg']
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if (
                any(file.lower().endswith(ext) for ext in image_extensions) and
                "_COMP_" not in file
            ):
                yield file_path

# Function to extract metadata from an image file
def extract_image_metadata(file_path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))

    with Image.open(file_path) as img:
        # Determine bit depth based on image mode
        if img.mode == 'RGB':
            bit_depth = 24  # 8 bits per channel
        elif img.mode == 'L':
            bit_depth = 8   # 8 bits for grayscale
        else:
            bit_depth = None  # Undefined or varies for other modes

        metadata = {
            'FILE_NAME': os.path.splitext(file_name)[0],  # File name without extension
            'FILE_PATH': file_path,                    
            'FILE_TITLE': '',  # Placeholder for manual entry
            'FILE_DESCRIPTION': '',  # Placeholder for manual entry
            'FILE_KEYWORDS': '',  # Placeholder for manual entry
            'FILE_VERSION': img.format_version if hasattr(img, 'format_version') else '',
            'FILE_SIZE': f"{file_size_mb:.2f} MB",
            'FILE_RESOLUTION': img.info.get('dpi', ())[0] if 'dpi' in img.info else '',
            'FILE_DIMENSIONS': f"{img.width} x {img.height}px",
            'FILE_COLOUR': 'RGB' if img.mode == 'RGB' else 'grayscale' if img.mode == 'L' else img.mode,
            'FILE_BITDEPTH': bit_depth,
        }
        return metadata

# Main function to create metadata for image files and save as XML
def create_image_metadata(start_dir):
    metadata_records = []
    for file_path in search_image_files(start_dir):
        metadata = extract_image_metadata(file_path)
        if metadata:
            metadata_records.append(metadata)

    # Create an XML root element
    root = ET.Element("ImageMetadata")

    for metadata in metadata_records:
        # Create an XML element for each image
        image_element = ET.SubElement(root, "Image")
        for key, value in metadata.items():
            ET.SubElement(image_element, key).text = str(value)

    # Path to the output XML file
    xml_output_path = os.path.join(start_dir, 'METADATA_Image.xml')

    # Write the XML tree to the output file
    tree = ET.ElementTree(root)
    tree.write(xml_output_path, encoding='utf-8', xml_declaration=True)

    print(f"The metadata XML file has been created at: {xml_output_path}")


##################
##################
######
####### Geodata Metadata
######
##################
##################

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
                    'FILE_PATH': file_path,                    
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

def create_Geospatial_metadata(metadata_records, output_path, root_element_name):
    root = ET.Element(root_element_name)

    # Filter out None values from metadata_records
    metadata_records = [metadata for metadata in metadata_records if metadata is not None]

    for metadata in metadata_records:
        element = ET.SubElement(root, "Item")
        for key, value in metadata.items():
            ET.SubElement(element, key).text = str(value)

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    if metadata_records:
        print(f"The metadata XML file has been created at: {output_path}")
    else:
        print("No supported files found for XML creation.")



##################
##################
######
####### Process as Main
######
##################
##################

if __name__ == "__main__":
    directory = input("Enter the directory where you want to save the XML files: ")
    
    # Process project metadata
    process_project_metadata(directory)

    # Process folder tree metadata
    create_folder_tree_xml(directory)

    # Process raster/vector metadata
    create_image_metadata(directory)

    # Gather and process geospatial metadata
    shp_files, geotiff_files = search_files(directory)
    geospatial_metadata_records = []
    for file_path in shp_files:
        metadata = extract_metadata(file_path, '.shp')
        if metadata:
            geospatial_metadata_records.append(metadata)
    for file_path in geotiff_files:
        metadata = extract_metadata(file_path, '.tif')  # assuming .tif and .tiff are treated the same
        if metadata:
            geospatial_metadata_records.append(metadata)

    # Create geospatial metadata XML
    output_xml_path = os.path.join(directory, 'METADATA_Geospatial.xml')
    create_Geospatial_metadata(geospatial_metadata_records, output_xml_path, "GeospatialMetadata")