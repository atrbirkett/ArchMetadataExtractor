## version 3.2 of the folder structure.

import os
import tkinter as tk
from tkinter import ttk, filedialog

# The directory structure
directory_structure = {
        "3D_Modelling": {
            "PROJECT": {
                "PROJECT_LightingAnalysis": {
                    "LIGHTINGANALYSIS_ResultsData": {
                        "RESULTS_AutumnEquinox": {},
                        "RESULTS_SpringEquinox": {},
                        "RESULTS_SummerSolstice": {},
                        "RESULTS_WinterSolstice": {},
                    },
                    "LIGHTINGANALYSIS_ResultsImages": {
                        "RESULTS_AutumnEquinox": {},
                        "RESULTS_SpringEquinox": {},
                        "RESULTS_SummerSolstice": {},
                        "RESULTS_WinterSolstice": {},
                    },
                    "LIGHTINGANALYSIS_Scenes": {
                        "SCENES_AutumnEquinox": {},
                        "SCENES_SpringEquinox": {},
                        "SCENES_SummerSolstice": {},
                        "SCENES_WinterSolstice": {},
                    },
                },
                "PROJECT_MaterialLibraries": {},
                "PROJECT_SceneAssets": {
                    "ASSETS_Animations": {},
                    "ASSETS_Images": {},
                    "ASSETS_Other": {},
                    "ASSETS_Sounds": {},
                },
                "PROJECT_Scenes": {
                    "PROJECT_BasicModel": {},
                    "PROJECT_TechnicalModel": {},
                },
                "PROJECT_StructuralAnalysis": {
                    "STRUCTURALANALYSIS_Assemblies": {},
                    "STRUCTURALANALYSIS_MaterialProperties": {},
                    "STRUCTURALANALYSIS_Parts": {},
                    "STRUCTURALANALYSIS_Results": {},
                },
            },
        },
        "3D_Recording": {},
        "DATA_Database": {
            "DATABASE_Archive": {},
            "DATABASE_ControlledTerms": {},
            "DATABASE_Records": {},
            "DATABASE_RelationTable": {},
            "DATABASE_SQL": {},
        },
        "DATA_Geodata": {
            "GEODATA_Raster": {
                "RASTER_Orthophotos": {},
                "RASTER_Surface": {},
            },
            "GEODATA_Shapefile": {},
        },
        "DATA_Survey": {
            "SURVEY_FlightLogs": {},
            "SURVEY_Geophysics": {
                "GEOPHYS_Project_Year": {
                    "GEOPHYS_Data": {
                        "DATA_Preservation": {},
                        "DATA_Rasters": {},
                        "DATA_Working": {},
                    },
                    "GEOPHYS_Documents": {
                        "DOCUMENTS_FileTree": {},
                        "DOCUMENTS_Geodata": {},
                        "DOCUMENTS_Metadata": {},
                    },
                    "GEOPHYS_Project": {
                        "PROJECT_Notes": {},
                        "PROJECT_Report": {},
                    },
                },
            },
            "SURVEY_RAWData": {},
        },
        "DOCUMENTS_Records": {
            "RECORDS_ContextSheets": {},
            "RECORDS_Masonry": {},
            "RECORDS_Photoregister": {},
            "RECORDS_Samples": {},
            "RECORDS_Skeleton": {},
            "RECORDS_SpecialFinds": {},
        },
        "DOCUMENTS_Reports": {
            "REPORTS_Dating": {},
            "REPORTS_Excavation": {},
            "REPORTS_Photogrammetry": {},
            "REPORTS_Specialist": {},
            "REPORTS_Survey": {},
        },
        "DRAWINGS_Objects": {
            "DRAWINGS_Catalogues": {},
            "DRAWINGS_Digital": {},
            "DRAWINGS_Scans": {},
        },
        "DRAWINGS_Site": {
            "DRAWINGS_CAD": {},
            "DRAWINGS_Catalogues": {},
            "DRAWINGS_Scans": {},
        },
        "PHOTOGRAPHY": {
            "PHOTOGRAPHY_Objects": {},
            "PHOTOGRAPHY_Photogrammetry": {},
            "PHOTOGRAPHY_Rectified": {},
            "PHOTOGRAPHY_SitePhotos": {
                "YEAR": {},
            },
            "PHOTOGRAPHY_UAV": {},
        }
    }

def create_directory_structure(base_path, directory_structure):
    for directory, subdirectories in directory_structure.items():
        current_path = os.path.join(base_path, directory)
        os.makedirs(current_path, exist_ok=True)
        if subdirectories:
            create_directory_structure(current_path, subdirectories)

def create_project_structure():
    # Get values from entry widgets
    top_level_folder_name = top_level_folder_name_entry.get()

    # Ask the user to select the project location
    project_location = filedialog.askdirectory()
    if not project_location:
        return  # User canceled the selection

    # Create the top-level folder
    top_level_folder = os.path.join(project_location, top_level_folder_name)
    os.makedirs(top_level_folder, exist_ok=True)

    # Create the directory structure
    create_directory_structure(top_level_folder, directory_structure)

    # Display the completion message in a window
    completion_message = f"Project folder structure created successfully under {top_level_folder}"
    result_label.config(text=completion_message)

def close_window():
    root.destroy()

# Create a tkinter window
root = tk.Tk()
root.title("Folder Structure Creator")
root.geometry("400x400")

# Set the style
style = ttk.Style()
style.theme_use('default')  # Or try 'alt', 'default', 'classic', 'vista'
style.configure('TButton', font=('Helvetica', 12), padding=6)
style.configure('TLabel', font=('Helvetica', 12), background='#f0f0f0')
style.configure('TFrame', background='#f0f0f0')

# Create and place labels and entry widgets
top_level_folder_name_label = ttk.Label(root, text="Enter the top-level folder name:")
top_level_folder_name_label.pack(pady=10)
top_level_folder_name_entry = ttk.Entry(root)
top_level_folder_name_entry.pack()

# Create a button to trigger folder structure creation
create_button = ttk.Button(root, text="Create Folder Structure", command=create_project_structure)
create_button.pack(pady=20)

# Create a label to display the completion message
result_label = ttk.Label(root, text="", background='#f0f0f0')
result_label.pack()

# Create a button to close the window
close_button = ttk.Button(root, text="Close", command=close_window)
close_button.pack()

# Start the tkinter main loop
root.mainloop()