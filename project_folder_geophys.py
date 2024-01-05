import os
import tkinter as tk
from tkinter import ttk, filedialog

def create_project_structure():
    # Get values from entry widgets
    project_name = project_name_entry.get()
    project_year = project_year_entry.get()
    survey_name = survey_name_entry.get()
    survey_year = survey_year_entry.get()


    # Ask the user to select the project location
    project_location = filedialog.askdirectory()
    if not project_location:
        return  # User canceled the selection

    # Define the project structure
    project_structure = {
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

    # Function to create directories from the nested dictionary
    def create_directories(base_path, structure):
        for key, value in structure.items():
            new_path = os.path.join(base_path, key)
            os.makedirs(new_path, exist_ok=True)
            if isinstance(value, dict):
                create_directories(new_path, value)

    # Create directories based on the project structure
    create_directories(project_location, project_structure)

    # Display the completion message in a window
    completion_message = "Project folder structure created successfully"
    result_label.config(text=completion_message)

def close_window():
    root.destroy()

# Create a tkinter window
root = tk.Tk()
root.title("Folder Structure Creator")
root.geometry("400x300")

# Set the style
style = ttk.Style()
style.theme_use('default')  # Or try 'alt', 'default', 'classic', 'vista'
style.configure('TButton', font=('Helvetica', 12), padding=6)
style.configure('TLabel', font=('Helvetica', 12), background='#f0f0f0')
style.configure('TFrame', background='#f0f0f0')

# Create and place labels and entry widgets
survey_name_label = ttk.Label(root, text="Enter the top-level folder name (i.e. the broader project):")
survey_name_label.pack(pady=10)
survey_name_entry = ttk.Entry(root)
survey_name_entry.pack()

survey_year_label = ttk.Label(root, text="Enter the year of the project:")
survey_year_label.pack()
survey_year_entry = ttk.Entry(root)
survey_year_entry.pack()

project_name_label = ttk.Label(root, text="Enter the site/survey name:")
project_name_label.pack(pady=10)
project_name_entry = ttk.Entry(root)
project_name_entry.pack()

project_year_label = ttk.Label(root, text="Enter the year of the survey:")
project_year_label.pack()
project_year_entry = ttk.Entry(root)
project_year_entry.pack()

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
