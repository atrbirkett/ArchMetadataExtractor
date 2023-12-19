import os
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

if __name__ == "__main__":
    directory = input("Enter the directory where you want to save the XML files: ")
    
    # Process project metadata
    process_project_metadata(directory)

    # Process folder tree metadata
    create_folder_tree_xml(directory)
