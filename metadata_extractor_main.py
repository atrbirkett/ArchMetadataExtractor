import os
import tkinter as tk
import PIL
from PIL import Image, ImageFile
from tkinter import filedialog, simpledialog, Label, Text, Entry, Tk, Button, Frame, Scrollbar, Canvas, ttk
from tkinter.simpledialog import askstring
import tkinter.messagebox as mb
import webbrowser
from numpy import rad2deg
import rasterio
import geopandas as gpd
from datetime import datetime
import xml.etree.ElementTree as ET
import sys 
import csv
import re
import warnings

# Import the configuration file
from config_file_types import IMAGE_FILE_TYPES, GEOSPATIAL_FILE_TYPES, OTHER_FILE_TYPES, GEOPHYSICS_FILE_TYPES, EXCLUDED_DIRECTORY_SUFFIXES, GEOPHYSICS_COMP_CONDITION, THREED_FILE_TYPES

##################
##################
######
###### Directory Info
######
##################
##################

# Function to prompt for project directory
def get_directory_info_via_gui():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask for the project directory
    directory = filedialog.askdirectory(title="Select Project Directory")

    if not directory:
        # User clicked "Cancel," so exit the program
        sys.exit()

    save_directory = directory
    root.destroy()  # Close the Tkinter root window
    return directory, save_directory

##################
##################
######
###### Project Metadata
######
##################
##################

# Function to prompt for project metadata and return it as a dictionary
def get_project_metadata():
    def on_ok():
        for key in entries:
            project_metadata[key] = entries[key].get("1.0", "end-1c")
        root.destroy()

    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"  # prevent the default tab behavior

    project_metadata = {}
    fields = ['Title', 'Description', 'Subject', 'Site_Location', 'Grid_Refrence', 
              'Coverage', 'Creators', 'Publisher', 'Contributors', 'Project_ID', 
              'Dates', 'Copyright']

    root = tk.Tk()
    root.title("Project Metadata")
    root.geometry("700x500")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    entries = {}
    for field in fields:
        tk.Label(scrollable_frame, text=field).pack(anchor="w")
        text_widget = tk.Text(scrollable_frame, height=3, width=80)
        text_widget.pack(pady=5)
        text_widget.bind("<Tab>", focus_next_widget)
        entries[field] = text_widget

    ttk.Button(root, text='OK', command=on_ok).pack(pady=10)

    root.mainloop()
    return project_metadata

# Function to write the project metadata 
def process_project_metadata():
    project_metadata = get_project_metadata()
    root = ET.Element("Project_Level")
    for key, value in project_metadata.items():
        ET.SubElement(root, key).text = value
        
    return root  

##################
##################
######
###### Exclusion of GIT, Agisoft and ArcGIS files from search and file tree
######
##################
##################

# Excludes Agisoft and ArcGIS files
def is_excluded_dir(dir_name):
    return any(dir_name.endswith(suffix) for suffix in EXCLUDED_DIRECTORY_SUFFIXES)

##################
##################
######
###### Folder Tree creation
######
##################
##################

# Function to count folders for pop-up window
def count_total_folders(folder_path):
    folder_count = 0
    for _, dirs, _ in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Apply exclusion
        folder_count += len(dirs)
    return folder_count

# Function to get folder info and count
def get_folder_size_and_file_count(folder_path):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Apply exclusion
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):  # Skip symbolic links
                total_size += os.path.getsize(file_path)
                file_count += 1
    SizeMB = total_size / (1024 * 1024)  # Convert bytes to megabytes
    return round(SizeMB, 2), file_count

# Add detailed file metadata to each FILE node using the metadata extractors
def add_file_metadata(file_node, file_path, extractors):
    for extractor in extractors:
        metadata = extractor.extract_metadata(file_path)
        if metadata:
            for key, value in metadata.items():
                ET.SubElement(file_node, key).text = str(value)

# Modify this function to call the add_file_metadata function
def create_folder_element(folder_path, parent_xml_element, extractors):
    folder_name = os.path.basename(folder_path)
    if is_excluded_dir(folder_name):
        return  # Skip excluded folders

    folder_size, file_count = get_folder_size_and_file_count(folder_path)
    folder_element = ET.SubElement(parent_xml_element, 'FOLDER', {
        'Name': folder_name,
        'Size_MB': str(folder_size),
        'FileCount': str(file_count)
    })

    for item in os.listdir(folder_path):
        item_full_path = os.path.join(folder_path, item)
        if os.path.isdir(item_full_path):
            create_folder_element(item_full_path, folder_element, extractors)
        else:
            file_element = ET.SubElement(folder_element, 'FILE', {'Name': item})
            add_file_metadata(file_element, item_full_path, extractors)  # Add detailed metadata here

