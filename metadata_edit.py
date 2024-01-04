import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Frame, Scrollbar, Canvas
import xml.etree.ElementTree as ET

class XmlEditor:
    def __init__(self, root):
        self.root = root
        self.tree = None
        self.current_index = 0
        self.entries = []
        self.elements_to_edit = []

        # Configure the root window
        self.root.geometry("600x400")
        self.root.minsize(400, 300)

        # UI Setup
        self.load_button = Button(root, text="Load XML", command=self.load_xml)
        self.load_button.pack(pady=5)

        self.canvas = Canvas(root)
        self.scrollbar = Scrollbar(root, command=self.canvas.yview)
        self.edit_frame = Frame(self.canvas)
        self.entry_width = 500

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.edit_frame, anchor="nw")

        self.edit_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.button_frame = Frame(root)
        self.button_frame.pack(pady=5)

        self.save_button = Button(self.button_frame, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=0, column=1, padx=5)

        self.next_button = Button(self.button_frame, text="Next", command=self.next_element)
        self.next_button.grid(row=0, column=2, padx=5)

        self.prev_button = Button(self.button_frame, text="Previous", command=self.prev_element)
        self.prev_button.grid(row=0, column=0, padx=5)

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

        if index < len(self.elements_to_edit):
            element = self.elements_to_edit[index]
            last_entry = None
            for i, sub_element in enumerate(list(element)):
                label = Label(self.edit_frame, text=sub_element.tag)
                label.grid(row=i, column=0, padx=5, sticky='e')
                entry = Entry(self.edit_frame, width=self.entry_width)
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
