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

# Excludes certain directories
def is_excluded_dir(dir_name):
    return any(dir_name.endswith(suffix) for suffix in EXCLUDED_DIRECTORY_SUFFIXES)

##################
##################
######
###### Folder Tree creation
######
##################
##################

# Count total folders for message box
def count_total_folders(folder_path):
    folder_count = 0
    for _, dirs, _ in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
        folder_count += len(dirs)
    return folder_count

# Get folder size and file count
def get_folder_size_and_file_count(folder_path):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)
                file_count += 1
    SizeMB = total_size / (1024 * 1024)
    return round(SizeMB, 2), file_count

# Create folder tree with metadata for files
def create_folder_tree_xml(start_dir, all_metadata_records):
    root = ET.Element('Folder_Tree')

    # Walk through directories
    for root_dir, dirs, files in os.walk(start_dir):
        if is_excluded_dir(os.path.basename(root_dir)):
            continue

        folder_element = ET.SubElement(root, 'Folder', {
            'Name': os.path.basename(root_dir),
            'Size_MB': str(get_folder_size_and_file_count(root_dir)[0]),
            'FileCount': str(len(files))
        })

        # Process files in the current directory
        for file in files:
            file_path = os.path.join(root_dir, file)
            file_element = ET.SubElement(folder_element, 'File', {'Name': file})

            # Match file path with metadata records and append metadata to the file element
            for metadata in all_metadata_records:
                if 'FILE_PATH' in metadata and metadata['FILE_PATH'] == file_path:
                    for key, value in metadata.items():
                        ET.SubElement(file_element, key).text = str(value)

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

# Recursively search for image files
def search_image_files(directory):
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
                yield os.path.join(root, file)

    # Close the message window
    message_root.destroy()

