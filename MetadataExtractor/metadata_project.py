import csv
import os

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

# Prompt for the directory to save the output CSV file
save_directory = input("Enter the directory where you want to save the CSV file (e.g., C:/Documents/): ")
if not os.path.isdir(save_directory):
    print("Directory does not exist. Creating the directory.")
    os.makedirs(save_directory, exist_ok=True)

# Prompt for the output CSV file name
output_csv_name = input("Enter the output CSV file name (e.g., project_metadata.csv): ")

# Full path for the output CSV file
output_csv_path = os.path.join(save_directory, output_csv_name)

# Get project metadata from the user
project_metadata = get_project_metadata()

# Write the project metadata to a CSV file
with open(output_csv_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=project_metadata.keys())
    writer.writeheader()
    writer.writerow(project_metadata)

print(f"Project metadata has been saved to {output_csv_path}")
