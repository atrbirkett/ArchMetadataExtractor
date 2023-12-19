import os
import xml.etree.ElementTree as ET

# Function to prompt for file metadata and return it as a dictionary
def get_file_metadata(file_path):
    file_name = os.path.basename(file_path)
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes

    # Check if the file name contains "_COMP_" or the file extension is .xcp or .xgd
    if "_COMP_" in file_name.upper() or file_name.lower().endswith(('.xcp', '.xgd')):
        return {
            'FILE_PATH': file_path,
            'FILE_NAME': file_name,
            'FILE_DESCRIPTION': '',  # Placeholder for manual entry 
            'FILE_INSTRUMENT': '',  # Placeholder for manual entry' 
            'FILE_UNITS': '',  # Placeholder for manual entry 
            'FILE_UTM':  '',  # Placeholder for manual entry  
            'FILE_SURVEY': '',  # Placeholder for manual entry  
            'FILE_NORTHWEST': '',  # Placeholder for manual entry  
            'FILE_SOUTHEAST': '',  # Placeholder for manual entry  
            'FILE_COMMENTS': '',  # Placeholder for manual entry  
            'FILE_FIRSTTRAVDIR': '',  # Placeholder for manual entry  
            'FILE_COLLECTIONMETHOD': '',  # Placeholder for manual entry  
            'FILE_SENSORS': '',  # Placeholder for manual entry  
            'FILE_DUMMY': '',  # Placeholder for manual entry  
            'FILE_READINGSIZE': '',  # Placeholder for manual entry  
            'FILE_SURVEYSIZE': '',  # Placeholder for manual entry  
            'FILE_GRIDSIZE': '',  # Placeholder for manual entry  
            'FILE_XINT': '',  # Placeholder for manual entry  
            'FILE_YINT': '',  # Placeholder for manual entry  
            'FILE_SIZE': f"{file_size_mb:.2f} MB",  # Include file size in MB
        }

    # Default metadata for non-compressed files
    return None

# Create an XML root element for file metadata
root = ET.Element("FileMetadata")

# Prompt for the directory to search for files
start_dir = input("Enter the directory to search for files: ")

# Iterate through files in the directory
for root_dir, _, files in os.walk(start_dir):
    for file in files:
        file_path = os.path.join(root_dir, file)
        file_metadata = get_file_metadata(file_path)

        # Add file metadata to the XML tree if the conditions are met
        if file_metadata:
            file_element = ET.SubElement(root, "File")
            for key, value in file_metadata.items():
                ET.SubElement(file_element, key).text = value

# Prompt for the directory to save the output XML file
save_directory = input("Enter the directory where you want to save the XML file (e.g., C:/Documents/): ")
if not os.path.isdir(save_directory):
    print("Directory does not exist. Creating the directory.")
    os.makedirs(save_directory, exist_ok=True)

# Prompt for the output XML file name
output_xml_name = input("Enter the output XML file name (e.g., file_metadata.xml): ")

# Full path for the output XML file
output_xml_path = os.path.join(save_directory, output_xml_name)

# Write the XML tree to the output XML file
tree = ET.ElementTree(root)
tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)

print(f"File metadata has been saved to {output_xml_path}")
