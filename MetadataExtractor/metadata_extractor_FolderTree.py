import os
import xml.etree.ElementTree as ET

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

def create_file_tree_xml(start_dir):
    root = ET.Element('FolderTree')
    create_folder_element(start_dir, root)

    # Write the XML tree to a file
    tree = ET.ElementTree(root)
    xml_output_path = os.path.join(start_dir, 'METADATA_FolderTree.xml')
    tree.write(xml_output_path, encoding='utf-8', xml_declaration=True)

    print(f"XML file tree has been saved to {xml_output_path}")

if __name__ == "__main__":
    start_dir = input("Please enter the directory to create a file tree XML: ")
    create_file_tree_xml(start_dir)
