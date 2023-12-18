import os
import csv
from PIL import Image
from datetime import datetime

# Prompt for directory to search for image files
start_dir = input("Please enter the directory to search for image files: ")

# Supported image file extensions
image_extensions = ['.tiff', '.tif', '.png', '.jpg']

# Function to recursively search for image files
def search_image_files(directory):
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
        # Extract image metadata
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
            'FILE_BITDEPTH': img.bits,
        }

# List to keep all metadata records
metadata_records = []

# Search for all image files within the directory and subdirectories
for image_path in search_image_files(start_dir):
    # Extract metadata from the image file
    metadata = extract_image_metadata(image_path)
    if metadata:
        metadata_records.append(metadata)

# Convert the list of dictionaries to a list of rows including headers
headers = ['FILE_NAME', 'FILE_PATH', 'FILE_EXTENSION', 'FILE_TITLE', 'FILE_DESCRIPTION', 'FILE_KEYWORDS',
           'FILE_VERSION', 'FILE_SIZE', 'FILE_RESOLUTION', 'FILE_DIMENSIONS', 'FILE_COLOUR', 'FILE_BITDEPTH']
rows = [[record[header] for header in headers] for record in metadata_records]

# Path to the output CSV file
csv_output_path = os.path.join(start_dir, f'image_metadata_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv')

# Write the rows to a CSV file
with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)
    csvwriter.writerows(rows)

print(f"The metadata CSV file has been created at: {csv_output_path}")