# Function to create XML Folder Tree file with message box
def create_folder_tree_xml(start_dir):
    # Count the total number of folders
    total_folders = count_total_folders(start_dir)

    # Create and display the message window
    message_root = tk.Tk()
    message_root.title("Processing")
    message_label = tk.Label(message_root, text=f"Creating file tree ({total_folders} folders)... please wait")
    message_label.pack(padx=20, pady=20)
    message_root.update()

    # Perform folder tree creation
    root = ET.Element('Folder_Tree')
    create_folder_element(start_dir, root)

    # Close the message window
    message_root.destroy()
    return root

##################
##################
######
###### File Search
######
##################
##################

# Get total number of files in directory
def count_files(directory, extensions):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Exclude certain directories
        for file in files:
            if file.lower().endswith('.zip'):
                continue  # Skip zip files
            if any(file.lower().endswith(ext) for ext in extensions):
                file_count += 1
    return file_count

# Recursively search for image files and extract metadata
def search_image_files(directory, extractors):
    total_files = count_files(directory, IMAGE_FILE_TYPES)

    # Create and display the message window
    message_root = tk.Tk()
    message_root.title("Processing")
    message_label = tk.Label(message_root, text=f"Searching image files ({total_files} files)... please wait")
    message_label.pack(padx=20, pady=20)
    message_root.update()

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Exclude certain directories
        for file in files:
            if file.lower().endswith('.zip'):
                continue  # Skip zip files
            if any(file.lower().endswith(ext) for ext in IMAGE_FILE_TYPES) and GEOPHYSICS_COMP_CONDITION not in file:
                file_path = os.path.join(root, file)
                file_metadata = extractors.extract_metadata(file_path)  # Extract metadata
                yield file_path, file_metadata  # Yield both file path and metadata
    # Close the message window
    message_root.destroy()

# Recursively search for both .shp and .tif/.tiff files -- for Geospatial Files and extract metadata
def search_geodata_files(start_dir, extractors):
    total_files = count_files(start_dir, GEOSPATIAL_FILE_TYPES)

    # Create and display the message window
    message_root = tk.Tk()
    message_root.title("Processing")
    message_label = tk.Label(message_root, text=f"Searching geospatial files ({total_files} files)... please wait")
    message_label.pack(padx=20, pady=20)
    message_root.update()

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Exclude certain directories
        for file in files:
            if file.lower().endswith('.zip'):
                continue  # Skip zip files
            if any(file.lower().endswith(ext) for ext in GEOSPATIAL_FILE_TYPES):
                file_path = os.path.join(root, file)
                file_metadata = extractors.extract_metadata(file_path)  # Extract metadata
                yield file_path, file_metadata  # Yield both file path and metadata

    # Close the message window
    message_root.destroy()

# Search for control point files and extract metadata
def search_control_point_files(directory, extractors):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.shp', '.csv')) and ('_GCP' in file or '_CameraPositions' in file):
                file_path = os.path.join(root, file)
                file_metadata = extractors.extract_metadata(file_path)  # Extract metadata
                yield file_path, file_metadata  # Yield both file path and metadata

# Search for 3D model files and extract metadata
def search_model_files(directory, extractors):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(tuple(THREED_FILE_TYPES)):  # Assuming THREED_FILE_TYPES is defined
                file_path = os.path.join(root, file)
                file_metadata = extractors.extract_metadata(file_path)  # Extract metadata
                yield file_path, file_metadata  # Yield both file path and metadata

# Recursively search for "other" files and extract metadata
def search_other_files(directory, extractors):
    total_files = count_files(directory, OTHER_FILE_TYPES)

    # Create and display the message window
    message_root = tk.Tk()
    message_root.title("Processing")
    message_label = tk.Label(message_root, text=f"Searching for other files ({total_files} files)... please wait")
    message_label.pack(padx=20, pady=20)
    message_root.update()

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Exclude certain directories
        for file in files:
            if file.lower().endswith('.zip'):
                continue  # Skip zip files
            if any(file.lower().endswith(ext) for ext in OTHER_FILE_TYPES):
                file_path = os.path.join(root, file)
                file_metadata = extractors.extract_metadata(file_path)  # Extract metadata
                yield file_path, file_metadata  # Yield both file path and metadata

    # Close the message window
    message_root.destroy()

