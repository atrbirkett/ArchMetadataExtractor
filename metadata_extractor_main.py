import os
import tkinter as tk
from tkinter import filedialog, simpledialog, Label, Text, Entry, Tk, Button, Frame, Scrollbar, Canvas
from tkinter.simpledialog import askstring
from PIL import Image
from numpy import rad2deg
import rasterio
import geopandas as gpd
from datetime import datetime
import xml.etree.ElementTree as ET
import sys 

##################
##################
######
###### Directory Info
######
##################
##################

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
    root.geometry("700x500")  # Set initial size

    main_frame = Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = Canvas(main_frame)
    scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    entries = {}
    for field in fields:
        Label(scrollable_frame, text=field).pack(anchor="w")
        text_widget = Text(scrollable_frame, height=3, width=80)
        text_widget.pack(pady=5)
        text_widget.bind("<Tab>", focus_next_widget)
        entries[field] = text_widget

    Button(root, text='OK', command=on_ok).pack(pady=10)

    root.mainloop()
    return project_metadata


def process_project_metadata():
    project_metadata = get_project_metadata()
    root = ET.Element("Project_Level")
    for key, value in project_metadata.items():
        ET.SubElement(root, key).text = value
        
    return root  # Return the root element instead of writing to a file

def get_folder_size_and_file_count(folder_path):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.islink(file_path):  # Skip symbolic links
                total_size += os.path.getsize(file_path)
                file_count += 1
    SizeMB = total_size / (1024 * 1024)  # Convert bytes to megabytes
    return round(SizeMB, 2), file_count  # Round to 2 decimal places

def create_folder_element(folder_path, parent_xml_element):
    folder_name = os.path.basename(folder_path)
    folder_size, file_count = get_folder_size_and_file_count(folder_path)
    folder_size_str = str(folder_size) if folder_size is not None else "0"
    file_count_str = str(file_count) if file_count is not None else "0"

    folder_element = ET.SubElement(parent_xml_element, 'FOLDER', {
        'Name': folder_name,
        'Size_MB': folder_size_str,
        'File_Count': file_count_str
    })

    for item in os.listdir(folder_path):
        item_full_path = os.path.join(folder_path, item)
        if os.path.isdir(item_full_path):
            create_folder_element(item_full_path, folder_element)
        else:
            file_element = ET.SubElement(folder_element, 'FILE', {'Name': item})
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
    SizeMB = total_size / (1024 * 1024)  # Convert bytes to megabytes
    return round(SizeMB, 2), file_count  # Round to 2 decimal places

def create_folder_element(folder_path, parent_xml_element):
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
            create_folder_element(item_full_path, folder_element)
        else:
            file_element = ET.SubElement(folder_element, 'FILE', {'Name': item})
            # Optionally, add file details here

def create_folder_tree_xml(start_dir):
    root = ET.Element('Folder_Tree')
    create_folder_element(start_dir, root)
    return root

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
    file_SizeMB = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
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
            'Name': os.path.splitext(file_name)[0],  # File name without extension
            'Path': file_path,                    
            'Title': '',  # Placeholder for manual entry
            'Description': '',  # Placeholder for manual entry
            'Keywords': '',  # Placeholder for manual entry
            'File_Version': img.format_version if hasattr(img, 'format_version') else '',
            'Size_MB': f"{file_SizeMB:.2f}MB",
            'Resolution': img.info.get('dpi', ())[0] if 'dpi' in img.info else '',
            'Dimensions': f"{img.width} x {img.height}px",
            'Colour': 'RGB' if img.mode == 'RGB' else 'grayscale' if img.mode == 'L' else img.mode,
            'Bit_Depth': bit_depth,
        }
        return metadata

