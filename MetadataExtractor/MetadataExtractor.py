import os
import metadata_project as project
import metadata_extractor_FolderTree as file_tree
import metadata_extractor_RasterVector as rasters
import metadata_extractor_GeoTIFF as geotiff
import metadata_extractor_Other as other
import metadata_extractor_Geospatial as shp

def main():
    # Prompt for the base directory once
    base_directory = input("Enter the base directory for the project: ")
    
    # Check if the directory exists, if not, create it
    if not os.path.isdir(base_directory):
        print("Base directory does not exist. Creating the directory.")
        os.makedirs(base_directory, exist_ok=True)

    # Run project metadata creator
    project_data = project.main(base_directory)

    # For each module, check if we need a new directory or use the base directory
    for module in [file_tree, rasters, geotiff, other, shp]:
        use_new_directory = input(f"Do you want to define a new directory for {module.__name__}? (yes/no): ").lower()
        directory = base_directory
        if use_new_directory == 'yes':
            directory = input(f"Enter the directory for {module.__name__}: ")
            if not os.path.isdir(directory):
                print(f"Directory for {module.__name__} does not exist. Creating the directory.")
                os.makedirs(directory, exist_ok=True)
        # Run the module with the specified directory
        module_data = module.main(directory, project_data)

if __name__ == "__main__":
    main()