# Recursively search for geophysics files and extract metadata
def search_geophysics_files(directory, extractors):
    total_files = count_files(directory, GEOPHYSICS_FILE_TYPES)

    # Create and display the message window
    message_root = tk.Tk()
    message_root.title("Processing")
    message_label = tk.Label(message_root, text=f"Searching geophysics files ({total_files} files)... please wait")
    message_label.pack(padx=20, pady=20)
    message_root.update()

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Exclude certain directories
        for file in files:
            if file.lower().endswith('.zip'):
                continue  # Skip zip files
            if any(file.lower().endswith(ext) for ext in GEOPHYSICS_FILE_TYPES) or GEOPHYSICS_COMP_CONDITION in file.upper():
                file_path = os.path.join(root, file)
                file_metadata = extractors.extract_metadata(file_path)  # Extract metadata
                yield file_path, file_metadata  # Yield both file path and metadata

    # Close the message window
    message_root.destroy()

##################
##################
######
###### Metadata Extraction
######
##################
##################

class BaseMetadataExtractor:
    def extract_metadata(self, file_path):
        raise NotImplementedError("This method should be implemented by subclasses")

class ImageMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path):
        file_size_bytes = os.path.getsize(file_path)
        file_SizeMB = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
        file_name, _ = os.path.splitext(os.path.basename(file_path))
        try:
            with Image.open(file_path) as img:
                # Determine bit depth based on image mode
                if img.mode == 'RGB':
                    bit_depth = 24  # 8 bits per channel
                elif img.mode == 'L':
                    bit_depth = 8   # 8 bits for grayscale
                else:
                    bit_depth = None  # Undefined or varies for other modes

                metadata = {
                    'FILE_TITLE': os.path.splitext(file_name)[0],  # File name without extension
                    'FILE_PATH': file_path,
                    'FILE_DESCRIPTION': '',  # Placeholder for manual entry (Optional)
                    'FILE_COVERAGE': '',  # Placeholder for manual entry (Optional)
                    'FILE_PCS': '',  # Placeholder if PCS is applicable (Optional)
                    'FILE_GCS': '',  # Placeholder if GCS is applicable (Optional)
                    'FILE_KEYWORDS': '',  # Placeholder for manual entry (Optional)
                    'FILE_VERSION': img.format_version if hasattr(img, 'format_version') else '',
                    'FILE_SIZE': f"{file_SizeMB:.2f}MB",
                    'FILE_RESOLUTION': img.info.get('dpi', ())[0] if 'dpi' in img.info else '',
                    'FILE_DIMENSIONS': f"{img.width} x {img.height}px",
                    'FILE_COLOUR': 'RGB' if img.mode == 'RGB' else 'grayscale' if img.mode == 'L' else img.mode,
                    'FILE_BITDEPTH': bit_depth,
                }
                return metadata
        except PIL.Image.DecompressionBombError:
            # Handle too-large images by returning placeholder metadata
            return {
                'FILE_TITLE': os.path.splitext(os.path.basename(file_path))[0],
                'FILE_PATH': file_path,
                'FILE_DESCRIPTION': 'Too large to process',
                'FILE_VERSION': 'Too large to process',
                'FILE_SIZE': 'Too large to process',
                'FILE_DIMENSIONS': 'Maximum size exceeded',
                'FILE_COLOUR': 'Too large to process',
                'FILE_BITDEPTH': 'Too large to process',
            }
        except OSError as e:
            print(f"Error opening file {file_path}: {e}")
            return None

class OtherMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path, file_extension):
        file_stats = os.stat(file_path)
        creation_date = datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modification_date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        file_SizeMB = file_stats.st_size / (1024 * 1024)

        common_metadata = {
            'FILE_NAME': os.path.splitext(os.path.basename(file_path))[0],
            'FILE_PATH': file_path,
            'FILE_EXTENSION': file_extension,
            'FILE_SIZE': f"{file_SizeMB:.2f}MB",
            'FILE_CREATED': creation_date,
            'FILE_UPDATED': modification_date,
            'FILE_SOFTWARE': '',  # Placeholder for manual entry
            'FILE_HARDWARE': '',  # Placeholder for manual entry
            'FILE_OPSYS': '',  # Placeholder for manual entry
            'FILE_KEYWORDS': '',  # Placeholder for manual entry
            'FILE_DATES': '',  # Placeholder for manual entry
            'FILE_PROJECTID': '',  # Placeholder for manual entry
            'FILE_LINKED': '',  # Placeholder for manual entry
            'FILE_IDENTIFIER': '',  # Placeholder for manual entry
            'FILE_COPYRIGHT': '',  # Placeholder for manual entry
            'FILE_PCS': '',  # Placeholder for manual entry (if applicable)
            'FILE_GCS': '',  # Placeholder for manual entry (if applicable)
        }

        if file_extension == '.csv' and "_G_" in os.path.basename(file_path):
            # Special handling for CSV files with "_G_" in their name
            common_metadata.update({
                'Type': 'Point',  # Example metadata for CSV files
            })

        return common_metadata

## Geophysics Files: Looking for XCP and XGD files (Terrasurveyor) or files labled with _COMP_ for the composite image files.
class GeophysicsMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path):
        file_name = os.path.basename(file_path)
        file_size_bytes = os.path.getsize(file_path)
        file_SizeMB = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes

        # Check if the file name contains "_COMP_" or the file extension is .xcp or .xgd
        if GEOPHYSICS_COMP_CONDITION in file_name.upper() or file_name.lower().endswith(tuple(GEOPHYSICS_FILE_TYPES)):
            return {
                'FILE_PATH': file_path,
                'FILE_NAME': file_name,
                'FILE_DESCRIPTION': '',  # Placeholder for manual entry
                'FILE_INSTRUMENT': '',  # Placeholder for manual entry
                'FILE_UNITS': '',  # Placeholder for manual entry
                'FILE_CENTRAL_COORDINATE': '',  # Placeholder for manual entry
                'FILE_NW_COORDINATE': '',  # Placeholder for manual entry
                'FILE_SE_COORDINATE': '',  # Placeholder for manual entry
                'FILE_COMMENTS': '',  # Placeholder for manual entry
                'FILE_1ST_TRAVERSE_DIRECTION': '',  # Placeholder for manual entry
                'FILE_METHOD': '',  # Placeholder for manual entry
                'FILE_SENSORS': '',  # Placeholder for manual entry
                'FILE_DUMMY_VALUE': '',  # Placeholder for manual entry
                'FILE_COMPOSITE_SIZE': '',  # Placeholder for manual entry
                'FILE_SURVEY_SIZE': '',  # Placeholder for manual entry
                'FILE_GRID_SIZE': '',  # Placeholder for manual entry
                'FILE_X_INTERVAL': '',  # Placeholder for manual entry
                'FILE_Y_INTERVAL': '',  # Placeholder for manual entry
                'FILE_SIZE': f"{file_SizeMB:.2f}MB",  # Include file size in MB
            }
        return None  # Default metadata for non-matching files

class GeospatialMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path, file_extension):
        associated_files = []  # Initialize the list for associated files
        try:
            if file_extension.lower() in ['.tif', '.tiff']:
                # For GeoTIFF files
                with rasterio.open(file_path) as src:
                    tags = src.tags()
                    file_size_bytes = os.path.getsize(file_path)
                    file_SizeMB = file_size_bytes / 1048576  # Convert bytes to megabytes

                    # Get associated files based on the raster file name
                    associated_files = self.get_associated_files(file_path)

                    return {
                        'FILE_TITLE': tags.get('Title', 'Unknown'),  # Adding FILE_TITLE
                        'FILE_NAME': os.path.splitext(os.path.basename(file_path))[0],
                        'FILE_PATH': file_path,
                        'FILE_EXTENSION': os.path.splitext(file_path)[1],
                        'FILE_DESCRIPTION': tags.get('Description', 'Unknown'),
                        'FILE_KEYWORDS': tags.get('Keywords', 'Unknown'),  # Adding FILE_KEYWORDS
                        'FILE_VERSION': tags.get('Version', src.driver),
                        'FILE_SIZE': f"{file_SizeMB:.2f}MB",  # Store file size in MB
                        'FILE_BANDS': str(src.count),
                        'FILE_CELL_SIZE': str(src.res),
                        'FILE_COVERAGE': str(src.bounds),
                        'FILE_PCS': src.crs.to_string() if src.crs else 'Unknown',
                        'FILE_GCS': src.crs.to_epsg() if src.crs else 'Unknown',
                        'FILE_ASSOCIATED': ', '.join(associated_files),  # Include associated files
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
                file_SizeMB = file_size_bytes / 1024 / 1024  # Convert bytes to MB
                
                # Get associated files for shapefile
                associated_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(file_name_without_extension)]

                return {
                    'FILE_PROJECTID': '',  # Placeholder for manual entry
                    'FILE_NAME': file_name_without_extension,
                    'FILE_PATH': os.path.dirname(file_path),
                    'FILE_EXTENSION': file_extension,
                    'FILE_SIZE': f"{file_SizeMB:.2f}MB",  # File size in MB
                    'FILE_DESCRIPTION': "No Description",  # Placeholder for manual entry
                    'FILE_GEOMTYPE': geometry_type,
                    'FILE_FEATURE_COUNT': str(feature_count),
                    'FILE_METHOD': '',  # Placeholder for manual entry
                    'FILE_DATES': file_creation_date,
                    'FILE_COVERAGE': '',  # Placeholder for manual entry
                    'FILE_PCS': pcs,
                    'FILE_GCS': gcs,
                    'FILE_SCALE': '',  # Placeholder for manual entry
                    'FILE_ASSOCIATED': ', '.join(associated_files),  # Include associated files
                }
        except rasterio.errors.RasterioError as e:
            print(f"Rasterio error with file {file_path}: {e}")
            return None

        except Exception as e:
            print(f"General error reading {file_path}: {e}")
            return None

    @staticmethod
    def get_associated_files(file_path):
        """Get associated files based on the main raster file's name."""
        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
        folder_path = os.path.dirname(file_path)
        # Define the extensions for associated files
        associated_extensions = ['.tfw', '.prj', '.kml', '.shp', '.shx', '.dbf']
        associated_files = [f for f in os.listdir(folder_path) if f.startswith(file_name_without_extension) and f.endswith(tuple(associated_extensions))]
        return associated_files

# Folder Level Metadata Extractor
class FolderLevelMetadataExtractor(BaseMetadataExtractor):
    def extract_folder_metadata(self, folder_path):
        metadata = {}
        folder_name = os.path.basename(folder_path)

        # Process folder-level metadata
        metadata.update({
            'FILE_SUBJECT': '',  # Placeholder for folder-level subject keywords
            'FILE_ACCURACY': '',  # Placeholder for intended accuracy at folder level
            'FILE_COVERAGE': '',  # Placeholder for coverage of the folder contents
            'FILE_PCS': '',  # Placeholder for Projected Coordinate System (PCS)
            'PROJECT_RELATIONS': '',  # Placeholder for folder-level relations (source references)
            'PROJECT_LANGUAGE': 'English',  # Default to English
            'PROJECT_TYPE': '',  # Placeholder for resource type (primary data, processed data)
            'PROJECT_FORMAT': '',  # Placeholder for format (e.g., AutoCAD, 3D Model)
        })

        return metadata

# Control Point Metadata Extractor
class ControlPointMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path):
        metadata = {}
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_directory = os.path.dirname(file_path)

        # Look for associated files (e.g., .xml, .shx, .dbf, etc.)
        associated_files = [f for f in os.listdir(file_directory) if f.startswith(file_name)]
        linked_files = ', '.join(associated_files)

        # Process the main control point data (coordinates, etc.)
        if file_path.endswith(".shp"):
            # Example extraction from shapefile (using libraries like geopandas)
            gdf = gpd.read_file(file_path)
            # Assuming we extract the first geometry for simplicity, handle iteration for multiple
            first_geometry = gdf.geometry.iloc[0]

            if first_geometry.geom_type == 'Point':
                # Extracting x and y for Point geometries
                metadata['CONTL_X'] = first_geometry.x
                metadata['CONTL_Y'] = first_geometry.y
                metadata['CONTL_Z'] = first_geometry.z if hasattr(first_geometry, 'z') else ''

            elif first_geometry.geom_type == 'Polygon':
                # Extracting the centroid for Polygon geometries
                metadata['CONTL_X'] = first_geometry.centroid.x
                metadata['CONTL_Y'] = first_geometry.centroid.y
                metadata['CONTL_Z'] = ''  # Set to empty or handle as needed

        elif file_path.endswith(".csv"):
            # Example CSV extraction for control points (assuming columns for X, Y, Z)
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    metadata['CONTL_X'] = row.get('X')
                    metadata['CONTL_Y'] = row.get('Y')
                    metadata['CONTL_Z'] = row.get('Z', '')  # Handle missing Z

        # Add other metadata fields
        metadata.update({
            'CONTL_CX': '',  # Placeholder for Covariance X (from .dbf if available)
            'CONTL_CY': '',  # Placeholder for Covariance Y
            'CONTL_CZ': '',  # Placeholder for Covariance Z
            'CONTL_Location': '',  # Placeholder for textual description of location
            'FILE_DATES': '',  # Placeholder for dates (if present in attributes)
            'FILE_PROJECTID': '',  # Placeholder for project ID or reference code
            'FILE_COVERAGE': '',  # Placeholder for site location or coverage
            'FILE_PCS': '',  # Placeholder for Projected Coordinate System (from .prj file)
            'FILE_GCS': '',  # Placeholder for Geographic Coordinate System (from .prj file)
            'FILE_LINKED': linked_files  # Add the associated files as a comma-separated list
        })

        return metadata
    