# Main function to create metadata for image files and save as XML
def create_image_metadata(start_dir):
    metadata_records = []
    root = ET.Element("Raster_And_Vector_File_Metadata")

    for file_path in search_image_files(start_dir):
        metadata = extract_image_metadata(file_path)
        if metadata:
            metadata_records.append(metadata)

    for metadata in metadata_records:
        image_element = ET.SubElement(root, "File")
        for key, value in metadata.items():
            ET.SubElement(image_element, key).text = str(value)

    return root

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
                file_SizeMB = file_size_bytes / 1048576  # Convert bytes to megabytes
                return {
                    'Path': file_path,                    
                    'Name': os.path.splitext(os.path.basename(file_path))[0],
                    'Location': os.path.dirname(file_path),
                    'Extension': os.path.splitext(file_path)[1],
                    'Description': tags.get('Description', 'Unknown'),
                    'Keywords': tags.get('Keywords', 'Unknown'),
                    'Version': tags.get('Version', src.driver),
                    'Size_MB': str(file_SizeMB),  # Store file size in MB
                    'Bands': str(src.count),
                    'Cell_Size': str(src.res),
                    'Coverage': str(src.bounds),
                    'PCS': src.crs.to_string() if src.crs else 'Unknown',
                    'GCS': src.crs.to_epsg() if src.crs else 'Unknown',
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
            associated_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(file_name_without_extension)]
            data_description = "No Description"

            return {
                'Project_ID': '',  # Placeholder for manual entry
                'Name': file_name_without_extension,
                'Path': os.path.dirname(file_path),
                'Extension': file_extension,
                'Size_MB': file_SizeMB,  # File size in MB
                'Description': data_description,
                'TYPE': geometry_type,
                'Feature_Count': str(feature_count),
                'Method': '',  # Placeholder for manual entry
                'Dates': file_creation_date,
                'Coverage': '',  # Placeholder for manual entry
                'PCS': pcs,
                'GCS': gcs,
                'Scale': '',  # Placeholder for manual entry
                'Associated_Files': ', '.join(associated_files),
            }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def create_Geospatial_metadata(metadata_records, output_path, root_element_name):
    root = ET.Element(root_element_name)

    # Filter out None values from metadata_records
    metadata_records = [metadata for metadata in metadata_records if metadata is not None]

    for metadata in metadata_records:
        element = ET.SubElement(root, "File")
        for key, value in metadata.items():
            ET.SubElement(element, key).text = str(value)

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    if metadata_records:
        print(f"The metadata XML file has been created at: {output_path}")
    else:
        print("No supported files found for XML creation.")

def process_geospatial_metadata(directory):
    shp_files, geotiff_files = search_files(directory)
    geospatial_metadata_records = []
    for file_path in shp_files:
        metadata = extract_metadata(file_path, '.shp')
        if metadata:
            geospatial_metadata_records.append(metadata)
    for file_path in geotiff_files:
        metadata = extract_metadata(file_path, '.tif')
        if metadata:
            geospatial_metadata_records.append(metadata)
    
    # Create XML root element for geospatial metadata and return it
    geospatial_root = ET.Element("Geospatial_Files")
    for metadata in geospatial_metadata_records:
        element = ET.SubElement(geospatial_root, "File")
        for key, value in metadata.items():
            ET.SubElement(element, key).text = str(value)
    return geospatial_root

##################
##################
######
####### Other Metadata
######
##################
##################

# Define extract_csv_metadata function
def extract_file_metadata(file_path, file_name):
    file_stats = os.stat(file_path)
    creation_date = datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    modification_date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    file_SizeMB = file_stats.st_size / (1024 * 1024)
    file_extension = os.path.splitext(file_name)[1]

    return {
        'Path': file_path,                    
        'Name': os.path.splitext(file_name)[0],
        'Extension': file_extension,
        'Size_MB': f"{file_SizeMB:.2f}",
        'Format': '',  # Placeholder for file format extraction
        'Software': '',  # Placeholder for software extraction
        'Hardware': '',  # Placeholder for hardware extraction
        'Operating_System': '',  # Placeholder for operating system extraction
        'Date_Created': creation_date,
        'Date_Updated': modification_date,
        'Associated_Files': '',  # Placeholder for linked files
        'Dates': '',  # Placeholder for linked files,
        'File_Identifier': '',  # Placeholder for identifier extraction
        'Creators': '',  # Placeholder for creators extraction
    }

# Function to extract metadata from a .csv file with "_G_" in the name
def extract_csv_metadata(file_path, file_name):
    file_stats = os.stat(file_path)
    creation_date = datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    modification_date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    file_SizeMB = file_stats.st_size / (1024 * 1024)

    if "_G_" in file_name:
        # Update variables with specific metadata for these files
        file_SizeMB = os.path.getsize(file_path) / (1024 * 1024)  # Calculate file size in MB
        # Extract file creation date (you need to replace this with your logic)
        file_creation_date = "YYYY-MM-DD"  # Replace with your extraction logic
    
        return {
        'Project_ID': '',  # Placeholder for manual entry
        'Name': os.path.splitext(file_name)[0],
        'Path': os.path.dirname(file_path),
        'Extension': os.path.splitext(file_name)[1],
        'Size_MB': f"{file_SizeMB:.2f}",
        'Description': '',  # Placeholder for manual entry
        'Type': 'Point',  # Placeholder for manual entry
        'Feature_Count': '',  # Placeholder for manual entry
        'Method': '',  # Placeholder for manual entry
        'Date_Created': creation_date,
        'Date_Updated': modification_date,
        'Dates': '',  # Placeholder for manual entry,
        'Coverage': '',  # Placeholder for manual entry
        'PCS': '',  # Placeholder for manual entry
        'GCS': '',  # Placeholder for manual entry
        'Scale': '',  # Placeholder for manual entry
        'Associated_Files': '',  # Placeholder for manual entry
    }

