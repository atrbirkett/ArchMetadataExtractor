import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

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

def exit_application():
    # Display a confirmation message before exiting
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        sys.exit()

def main():
    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("300x200")

    btn_edit_xml = tk.Button(root, text="Launch EditXML", command=launch_edit_xml)
    btn_edit_xml.pack(pady=10)

    btn_metadata_extractor = tk.Button(root, text="Launch Metadata Extractor", command=launch_metadata_extractor)
    btn_metadata_extractor.pack(pady=10)

    btn_exit = tk.Button(root, text="Exit", command=exit_application)
    btn_exit.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()