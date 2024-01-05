import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Frame, Scrollbar, Canvas, messagebox, ttk
import webbrowser
import xml.etree.ElementTree as ET

def open_github():
    webbrowser.open_new("https://github.com/atrbirkett/ArchMetadataExtractor")

class XmlEditor:
    def set_style(self):
        style = ttk.Style()
        
        # Configure the default button style
        style.configure('TButton', font=('Helvetica', 10), padding=4, borderwidth=1, relief="solid")
        
        # Configure the larger button style
        style.configure('TLargeButton.TButton', font=('Helvetica', 12), padding=6, borderwidth=1, relief="solid")  # Correct style name

        # Configure the label style
        style.configure('TLabel', font=('Helvetica', 12), background='#f0f0f0')

        # Configure the frame style
        style.configure('TFrame', background='#f0f0f0')

        # Configure the entry style
        style.configure('TEntry', font=('Helvetica', 12), padding=6)

        # Configure the active state for buttons
        style.map('TButton', foreground=[('active', 'blue')], background=[('active', '#e6e6e6')])
        

    def __init__(self, root):
        self.root = root
        self.tree = None
        self.current_index = 0
        self.entries = []
        self.elements_to_edit = []
        
        self.entry_width = 50  # Define the width for Entry widgets, you can adjust this value as needed

        self.set_style()  # Apply the style before creating widgets

        # Configure the root window
        self.root.geometry("600x400")
        self.root.minsize(400, 300)
        self.root.title("ArchMetadataExtractor XML Editor")

        # Title label
        self.title_label = ttk.Label(root, text="ArchMetadataExtractor XML Editor", font=('Helvetica', 16, 'bold'))
        self.title_label.pack(pady=(10, 5))

        # GitHub link
        self.github_link = ttk.Label(root, text="GitHub Repository", font=('Helvetica', 10, 'underline'), 
                                     foreground="blue", cursor="hand2")
        self.github_link.pack(pady=(0, 10))
        self.github_link.bind("<Button-1>", lambda e: open_github())

        # Load XML button with larger style
        self.load_button = ttk.Button(root, text="Load XML", command=self.load_xml, style='TLargeButton.TButton')
        self.load_button.pack(pady=(5, 20))

        # Configure the canvas, scrollbar, and edit_frame for data entry
        self.canvas = Canvas(root, bg='#f0f0f0')
        self.scrollbar = Scrollbar(root, command=self.canvas.yview)
        self.edit_frame = Frame(self.canvas)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.edit_frame, anchor="nw")

        self.edit_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a button frame for navigation buttons and pack it at the bottom
        self.button_frame = Frame(root)
        self.button_frame.pack(side='bottom', fill='x', pady=5)  # Make sure it fills only the x direction and has padding

        # Smaller navigation buttons within button_frame
        self.prev_button = ttk.Button(self.button_frame, text="Previous", command=self.prev_element, style='TButton')
        self.prev_button.pack(side='left', padx=10)

        self.save_button = ttk.Button(self.button_frame, text="Save Changes", command=self.save_changes, style='TButton')
        self.save_button.pack(side='left', padx=10)

        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.next_element, style='TButton')
        self.next_button.pack(side='left', padx=10)

    def load_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            self.tree = ET.parse(file_path)
            self.root_xml = self.tree.getroot()

            # Add 'Project_Level' and all 'File' elements to the edit list
            project_level = self.root_xml.find('Project_Level')
            if project_level:
                self.elements_to_edit.append(project_level)

            files = self.root_xml.findall('.//File')
            self.elements_to_edit.extend(files)

            self.display_element(self.current_index)

    def display_element(self, index):
        # Clear previous entries
        for widget in self.edit_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        # Display elements with ttk widgets for consistency
        if index < len(self.elements_to_edit):
            element = self.elements_to_edit[index]
            last_entry = None
            for i, sub_element in enumerate(list(element)):
                label = ttk.Label(self.edit_frame, text=sub_element.tag)
                label.grid(row=i, column=0, padx=5, sticky='e')
                entry = ttk.Entry(self.edit_frame, width=self.entry_width)
                if sub_element.text:
                    entry.insert(0, sub_element.text)
                entry.grid(row=i, column=1, padx=5)
                self.entries.append((sub_element, entry))

                # Set focus order and bind tab key
                if last_entry is not None:
                    last_entry.tk_focusNext = lambda: entry
                    entry.bind('<Tab>', lambda e, entry=entry: self.focus_next(entry))
                last_entry = entry

            # Loop back to the first entry on tab from the last entry
            if last_entry is not None and self.entries:
                last_entry.tk_focusNext = lambda: self.entries[0][1]
                self.entries[0][1].bind('<Tab>', lambda e, entry=self.entries[0][1]: self.focus_next(entry))

            self.prev_button.grid(row=0, column=0, padx=5)
            self.save_button.grid(row=0, column=1, padx=5)
            self.next_button.grid(row=0, column=2, padx=5)
            self.prev_button['state'] = 'normal' if index > 0 else 'disabled'

    def focus_next(self, widget):
        widget.tk_focusNext().focus_set()
        return "break"
    
    def save_changes(self):
        for sub_element, entry in self.entries:
            sub_element.text = entry.get()
        # Optionally save the tree after each element is edited
        self.tree.write('edited_metadata.xml')

    def next_element(self):
        self.save_changes()
        self.current_index += 1
        if self.current_index < len(self.elements_to_edit):
            self.display_element(self.current_index)
        else:
            self.end_editing()

    def prev_element(self):
        if self.current_index > 0:
            self.save_changes()
            self.current_index -= 1
            self.display_element(self.current_index)

    def end_editing(self):
        for widget in self.button_frame.winfo_children():
            widget.grid_forget()

# Create the main window
root = tk.Tk()
root.title("XML Editor")
app = XmlEditor(root)
root.mainloop()
