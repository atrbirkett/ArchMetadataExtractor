
# Import each script as a module
import metadata_project as project
import metadata_extractor_FileTree as file_tree
import metadata_extractor_rasters as rasters
import metadata_extractor_GeoTIFF as geotiff
import metadata_extractor_other as other
import metadata_extractor_shp as shp
def main():
    # Assuming each script has a main function or equivalent
    project_data = project.main()
    file_tree_data = file_tree.main(project_data)
    geotiff_data = geotiff.main(file_tree_data)
    other_data = other.main(geotiff_data)
    rasters_data = rasters.main(other_data)
    shp_data = shp.main(rasters_data)

if __name__ == "__main__":
    main()