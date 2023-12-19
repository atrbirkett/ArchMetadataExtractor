import os
from PIL import Image
import xml.etree.ElementTree as ET

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
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
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
            'FILE_NAME': os.path.splitext(file_name)[0],  # File name without extension
            'FILE_PATH': file_path,                    
            'FILE_TITLE': '',  # Placeholder for manual entry
            'FILE_DESCRIPTION': '',  # Placeholder for manual entry
            'FILE_KEYWORDS': '',  # Placeholder for manual entry
            'FILE_VERSION': img.format_version if hasattr(img, 'format_version') else '',
            'FILE_SIZE': f"{file_size_mb:.2f} MB",
            'FILE_RESOLUTION': img.info.get('dpi', ())[0] if 'dpi' in img.info else '',
            'FILE_DIMENSIONS': f"{img.width} x {img.height}px",
            'FILE_COLOUR': 'RGB' if img.mode == 'RGB' else 'grayscale' if img.mode == 'L' else img.mode,
            'FILE_BITDEPTH': bit_depth,
        }
        return metadata

# Main function to create metadata for image files and save as XML
def create_image_metadata(start_dir):
    metadata_records = []
    for file_path in search_image_files(start_dir):
        metadata = extract_image_metadata(file_path)
        if metadata:
            metadata_records.append(metadata)

    # Create an XML root element
    root = ET.Element("ImageMetadata")

    for metadata in metadata_records:
        # Create an XML element for each image
        image_element = ET.SubElement(root, "Image")
        for key, value in metadata.items():
            ET.SubElement(image_element, key).text = str(value)

    # Path to the output XML file
    xml_output_path = os.path.join(start_dir, 'METADATA_Image.xml')

    # Write the XML tree to the output file
    tree = ET.ElementTree(root)
    tree.write(xml_output_path, encoding='utf-8', xml_declaration=True)

    print(f"The metadata XML file has been created at: {xml_output_path}")