# Recursively search for both .shp and .tif/.tiff files -- for Geospatial Files
def search_geodata_files(start_dir):
    total_files = count_files(start_dir, GEOSPATIAL_FILE_TYPES)

    # Create and display the message window
    message_root = tk.Tk()
    message_root.title("Processing")
    message_label = tk.Label(message_root, text=f"Searching geospatial files ({total_files} files)... please wait")
    message_label.pack(padx=20, pady=20)
    message_root.update()

    shp_files = []
    geotiff_files = []

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]  # Exclude certain directories
        for file in files:
            if file.lower().endswith('.zip'):
                continue  # Skip zip files
            if any(file.lower().endswith(ext) for ext in GEOSPATIAL_FILE_TYPES):
                if file.lower().endswith('.shp'):
                    shp_files.append(os.path.join(root, file))
                elif file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                    geotiff_files.append(os.path.join(root, file))

    # Close the message window
    message_root.destroy()

    return shp_files, geotiff_files

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
                    'FILE_DESCRIPTION': '',  # Placeholder for manual entry
                    'FILE_COVERAGE': '',  # Placeholder for manual entry (coverage information)
                    'FILE_PCS': '',  # Placeholder if PCS is applicable
                    'FILE_GCS': '',  # Placeholder if GCS is applicable
                    'FILE_KEYWORDS': '',  # Placeholder for manual entry
                    'FILE_VERSION': img.format_version if hasattr(img, 'format_version') else '',
                    'FILE_SIZE': f"{file_SizeMB:.2f}MB",
                    'FILE_RESOLUTION': img.info.get('dpi', ())[0] if 'dpi' in img.info else '',
                    'FILE_DIMENSIONS': f"{img.width} x {img.height}px",
                    'FILE_COLOUR': 'RGB' if img.mode == 'RGB' else 'grayscale' if img.mode == 'L' else img.mode,
                    'FILE_BITDEPTH': bit_depth,
                }
                return metadata
        except PIL.Image.DecompressionBombError:
            # If the image is too large, set a placeholder or maximum size
            return {
                'FILE_TITLE': os.path.splitext(os.path.basename(file_path))[0],
                'FILE_PATH': file_path,
                'FILE_DESCRIPTION': '',  # Placeholder for manual entry
                'FILE_COVERAGE': '',  # Placeholder for manual entry
                'FILE_PCS': '',
                'FILE_GCS': '',
                'FILE_KEYWORDS': '',
                'FILE_VERSION': 'Too large to process',
                'FILE_SIZE': 'Too large to process',
                'FILE_DIMENSIONS': 'Maximum size exceeded',
                'FILE_RESOLUTION': 'Too large to process',
                'FILE_COLOUR': 'Too large to process',
                'FILE_BITDEPTH': 'Too large to process',
            }

        except OSError as e:
            print(f"Error opening file {file_path}: {e}")
            return None

    def create_image_metadata(self, start_dir):  # Include 'self' as the first parameter
        metadata_records = []
        root = ET.Element("Raster_And_Vector_File_Metadata")

        for file_path in search_image_files(start_dir):
            metadata = self.extract_metadata(file_path)  # Use 'self' to call another instance method
            if metadata:
                metadata_records.append(metadata)

        for metadata in metadata_records:
            image_element = ET.SubElement(root, "File")
            for key, value in metadata.items():
                ET.SubElement(image_element, key).text = str(value)

        return root

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
            'FILE_SIZE': f"{file_SizeMB:.2f}",
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
                'Type': 'Point',  # Placeholder for manual entry
            })

        return common_metadata
    
    def process_other_metadata(self, start_dir):
        root = ET.Element("Other_Files_Metadata")
        for path, name in search_other_files(start_dir):
            file_extension = os.path.splitext(name)[1]
            metadata = self.extract_metadata(path, file_extension)
            if metadata:
                file_element = ET.SubElement(root, "File")
                for key, value in metadata.items():
                    ET.SubElement(file_element, key).text = str(value)

        return root

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
                'FILE_SIZE': f"{file_SizeMB:.2f}MB",
            }

        # Default metadata for non-compressed files
        return None
    
    def process_geophysics_metadata(self, start_dir):
        root = ET.Element("Geophysics_Files")

        geophysics_file_paths = search_geophysics_files(start_dir)

        for root_dir, _, files in os.walk(start_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                file_metadata = self.extract_metadata(file_path)
                if file_metadata:
                    file_element = ET.SubElement(root, "File")
                    for key, value in file_metadata.items():
                        ET.SubElement(file_element, key).text = str(value)

        return root

class GeospatialMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path, file_extension):
        associated_files = []
        try:
            if file_extension.lower() in ['.tif', '.tiff']:
                with rasterio.open(file_path) as src:
                    tags = src.tags()
                    file_size_bytes = os.path.getsize(file_path)
                    file_SizeMB = file_size_bytes / 1048576  # Convert bytes to megabytes

                    # Get associated files based on the raster file name
                    associated_files = self.get_associated_files(file_path)

                    return {
                        'FILE_TITLE': tags.get('Title', 'Unknown'),
                        'FILE_NAME': os.path.splitext(os.path.basename(file_path))[0],
                        'FILE_PATH': file_path,
                        'FILE_EXTENSION': os.path.splitext(file_path)[1],
                        'FILE_DESCRIPTION': tags.get('Description', 'Unknown'),
                        'FILE_KEYWORDS': tags.get('Keywords', 'Unknown'),
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
                gdf = gpd.read_file(file_path)
                geometry_type = gdf.geometry.geom_type.unique()[0] if len(gdf) > 0 else 'Unknown'
                feature_count = len(gdf)
                file_creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d')
                pcs = gdf.crs.to_string() if gdf.crs else 'Unknown'
                gcs = gdf.crs.geodetic_crs.to_string() if gdf.crs and gdf.crs.geodetic_crs else 'Unknown'
                file_name_without_extension, _ = os.path.splitext(os.path.basename(file_path))
                file_size_bytes = os.path.getsize(file_path)
                file_SizeMB = file_size_bytes / 1024 / 1024  # Convert bytes to MB

                associated_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(file_name_without_extension)]

                return {
                    'FILE_PROJECTID': '',  # Placeholder for manual entry
                    'FILE_NAME': file_name_without_extension,
                    'FILE_PATH': os.path.dirname(file_path),
                    'FILE_EXTENSION': file_extension,
                    'FILE_SIZE': file_SizeMB,
                    'FILE_DESCRIPTION': "No Description",
                    'FILE_GEOMTYPE': geometry_type,
                    'FILE_FEATURE_COUNT': str(feature_count),
                    'FILE_METHOD': '',  # Placeholder for manual entry
                    'FILE_DATES': file_creation_date,
                    'FILE_COVERAGE': '',  # Placeholder for manual entry
                    'FILE_PCS': pcs,
                    'FILE_GCS': gcs,
                    'FILE_SCALE': '',  # Placeholder for manual entry
                    'FILE_ASSOCIATED': ', '.join(associated_files),
                }
        except rasterio.errors.RasterioError as e:
            print(f"Rasterio error with file {file_path}: {e}")
            return None

        except Exception as e:
            print(f"General error reading {file_path}: {e}")
            return None

    def process_geospatial_metadata(self, directory):
        shp_files, geotiff_files = self.search_geodata_files(directory)
        geospatial_metadata_records = []

        for file_path in shp_files + geotiff_files:
            metadata = self.extract_metadata(file_path, os.path.splitext(file_path)[1])
            if metadata:
                geospatial_metadata_records.append(metadata)

        root = ET.Element("Geospatial_Files")
        for metadata in geospatial_metadata_records:
            file_element = ET.SubElement(root, "File")
            for key, value in metadata.items():
                ET.SubElement(file_element, key).text = str(value)

        return root

    def create_geospatial_metadata(self, metadata_records, root_element_name="Geospatial_Files"):
        root = ET.Element(root_element_name)
        for metadata in metadata_records:
            element = ET.SubElement(root, "File")
            for key, value in metadata.items():
                ET.SubElement(element, key).text = str(value)
        return root

    @staticmethod
    def get_associated_files(file_path):
        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
        folder_path = os.path.dirname(file_path)
        associated_extensions = ['.tfw', '.prj', '.kml', '.shp', '.shx', '.dbf']
        associated_files = [f for f in os.listdir(folder_path) if f.startswith(file_name_without_extension) and f.endswith(tuple(associated_extensions))]
        return associated_files

    @staticmethod
    def search_geodata_files(start_dir):
        total_files = count_files(start_dir, GEOSPATIAL_FILE_TYPES)

        message_root = tk.Tk()
        message_root.title("Processing")
        message_label = tk.Label(message_root, text=f"Searching geospatial files ({total_files} files)... please wait")
        message_label.pack(padx=20, pady=20)
        message_root.update()

        shp_files = []
        geotiff_files = []

        for root, dirs, files in os.walk(start_dir):
            dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith('.zip'):
                    continue
                if any(file.lower().endswith(ext) for ext in GEOSPATIAL_FILE_TYPES):
                    if file.lower().endswith('.shp'):
                        shp_files.append(file_path)
                    elif file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                        geotiff_files.append(file_path)

        message_root.destroy()

        return shp_files, geotiff_files

