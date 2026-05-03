"""
Archaeology project folder structure creator — v3.2
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog

DIRECTORY_STRUCTURE = {
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
    },
}


def create_directory_structure(base_path, structure):
    for name, children in structure.items():
        path = os.path.join(base_path, name)
        os.makedirs(path, exist_ok=True)
        if children:
            create_directory_structure(path, children)


def main():
    root = tk.Tk()
    root.title("Folder Structure Creator")
    root.geometry("400x200")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")
    style.configure("TFrame", background="#f0f0f0")

    ttk.Label(root, text="Enter the top-level folder name:").pack(pady=10)
    name_entry = ttk.Entry(root)
    name_entry.pack()

    result_label = ttk.Label(root, text="", background="#f0f0f0")

    def on_create():
        project_name = name_entry.get().strip()
        if not project_name:
            result_label.config(text="Please enter a folder name.")
            result_label.pack()
            return

        location = filedialog.askdirectory(title="Select project location")
        if not location:
            return

        top_level = os.path.join(location, project_name)
        os.makedirs(top_level, exist_ok=True)
        create_directory_structure(top_level, DIRECTORY_STRUCTURE)
        result_label.config(text=f"Created: {top_level}")
        result_label.pack()

    ttk.Button(root, text="Create Folder Structure", command=on_create).pack(pady=20)
    ttk.Button(root, text="Close", command=root.destroy).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