# Three-Dimensional Model Metadata Extractor
class ThreeDimensionalModelMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path):
        metadata = {}
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_directory = os.path.dirname(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB

        metadata.update({
            'FILE_NAME': file_name,
            'FILE_PATH': file_directory,
            'FILE_EXTENSION': os.path.splitext(file_path)[1],
            'FILE_SIZE': f"{file_size:.2f}MB",
            'FILE_VERT': '',  # Number of vertices (to be extracted from model if available)
            'FILE_POLY': '',  # Number of polygons
            'FILE_GEOMTYPE': '',  # Geometry type
            'FILE_UNITSCALE': '',  # Scale in units
            'FILE_COVERAGE': '',  # Coverage information
            'FILE_PCS': '',  # Projected Coordinate System (if available)
            'FILE_GCS': '',  # Geographic Coordinate System (if available)
            'FILE_LAYERS': '',  # Number of layers if applicable
            'FILE_TEXTURES': '',  # Texture info if available
            'FILE_MATERIAL': '',  # Material info if available
            'FILE_LIGHT': '',  # Light source information
            'FILE_TYPE': '',  # Basic, technical, or extended file type
            'FILE_LOD': '',  # Level of detail
        })

        return metadata

import subprocess  # Ensure subprocess is imported

def open_folder(path):
    if sys.platform == "win32":
        os.startfile(path)
    else:
        # Adjust the opener command for macOS or Linux if necessary
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])

# Function to create a custom dialog
def custom_message_box(parent, folder_tree_xml_path, combined_xml_path, total_folders, directory):  # Added 'directory' parameter
    # Create a Toplevel window
    dialog = tk.Toplevel(parent)
    dialog.title("Process Complete")
    dialog.geometry("400x200")  # Adjust the size as needed

    # Add a frame to the Toplevel window
    frame = ttk.Frame(dialog)
    frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    # Display the message
    message = f"Folder tree and combined metadata file have been created in the specified directory\n" \
              f"Total folders scanned: {total_folders}"
    message_label = ttk.Label(frame, text=message, background='#f0f0f0', justify="left")
    message_label.pack(pady=10, fill=tk.X)

    # Function to handle 'Yes' button click
    def on_yes():
        open_folder(directory)  # Use the passed directory variable
        dialog.destroy()

    # Function to handle 'No' button click
    def on_no():
        dialog.destroy()

    # Add 'Yes' and 'No' buttons
    yes_button = ttk.Button(frame, text="Yes", command=on_yes)
    yes_button.pack(side=tk.LEFT, expand=True, pady=10, padx=(0, 10))

    no_button = ttk.Button(frame, text="No", command=on_no)
    no_button.pack(side=tk.RIGHT, expand=True, pady=10, padx=(10, 0))

    # Wait for the user to close the dialog
    dialog.transient(parent)  # Set to be on top of the main window
    dialog.grab_set()  # Prevent interaction with the main window
    parent.wait_window(dialog)
            
##################
##################
######
###### Main
######
##################
##################
def open_folder(path):
    # Function to open the folder, adjust based on your platform
    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])

