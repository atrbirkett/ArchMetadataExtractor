import os
import datetime
import xml.etree.ElementTree as ET

# Placeholder for extract_file_metadata function
def extract_file_metadata(file_path, file_name):
    # You can define the logic for extracting metadata from other file types here
    # Return metadata as a dictionary
    return {
        'FILE_PATH': file_path,                    
        'FILE_NAME': file_name,
        'FILE_EXTENSION': os.path.splitext(file_name)[1],
        'FILE_FORMAT': '',  # Placeholder for file format extraction
        'FILE_SOFTWARE': '',  # Placeholder for software extraction
        'FILE_HARDWARE': '',  # Placeholder for hardware extraction
        'FILE_OPSYS': '',  # Placeholder for operating system extraction
        'FILE_CREATED': '',  # Placeholder for creation date extraction
        'FILE_UPDATED': '',  # Placeholder for modification date extraction
        'FILE_LINKED': '',  # Placeholder for linked files
        'FILE_IDENTIFIER': '',  # Placeholder for identifier extraction
        'FILE_CREATORS': '',  # Placeholder for creators extraction
    }

def search_other_files(start_dir):
    # Supported file extensions (excluding .xml)
    file_extensions = ['.txt', '.pdf', '.csv', '.dwg', '.dxf']

    # Function to recursively search for files
    def search_files(directory, extensions):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    yield os.path.join(root, file), file

    # Function to extract metadata from a .csv file with "_G_" in the name
    def extract_csv_metadata(file_path, file_name):
        # Initialize variables
        file_size_mb = 0.0  # Placeholder for file size in MB
        file_creation_date = ""  # Placeholder for file creation date

        # Extract the file extension and format
        file_extension = os.path.splitext(file_name)[1]
        file_format = file_extension.strip('.').upper()

        # Check if the file name contains "_G_" and update variables accordingly
        if "_G_" in file_name:
            # Update variables with specific metadata for these files
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Calculate file size in MB
            # Extract file creation date (you need to replace this with your logic)
            file_creation_date = "YYYY-MM-DD"  # Replace with your extraction logic

        # Create a dictionary with the updated metadata
        return {
            'FILE_PROJECTID': '',  # Placeholder for manual entry
            'FILE_NAME': os.path.splitext(file_name)[0],  # File name without extension
            'FILE_PATH': os.path.dirname(file_path),
            'FILE_EXTENSION': file_extension,
            'FILE_SIZE_MB': file_size_mb,
            'FILE_DESCRIPTION': '',  # Placeholder for manual entry
            'FILE_TYPE': 'Point',  # Placeholder for manual entry
            'FILE_FEATURECOUNT': '',  # Placeholder for manual entry
            'FILE_METHOD': '',  # Placeholder for manual entry
            'FILE_DATES': file_creation_date,
            'FILE_COVERAGE': '',  # Placeholder for manual entry
            'FILE_PCS': '',  # Placeholder for manual entry
            'FILE_GCS': '',  # Placeholder for manual entry
            'FILE_SCALE': '',  # Placeholder for manual entry
            'FILE_RELATED': '',  # Placeholder for manual entry
        }

    # List to keep all metadata records
    metadata_records = []

    # Search for all files within the directory and subdirectories
    for path, name in search_files(start_dir, file_extensions):
        # Extract metadata from the file
        if name.lower().endswith('.csv') and "_G_" in name:
            metadata = extract_csv_metadata(path, name)
        else:
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