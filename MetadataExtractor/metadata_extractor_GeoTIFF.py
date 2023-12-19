import os
import rasterio
import xml.etree.ElementTree as ET

def search_geotiff_files(start_dir):
    # Function to recursively search for GeoTIFF files
    def search_geotiff_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.tif') or file.lower().endswith('.tiff'):
                    yield os.path.join(root, file)

    # Function to extract metadata from a GeoTIFF file
    def extract_geotiff_metadata(geotiff_path):
        try:
            with rasterio.open(geotiff_path) as src:
                tags = src.tags()
                file_size_bytes = os.path.getsize(geotiff_path)
                file_size_mb = file_size_bytes / 1048576  # Convert bytes to megabytes
                return {
                    'FILE_NAME': os.path.splitext(os.path.basename(geotiff_path))[0],
                    'FILE_LOCATION': os.path.dirname(geotiff_path),
                    'FILE_EXTENSION': os.path.splitext(geotiff_path)[1],
                    'FILE_DESCRIPTION': tags.get('Description', 'Unknown'),
                    'FILE_KEYWORDS': tags.get('Keywords', 'Unknown'),
                    'FILE_VERSION': tags.get('Version', src.driver),
                    'FILE_SIZE_MB': str(file_size_mb),  # Store file size in MB
                    'FILE_BANDS': str(src.count),
                    'FILE_CELLSIZE': str(src.res),
                    'FILE_COVERAGE': str(src.bounds),
                    'FILE_PCS': src.crs.to_string() if src.crs else 'Unknown',
                    'FILE_GCS': src.crs.to_epsg() if src.crs else 'Unknown',
                }
        except rasterio.errors.RasterioIOError as e:
            print(f"Error reading {geotiff_path}: {e}")
            return None

    # Create an XML root element
    root = ET.Element("GeoTIFFMetadata")

    for geotiff_path in search_geotiff_files(start_dir):
        metadata = extract_geotiff_metadata(geotiff_path)
        if metadata:
            # Create an XML element for each GeoTIFF file
            geotiff_element = ET.SubElement(root, "GeoTIFF")
            for key, value in metadata.items():
                ET.SubElement(geotiff_element, key).text = str(value)

    # Write the XML tree to a file
    xml_output_path = os.path.join(start_dir, 'METADATA_GeoTIFF.xml')
    tree = ET.ElementTree(root)
    tree.write(xml_output_path, encoding='utf-8', xml_declaration=True)

    print(f"The GeoTIFF metadata XML file has been created at: {xml_output_path}")

if __name__ == "__main__":
    start_dir = input("Please enter the directory to search for GeoTIFF files: ")
    search_geotiff_files(start_dir)
