import os
import tkinter as tk
from tkinter import filedialog
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

def create_folder_tree_xml(start_dir):
    root = ET.Element('Folder_Tree')
    create_folder_element(start_dir, root)
    return root

def generate_folder_tree():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(title="Select Directory for Folder Tree")
    root.destroy()

    if directory:
        folder_tree_root = create_folder_tree_xml(directory)
        folder_tree = ET.ElementTree(folder_tree_root)
        folder_tree_xml_path = os.path.join(directory, 'METADATA_FolderTree.xml')
        folder_tree.write(folder_tree_xml_path, encoding='utf-8', xml_declaration=True)
        print(f"Folder tree file has been created at: {folder_tree_xml_path}")
    else:
        print("No directory selected, operation cancelled.")

# Example usage:
if __name__ == "__main__":
    generate_folder_tree()