class FolderLevelMetadataExtractor(BaseMetadataExtractor):
    def extract_folder_metadata(self, folder_path):
        metadata = {}
        folder_name = os.path.basename(folder_path)

        metadata.update({
            'FILE_SUBJECT': '',
            'FILE_ACCURACY': '',
            'FILE_COVERAGE': '',
            'FILE_PCS': '',
            'PROJECT_RELATIONS': '',
            'PROJECT_LANGUAGE': 'English',
            'PROJECT_TYPE': '',
            'PROJECT_FORMAT': '',
        })

        return metadata

    def process_folder_metadata(self, start_dir):
        root = ET.Element("Folder_Level_Metadata")

        for root_dir, dirs, _ in os.walk(start_dir):
            if "3D_Recording" in os.path.basename(root_dir):
                for subfolder in dirs:
                    if not subfolder.endswith('.zip'):
                        folder_path = os.path.join(root_dir, subfolder)
                        metadata = self.extract_folder_metadata(folder_path)

                        folder_element = ET.SubElement(root, "Folder")
                        for key, value in metadata.items():
                            ET.SubElement(folder_element, key).text = str(value)

        return root

class ControlPointMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path):
        metadata = {}
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_directory = os.path.dirname(file_path)

        associated_files = [f for f in os.listdir(file_directory) if f.startswith(file_name)]
        linked_files = ', '.join(associated_files)

        if file_path.endswith(".shp"):
            gdf = gpd.read_file(file_path)
            first_point = gdf.geometry.iloc[0]
            metadata['CONTL_X'] = first_point.x
            metadata['CONTL_Y'] = first_point.y
            metadata['CONTL_Z'] = first_point.z if hasattr(first_point, 'z') else ''

        elif file_path.endswith(".csv"):
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    metadata['CONTL_X'] = row.get('X')
                    metadata['CONTL_Y'] = row.get('Y')
                    metadata['CONTL_Z'] = row.get('Z', '')

        metadata.update({
            'CONTL_CX': '',
            'CONTL_CY': '',
            'CONTL_CZ': '',
            'CONTL_Location': '',
            'FILE_DATES': '',
            'FILE_PROJECTID': '',
            'FILE_COVERAGE': '',
            'FILE_PCS': '',
            'FILE_GCS': '',
            'FILE_LINKED': linked_files
        })

        return metadata

    def process_control_point_metadata(self, start_dir):
        root = ET.Element("Three_Dimensional_Control_Point_Metadata")
        for file_path in search_control_point_files(start_dir):
            metadata = self.extract_metadata(file_path)
            if metadata:
                file_element = ET.SubElement(root, "File")
                for key, value in metadata.items():
                    ET.SubElement(file_element, key).text = str(value)

        return root

