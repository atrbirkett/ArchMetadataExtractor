import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import webbrowser

# Function to open the GitHub page
def open_github():
    webbrowser.open_new("https://github.com/atrbirkett/ArchMetadataExtractor")

# Improved styling
def set_style():
    style = ttk.Style()
    style.theme_use('default')  # Or try 'alt', 'default', 'classic', 'vista'
    style.configure('TButton', font=('Helvetica', 12), padding=6)
    style.configure('TLabel', font=('Helvetica', 12), background='#f0f0f0')
    style.configure('TFrame', background='#f0f0f0')

def launch_edit_xml():
    try:
        subprocess.run(['python', 'metadata_edit.py'], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch metadata_edit.py: {e}")

def launch_metadata_extractor():
    try:
        subprocess.run(['python', 'metadata_extractor_main.py'], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch metadata_extractor_main.py: {e}")
        
def launch_folder_tree():
    try:
        subprocess.run(['python', 'metadata_foldertree.py'], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch metadata_foldertree.py: {e}")

def exit_application():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        sys.exit()

def main():
    root = tk.Tk()
    root.title("ArchMetadataExtractor")
    root.geometry("600x450")
    set_style()

    frame = ttk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def configure_label(event):
        width = event.width
        description_label.config(wraplength=width-10)

    # Title for the software
    title_label = ttk.Label(frame, text="ArchMetadataExtractor", font=('Helvetica', 16, 'bold'), background='#f0f0f0')
    title_label.pack(pady=(10,0), fill=tk.X)

    description_label = ttk.Label(frame, text="A Python tool for archaeologists and researchers, "
                                              "designed to automate the creation of detailed and structured metadata for "
                                              "archaeological projects, ensuring comprehensive documentation and adherence "
                                              "to data management standards.",
                                  background='#f0f0f0', justify="left")
    description_label.pack(pady=10, fill=tk.X)
    description_label.bind('<Configure>', configure_label)  # Bind the configure event to the label

    btn_metadata_extractor = ttk.Button(frame, text="Launch Metadata Extractor", command=launch_metadata_extractor)
    btn_metadata_extractor.pack(pady=10, fill=tk.X)

    btn_edit_xml = ttk.Button(frame, text="Edit an XML Metadata file", command=launch_edit_xml)
    btn_edit_xml.pack(pady=10, fill=tk.X)
    
    btn_folder_tree = ttk.Button(frame, text="Create a Folder Tree file", command=launch_folder_tree)
    btn_folder_tree.pack(pady=10, fill=tk.X)

    btn_exit = ttk.Button(frame, text="Exit", command=exit_application)
    btn_exit.pack(pady=10, fill=tk.X)

        # Link to GitHub
    github_link = ttk.Label(frame, text="For more details, updates, and to report problems, visit the GitHub page.", 
                            font=('Helvetica', 10, 'underline'), foreground="blue", background='#f0f0f0', cursor="hand2")
    github_link.pack(pady=(5,10))
    github_link.bind("<Button-1>", lambda e: open_github())

    root.mainloop()

if __name__ == "__main__":
    main()