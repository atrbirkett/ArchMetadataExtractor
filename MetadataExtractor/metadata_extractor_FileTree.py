import os
import csv

# Prompt for the directory to create a file tree
start_dir = input("Enter the directory to create a file tree: ")

# Prepare the header for the CSV
headers = ['Folder Name', 'Size (MB)', 'Number of Files']

# Function to get folder size and file count
def get_folder_details(folder_path):
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            if not os.path.islink(file_path):  # Check if it's not a symbolic link
                total_size += os.path.getsize(file_path)
                file_count += 1
    size_mb = total_size / (1024 * 1024)  # Convert bytes to megabytes
    return round(size_mb, 2), file_count  # Round the size to 2 decimal places

# List to keep all folder records
folder_records = []

# Walk through the directory and subdirectories
for root, dirs, files in os.walk(start_dir):
    size_mb, file_count = get_folder_details(root)
    # Calculate folder depth for indentation
    depth = root.replace(start_dir, '').count(os.sep)
    indent = ' ' * 4 * depth
    folder_name = os.path.basename(root) if os.path.basename(root) else os.path.basename(start_dir)
    folder_records.append([indent + folder_name, size_mb, file_count])

# Path to the output CSV file
csv_output_path = os.path.join(start_dir, 'directory_file_tree.csv')

# Write the folder records to a CSV file
with open(csv_output_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)
    csvwriter.writerows(folder_records)

print(f"The file tree has been saved to {csv_output_path}")