# Define search_other_files function
def search_other_files(directory, extensions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                yield os.path.join(root, file), file

def search_other_files(directory, extensions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                yield os.path.join(root, file), file

def process_other_metadata(start_dir):
    root = ET.Element("Other_Files_Metadata")

    for path, name in search_other_files(start_dir, ['.txt', '.pdf', '.csv', '.dwg', '.dxf']):
        if name.lower().endswith('.csv') and "_G_" in name:
            metadata = extract_csv_metadata(path, name)
        else:
            metadata = extract_file_metadata(path, name)
        if metadata:
            file_element = ET.SubElement(root, "File")
            for key, value in metadata.items():
                ET.SubElement(file_element, key).text = str(value)

    return root

##################
##################
######
####### Geophysics Metadata
######
##################
##################

# Function to prompt for file metadata and return it as a dictionary
def get_file_metadata(file_path):
    file_name = os.path.basename(file_path)
    file_size_bytes = os.path.getsize(file_path)
    file_SizeMB = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes

    # Check if the file name contains "_COMP_" or the file extension is .xcp or .xgd
    if "_COMP_" in file_name.upper() or file_name.lower().endswith(('.xcp', '.xgd')):
        return {
            'Path': file_path,
            'Name': file_name,
            'Description': '',  # Placeholder for manual entry 
            'Instrument': '',  # Placeholder for manual entry' 
            'Units': '',  # Placeholder for manual entry 
            'Central_Coordinate':  '',  # Placeholder for manual entry  
            'NW_Coordinate': '',  # Placeholder for manual entry  
            'SE_Coordinate': '',  # Placeholder for manual entry  
            'Comments': '',  # Placeholder for manual entry  
            'Direction_of_1st_Traverse': '',  # Placeholder for manual entry  
            'Collection_Method': '',  # Placeholder for manual entry  
            'Sensors': '',  # Placeholder for manual entry  
            'Dummy_Value': '',  # Placeholder for manual entry  
            'Composite_Size': '',  # Placeholder for manual entry  
            'Survey_Size': '',  # Placeholder for manual entry  
            'Grid_Size': '',  # Placeholder for manual entry  
            'X_Interval': '',  # Placeholder for manual entry  
            'Y_Interval': '',  # Placeholder for manual entry  
            'Size_MB': f"{file_SizeMB:.2f}MB",  # Include file size in MB
        }

    # Default metadata for non-compressed files
    return None

def process_geophysics_metadata(start_dir):
    root = ET.Element("Geophysics_Files")

    for root_dir, _, files in os.walk(start_dir):
        for file in files:
            file_path = os.path.join(root_dir, file)
            file_metadata = get_file_metadata(file_path)
            if file_metadata:
                file_element = ET.SubElement(root, "File")
                for key, value in file_metadata.items():
                    ET.SubElement(file_element, key).text = str(value)

    return root

##################
##################
######
####### Process as Main
######
##################
##################

if __name__ == "__main__":
    # Get directory details and location for saving the XML
    directory, save_directory = get_directory_info_via_gui()
    combined_root = ET.Element("CombinedMetadata")
    # Append returned elements from each function to the combined XML
    combined_root.append(process_project_metadata())  
    # combined_root.append(create_folder_tree_xml(directory))  # This line is commented out to exclude the folder tree
    combined_root.append(create_image_metadata(directory))
    combined_root.append(process_geospatial_metadata(directory))
    combined_root.append(process_other_metadata(directory))
    combined_root.append(process_geophysics_metadata(directory))

    combined_tree = ET.ElementTree(combined_root)
    combined_xml_path = os.path.join(directory, 'METADATA.xml')
    combined_tree.write(combined_xml_path, encoding='utf-8', xml_declaration=True)

    print(f"The metadata file has been created at: {combined_xml_path}")

    folder_tree_root = create_folder_tree_xml(directory)
    folder_tree = ET.ElementTree(folder_tree_root)
    folder_tree_xml_path = os.path.join(directory, 'METADATA_FolderTree.xml')
    folder_tree.write(folder_tree_xml_path, encoding='utf-8', xml_declaration=True)
    print(f"Folder tree file has been created at: {folder_tree_xml_path}")