def show_completion_window(folder_tree_xml_path, combined_xml_path, total_folders, directory):
    # Create a new window to show completion message
    completion_window = tk.Tk()
    completion_window.title("Process Complete")

    # Message label
    message = f"Folder tree and combined metadata file\n"\
              f"has been created in the specified directory.\n" \
              f"\n" \
              f"Total folders scanned: {total_folders}"
    ttk.Label(completion_window, text=message).pack(padx=20, pady=10)

    # Button to open the folder
    open_button = ttk.Button(completion_window, text="Open Directory", 
                             command=lambda: open_folder(directory))
    open_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Exit button
    exit_button = ttk.Button(completion_window, text="Finish", command=completion_window.destroy)
    exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Run the window's main loop
    completion_window.mainloop()

if __name__ == "__main__":
    # Get directory details and location for saving the XML
    directory, save_directory = get_directory_info_via_gui()
    combined_root = ET.Element("CombinedMetadata")

    # Process project metadata
    project_metadata = process_project_metadata()
    if project_metadata is not None:
        combined_root.append(project_metadata)

    # Create a list of extractor instances
    extractors = [
        ImageMetadataExtractor(),
        GeospatialMetadataExtractor(),
        OtherMetadataExtractor(),
        ThreeDimensionalModelMetadataExtractor(),
        ControlPointMetadataExtractor(),
        GeophysicsMetadataExtractor()
    ]

    # Create a folder element in the combined XML
    folder_tree_element = ET.SubElement(combined_root, 'Folder_Tree')

    # Function to create folders and add metadata
    def create_folder_with_metadata(folder_path, parent_xml_element):
        folder_name = os.path.basename(folder_path)
        folder_size, file_count = get_folder_size_and_file_count(folder_path)
        folder_element = ET.SubElement(parent_xml_element, 'FOLDER', {
            'Name': folder_name,
            'Size_MB': str(folder_size),
            'FileCount': str(file_count)
        })

        for item in os.listdir(folder_path):
            item_full_path = os.path.join(folder_path, item)
            if os.path.isdir(item_full_path):
                create_folder_with_metadata(item_full_path, folder_element)
            else:
                file_element = ET.SubElement(folder_element, 'FILE', {'Name': item})

                # Track seen metadata to prevent duplication
                metadata_seen = set()

                for extractor in extractors:
                    metadata = None

                    # Conditional checks for each extractor
                    if isinstance(extractor, ImageMetadataExtractor) and item.lower().endswith(tuple(IMAGE_FILE_TYPES)):
                        metadata = extractor.extract_metadata(item_full_path)
                    elif isinstance(extractor, GeospatialMetadataExtractor) and item.lower().endswith(tuple(GEOSPATIAL_FILE_TYPES)):
                        metadata = extractor.extract_metadata(item_full_path, os.path.splitext(item)[1])
                    elif isinstance(extractor, OtherMetadataExtractor) and item.lower().endswith(tuple(OTHER_FILE_TYPES)):
                        metadata = extractor.extract_metadata(item_full_path, os.path.splitext(item)[1])
                    elif isinstance(extractor, GeophysicsMetadataExtractor) and item.lower().endswith(tuple(GEOPHYSICS_FILE_TYPES)):
                        metadata = extractor.extract_metadata(item_full_path)
                    elif isinstance(extractor, ControlPointMetadataExtractor) and (item.lower().endswith('.shp') or item.lower().endswith('.csv')):
                        metadata = extractor.extract_metadata(item_full_path)
                    elif isinstance(extractor, ThreeDimensionalModelMetadataExtractor) and item.lower().endswith(tuple(THREED_FILE_TYPES)):
                        metadata = extractor.extract_metadata(item_full_path)

                    # Add metadata only if it has been seen before
                    if metadata:
                        # Check for FILE_TITLE and handle missing cases
                        file_title = metadata.get('FILE_TITLE', None)
                        if file_title and file_title not in metadata_seen:
                            metadata_seen.add(file_title)  # Keep track of added metadata
                            for key, value in metadata.items():
                                ET.SubElement(file_element, key).text = str(value)
                        else:
                            print(f"Warning: 'FILE_TITLE' missing or duplicate for {item_full_path}. Metadata: {metadata}")

    # Process the directory and create the folder structure with metadata
    create_folder_with_metadata(directory, folder_tree_element)

    # Write Combined Metadata XML
    combined_xml_path = os.path.join(directory, 'METADATA.xml')
    combined_tree = ET.ElementTree(combined_root)
    combined_tree.write(combined_xml_path, encoding='utf-8', xml_declaration=True)

    # Total folders processed
    total_folders = count_total_folders(directory)

    # Call the custom completion window function
    def show_completion_window(folder_tree_xml_path, combined_xml_path, total_folders, directory):
