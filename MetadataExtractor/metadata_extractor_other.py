import os
import csv
import datetime

# Prompt for directory to search for files
start_dir = input("Please enter the directory to search for files: ")

# Supported file extensions
file_extensions = ['.txt', '.pdf', '.csv', '.xml', '.dwg', '.dxf']

# Function to recursively search for files
def search_files(directory, extensions):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                yield os.path.join(root, file), file

# Function to extract metadata from a file
def extract_file_metadata(file_path, file_name):
    # Extract the file extension and format
    file_extension = os.path.splitext(file_name)[1]
    file_format = file_extension.strip('.').upper()

    # Get file creation and modification times
    file_stats = os.stat(file_path)
    created = datetime.datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    updated = datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

    # Return the extracted metadata
    return {
        'FILE_NAME': file_name,
        'FILE_EXTENSION': file_extension,
        'FILE_FORMAT': file_format,
        'FILE_LOCATION': file_path,
        'FILE_SOFTWARE': '',  # Placeholder for manual entry
        'FILE_HARDWARE': '',  # Placeholder for manual entry
        'FILE_OPSYS': '',  # Placeholder for manual entry
        'FILE_CREATED': created,
        'FILE_UPDATED': updated,
        'FILE_LINKED': '',  # Placeholder for manual entry
        'FILE_IDENTIFIER': '',  # Placeholder for manual entry
        'FILE_CREATORS': '',  # Placeholder for manual entry
    }

# List to keep all metadata records
metadata_records = []

# Search for all files within the directory and subdirectories
for path, name in search_files(start_dir, file_extensions):
    # Extract metadata from the file
    metadata = extract_file_metadata(path, name)
    metadata_records.append(metadata)

# Check if we found any files
if not metadata_records:
    print("No files found.")
else:
    # Convert the list of dictionaries to a list of rows including headers
    headers = metadata_records[0].keys()
    rows = [list(record.values()) for record in metadata_records]

    # Path to the output CSV file
    csv_output_path = os.path.join(start_dir, 'file_metadata.csv')

    # Write the rows to a CSV file
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)

    print(f"The metadata CSV file has been created at: {csv_output_path}")
