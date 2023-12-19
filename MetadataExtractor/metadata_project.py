import os
import xml.etree.ElementTree as ET

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

# Create an XML root element for project metadata
root = ET.Element("ProjectMetadata")

# Get project metadata from the user
project_metadata = get_project_metadata()

# Add project metadata to the XML tree
for key, value in project_metadata.items():
    ET.SubElement(root, key).text = value

# Prompt for the directory to save the output XML file
save_directory = input("Enter the directory where you want to save the XML file (e.g., C:/Documents/): ")
if not os.path.isdir(save_directory):
    print("Directory does not exist. Creating the directory.")
    os.makedirs(save_directory, exist_ok=True)

# Prompt for the output XML file name
output_xml_name = input("Enter the output XML file name (e.g., project_metadata.xml): ")

# Full path for the output XML file
output_xml_path = os.path.join(save_directory, output_xml_name)

# Write the XML tree to the output XML file
tree = ET.ElementTree(root)
tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)

print(f"Project metadata has been saved to {output_xml_path}")