class ThreeDimensionalModelMetadataExtractor(BaseMetadataExtractor):
    def extract_metadata(self, file_path):
        metadata = {}
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_directory = os.path.dirname(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)

        metadata.update({
            'FILE_NAME': file_name,
            'FILE_PATH': file_directory,
            'FILE_EXTENSION': os.path.splitext(file_path)[1],
            'FILE_SIZE': f"{file_size:.2f}MB",
            'FILE_VERT': '',
            'FILE_POLY': '',
            'FILE_GEOMTYPE': '',
            'FILE_UNITSCALE': '',
            'FILE_COVERAGE': '',
            'FILE_PCS': '',
            'FILE_GCS': '',
            'FILE_LAYERS': '',
            'FILE_TEXTURES': '',
            'FILE_MATERIAL': '',
            'FILE_LIGHT': '',
            'FILE_TYPE': '',
            'FILE_LOD': '',
        })

        return metadata

    def process_model_metadata(self, start_dir):
        root = ET.Element("Three_Dimensional_Model_Metadata")
        for file_path in search_model_files(start_dir):
            metadata = self.extract_metadata(file_path)
            if metadata:
                file_element = ET.SubElement(root, "File")
                for key, value in metadata.items():
                    ET.SubElement(file_element, key).text = str(value)

        return root
            
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
              f"has been created in the specified directory.\n"\
              f"\n"\
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
    directory, save_directory = get_directory_info_via_gui()  # Make sure this function is called first
    combined_root = ET.Element("CombinedMetadata")

    # Collect all metadata types
    all_metadata_records = []

    # Process Project Level Metadata
    project_metadata = process_project_metadata()
    if project_metadata is not None:
        combined_root.append(project_metadata)

    # Process other metadata types
    image_extractor = ImageMetadataExtractor()
    image_metadata = image_extractor.create_image_metadata(directory)
    if image_metadata is not None:
        all_metadata_records.extend(image_metadata)

    geospatial_extractor = GeospatialMetadataExtractor()
    geospatial_metadata = geospatial_extractor.process_geospatial_metadata(directory)
    if geospatial_metadata is not None:
        all_metadata_records.extend(geospatial_metadata)

    control_point_extractor = ControlPointMetadataExtractor()
    control_point_metadata = control_point_extractor.process_control_point_metadata(directory)
    if control_point_metadata is not None:
        all_metadata_records.extend(control_point_metadata)

    geophysics_extractor = GeophysicsMetadataExtractor()
    geophysics_metadata = geophysics_extractor.process_geophysics_metadata(directory)
    if geophysics_metadata is not None:
        all_metadata_records.extend(geophysics_metadata)

    # Create the folder tree and include all metadata directly within it
    folder_tree_root = create_folder_tree_xml(directory, all_metadata_records)
    combined_root.append(folder_tree_root)

    # Write out the combined XML
    combined_xml_path = os.path.join(directory, 'Combined_Metadata.xml')
    combined_tree = ET.ElementTree(combined_root)
    combined_tree.write(combined_xml_path, encoding='utf-8', xml_declaration=True)

    # Define folder_tree_xml_path for the completion window
    folder_tree_xml_path = os.path.join(directory, 'METADATA_FolderTree.xml')  # Assuming you want to reference the previous folder tree path

    # Total folders processed
    total_folders = count_total_folders(directory)

    # Call the custom completion window function
    show_completion_window(folder_tree_xml_path, combined_xml_path, total_folders, directory)
