"""
Geophysics project folder structure creator
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog


def create_directory_structure(base_path, structure):
    for name, children in structure.items():
        path = os.path.join(base_path, name)
        os.makedirs(path, exist_ok=True)
        if children:
            create_directory_structure(path, children)


def main():
    root = tk.Tk()
    root.title("Geophysics Folder Structure Creator")
    root.geometry("400x320")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")
    style.configure("TFrame", background="#f0f0f0")

    ttk.Label(root, text="Top-level project name:").pack(pady=(10, 0))
    project_name_entry = ttk.Entry(root)
    project_name_entry.pack()

    ttk.Label(root, text="Top-level project year:").pack(pady=(10, 0))
    project_year_entry = ttk.Entry(root)
    project_year_entry.pack()

    ttk.Label(root, text="Survey / site name:").pack(pady=(10, 0))
    survey_name_entry = ttk.Entry(root)
    survey_name_entry.pack()

    ttk.Label(root, text="Survey year:").pack(pady=(10, 0))
    survey_year_entry = ttk.Entry(root)
    survey_year_entry.pack()

    result_label = ttk.Label(root, text="", background="#f0f0f0")

    def on_create():
        project_name = project_name_entry.get().strip()
        project_year = project_year_entry.get().strip()
        survey_name = survey_name_entry.get().strip()
        survey_year = survey_year_entry.get().strip()

        if not all([project_name, project_year, survey_name, survey_year]):
            result_label.config(text="Please fill in all fields.")
            result_label.pack()
            return

        location = filedialog.askdirectory(title="Select project location")
        if not location:
            return

        structure = {
            f"{project_name}_{project_year}": {
                f"{survey_name}_{survey_year}": {
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
            }
        }

        create_directory_structure(location, structure)
        result_label.config(text="Project folder structure created successfully.")
        result_label.pack()

    ttk.Button(root, text="Create Folder Structure", command=on_create).pack(pady=20)
    ttk.Button(root, text="Close", command=root.destroy).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
