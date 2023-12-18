import os
import csv
from PIL import Image
from datetime import datetime

# Function to recursively search for image files
def search_image_files(directory):
    # Supported image file extensions
    image_extensions = ['.tiff', '.tif', '.png', '.jpg']
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                yield os.path.join(root, file)

# Function to extract metadata from an image file
def extract_image_metadata(image_path):
    file_size_bytes = os.path.getsize(image_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
    file_name, file_extension = os.path.splitext(os.path.basename(image_path))

    with Image.open(image_path) as img:
        # Determine bit depth based on image mode
        if img.mode == 'RGB':
            bit_depth = 24  # 8 bits per channel
        elif img.mode == 'L':
            bit_depth = 8   # 8 bits for grayscale
        else:
            bit_depth = None  # Undefined or varies for other modes

        return {
            'FILE_NAME': file_name,
            'FILE_PATH': image_path,
            'FILE_EXTENSION': file_extension,
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

# Main function to create metadata for image files
def create_image_metadata(start_dir):
    metadata_records = []
    for image_path in search_image_files(start_dir):
        metadata = extract_image_metadata(image_path)
        if metadata:
            metadata_records.append(metadata)

    headers = ['FILE_NAME', 'FILE_PATH', 'FILE_EXTENSION', 'FILE_TITLE', 'FILE_DESCRIPTION', 'FILE_KEYWORDS',
               'FILE_VERSION', 'FILE_SIZE', 'FILE_RESOLUTION', 'FILE_DIMENSIONS', 'FILE_COLOUR', 'FILE_BITDEPTH']
    rows = [[record[header] for header in headers] for record in metadata_records]

    csv_output_path = os.path.join(start_dir, 'METADATA_RasterVector.csv')
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)

    print(f"The metadata CSV file has been created at: {csv_output_path}")

if __name__ == "__main__":
    start_dir = input("Please enter the directory to search for image files: ")
    create_image_metadata(start_dir)
