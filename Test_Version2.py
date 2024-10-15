import os
import time
import tkinter as tk
from tkinter import simpledialog
from PIL import Image
import csv
import rasterio
import geopandas as gpd
import xml.etree.ElementTree as ET

# Project Metadata Extractor
def project_metadata_extractor():
    # Initialize Tkinter GUI
    root = tk.Tk()
    root.withdraw()

    # Prompt the user for input fields
    project_metadata = {}
    project_metadata['PROJECT_TITLE'] = simpledialog.askstring("Input", "Enter the Project Title:")
    project_metadata['PROJECT_DESCRIPTION'] = simpledialog.askstring("Input", "Enter the Project Description:")
    project_metadata['PROJECT_SUBJECT'] = simpledialog.askstring("Input", "Enter the Subject Keywords:")
    project_metadata['PROJECT_COVERAGE'] = simpledialog.askstring("Input", "Enter the Spatial/Temporal Coverage:")
    project_metadata['PROJECT_PCS'] = simpledialog.askstring("Input", "Enter the Projected Coordinate System:")
    project_metadata['PROJECT_GCS'] = simpledialog.askstring("Input", "Enter the Geographic Coordinate System:")
    project_metadata['PROJECT_CREATORS'] = simpledialog.askstring("Input", "Enter the Creators:")
    project_metadata['PROJECT_PUBLISHER'] = simpledialog.askstring("Input", "Enter the Publisher:")
    project_metadata['PROJECT_CONTRIBUTORS'] = simpledialog.askstring("Input", "Enter the Contributors:")
    project_metadata['PROJECT_PROJECTID'] = simpledialog.askstring("Input", "Enter the Project ID:")
    project_metadata['PROJECT_DATES'] = simpledialog.askstring("Input", "Enter the Dates:")
    project_metadata['PROJECT_COPYRIGHT'] = simpledialog.askstring("Input", "Enter the Copyright Holder:")

    # Construct XML Element
    project_elem = ET.Element('Project_Level')
    for key, value in project_metadata.items():
        sub_elem = ET.SubElement(project_elem, key)
        sub_elem.text = value

    return project_elem

# Folder Level Metadata Extractor
def folder_metadata_extractor(folder_path):
    metadata = {}
    metadata['FOLDER_NAME'] = os.path.basename(folder_path)
    metadata['FOLDER_PATH'] = folder_path
    metadata['FOLDER_DESCRIPTION'] = "Manual entry required"
    metadata['FOLDER_SIZE'] = f"{get_folder_size(folder_path):.2f} MB"
    metadata['FOLDER_COUNT'] = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

    folder_elem = ET.Element('Folder')
    for key, value in metadata.items():
        sub_elem = ET.SubElement(folder_elem, key)
        sub_elem.text = str(value)

    return folder_elem

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # Convert bytes to MB

# Other Metadata Extractor (for non-image files)
def other_metadata_extractor(file_path):
    stats = os.stat(file_path)
    file_size = stats.st_size / (1024 * 1024)  # Convert bytes to MB

    metadata = {
        'FILE_NAME': os.path.splitext(os.path.basename(file_path))[0],
        'FILE_PATH': file_path,
        'FILE_EXTENSION': os.path.splitext(file_path)[1],
        'FILE_SIZE': f"{file_size:.2f} MB",
        'FILE_CREATED': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_ctime)),
        'FILE_UPDATED': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime)),
        'FILE_SOFTWARE': 'Manual entry required',
        'FILE_HARDWARE': 'Manual entry required',
        'FILE_OPSYS': os.name
    }

    file_elem = ET.Element('File')
    for key, value in metadata.items():
        sub_elem = ET.SubElement(file_elem, key)
        sub_elem.text = str(value)

    return file_elem

# Image Metadata Extractor
def image_metadata_extractor(file_path):
    img = Image.open(file_path)
    img_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB

    metadata = {
        'FILE_TITLE': 'Manual entry required',
        'FILE_PATH': file_path,
        'FILE_SIZE': f"{img_size:.2f} MB",
        'FILE_RESOLUTION': f"{img.info.get('dpi', (72, 72))[0]} dpi",
        'FILE_DIMENSIONS': f"{img.width} x {img.height}",
        'FILE_COLOUR': img.mode,
        'FILE_BITDEPTH': img.bits
    }

    img_elem = ET.Element('Image')
    for key, value in metadata.items():
        sub_elem = ET.SubElement(img_elem, key)
        sub_elem.text = str(value)

    return img_elem

# Control Point Metadata Extractor
def control_point_metadata_extractor(file_path):
    metadata = {}
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    if file_path.endswith('.shp'):
        gdf = gpd.read_file(file_path)
        first_geom = gdf.geometry.iloc[0]
        metadata['CONTL_X'] = first_geom.x
        metadata['CONTL_Y'] = first_geom.y
        metadata['CONTL_Z'] = getattr(first_geom, 'z', '')
    elif file_path.endswith('.csv'):
        with open(file_path, mode='r') as infile:
            reader = csv.DictReader(infile)
            first_row = next(reader)
            metadata['CONTL_X'] = first_row.get('X', '')
            metadata['CONTL_Y'] = first_row.get('Y', '')
            metadata['CONTL_Z'] = first_row.get('Z', '')

    # Add placeholders
    metadata.update({
        'CONTL_CX': 'Manual entry required',
        'CONTL_CY': 'Manual entry required',
        'CONTL_CZ': 'Manual entry required',
        'CONTL_LOCATION': 'Manual entry required',
        'FILE_DATES': 'Manual entry required',
        'FILE_PROJECTID': 'Manual entry required',
        'FILE_COVERAGE': 'Manual entry required',
        'FILE_PCS': 'Manual entry required',
        'FILE_GCS': 'Manual entry required',
        'FILE_LINKED': ', '.join([f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(base_name)])
    })

    control_elem = ET.Element('Control_Point')
    for key, value in metadata.items():
        sub_elem = ET.SubElement(control_elem, key)
        sub_elem.text = str(value)

    return control_elem

# Folder Tree XML Creation
def create_folder_tree_xml(start_dir):
    root = ET.Element('Folder_Tree')

    def create_folder_element(folder_path, parent_xml_element):
        folder_elem = folder_metadata_extractor(folder_path)
        parent_xml_element.append(folder_elem)

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                create_folder_element(item_path, folder_elem)
            else:
                file_elem = other_metadata_extractor(item_path)
                folder_elem.append(file_elem)

    create_folder_element(start_dir, root)
    return ET.ElementTree(root)

# Example Usage
if __name__ == "__main__":
    project_metadata = project_metadata_extractor()
    folder_tree = create_folder_tree_xml('/path/to/project_directory')

    # Save the XML file
    folder_tree.write('metadata_output.xml', encoding='utf-8', xml_declaration=True)
