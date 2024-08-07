# GUI interface to create and print labels for snap SMD Boxes
# https://www.printables.com/de/model/139035-snap-smd-boxes
# Created by tecmarek 2024

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk
import os
import subprocess
import json
import re

from label_generator import label_generator

ptouch_print_pattern = re.compile(r"max_pixels=\d+, offset=\d+")
ptouch_print_stderr_pattern = re.compile(r"[\w-]+ found on USB bus \d+, device \d+")

class LabelPrinterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Printer specifics
        self.tag_size = 10 #mm
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        self.label_generator = label_generator(self.tag_size, self.font_path)

        # GUI
        self.title("Label Printer")
        self.geometry("900x420")
        self.resizable(False, False)

        vcmd_num_pos = (self.register(self.validate_positive_number), '%P')
        vcmd_id = (self.register(self.validate_id), '%P')

        # Config File Folder Selection
        self.config_folder_label = tk.Label(self, text="Template Folder:")
        self.config_folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.config_folder_entry = tk.Entry(self, state='readonly', width=40)
        self.config_folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.config_folder_button = tk.Button(self, text="Browse", command=self.select_config_folder)
        self.config_folder_button.grid(row=0, column=2, padx=5, pady=5)

        # Template Selection Label
        self.template_label = tk.Label(self, text="Template:")
        self.template_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        # Template Selection Frame
        template_frame = tk.Frame(self)
        template_frame.grid(row=1, column=1, padx=0, pady=5, sticky="w")

        self.template_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(template_frame, textvariable=self.template_var, state="readonly")
        self.template_dropdown.pack(side=tk.LEFT, padx=5)
        self.template_dropdown.bind("<<ComboboxSelected>>", self.load_template)

        self.reload_button = tk.Button(template_frame, text="Reload", command=self.reload_templates)
        self.reload_button.pack(side=tk.LEFT, padx=5)

        # Label Width Selection Dropdown
        self.label_width_label = tk.Label(self, text="Label Width:")
        self.label_width_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.label_width_var = tk.StringVar()
        self.label_width_dropdown = ttk.Combobox(self, textvariable=self.label_width_var, values=["18mm", "24mm"], state="readonly")
        self.label_width_dropdown.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="w")
        self.label_width_dropdown.current(0)

        # Label Type Selection Dropdown
        self.label_type_label = tk.Label(self, text="Label Type:")
        self.label_type_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.label_type_var = tk.StringVar()
        self.label_type_dropdown = ttk.Combobox(self, textvariable=self.label_type_var, values=["small", "large", "xl"], state="readonly")
        self.label_type_dropdown.grid(row=3, column=1, padx=5, pady=5, columnspan=2, sticky="w")
        self.label_type_dropdown.current(0)

        # Number of Text Boxes Dropdown
        self.num_text_boxes_label = tk.Label(self, text="Text Lines:")
        self.num_text_boxes_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.num_text_boxes_var = tk.IntVar(value=1)
        self.num_text_boxes_dropdown = ttk.Combobox(self, textvariable=self.num_text_boxes_var, values=[1, 2, 3, 4], state="readonly")
        self.num_text_boxes_dropdown.grid(row=4, column=1, padx=5, pady=5, columnspan=2, sticky="w")
        self.num_text_boxes_dropdown.bind("<<ComboboxSelected>>", self.update_text_boxes)

        # ID Entry
        self.id_label = tk.Label(self, text="ID:")
        self.id_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.id_entry = tk.Entry(self, validate="key", validatecommand=vcmd_id)
        self.id_entry.grid(row=5, column=1, padx=5, pady=5, columnspan=2, sticky="w")

        # Text Entries
        self.text_entries = []
        self.text_labels = []
        for i in range(4):
            label = tk.Label(self, text=f"Text {i+1}:")
            label.grid(row=6+i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(self)
            entry.grid(row=6+i, column=1, padx=5, pady=5, columnspan=2, sticky="w")
            self.text_labels.append(label)
            self.text_entries.append(entry)
        
        self.update_text_boxes()  # Update text boxes visibility based on the initial value

        # Font Size Entry
        self.font_size_label = tk.Label(self, text="Font Size:")
        self.font_size_label.grid(row=10, column=0, padx=10, pady=5, sticky="e")
        self.font_size_entry = tk.Entry(self, validate="key", validatecommand=vcmd_num_pos)
        self.font_size_entry.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="w")

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=11, column=0, columnspan=3, pady=10)

        self.print_button = tk.Button(button_frame, text="Print", command=self.print_label)
        self.print_button.pack(side=tk.LEFT, padx=5)

        self.print_cut_button = tk.Button(button_frame, text="Print + Cut", command=self.print_and_cut)
        self.print_cut_button.pack(side=tk.LEFT, padx=5)

        self.check_printer_button = tk.Button(button_frame, text="Check Printer", command=self.check_printer)
        self.check_printer_button.pack(side=tk.LEFT, padx=5)

        self.store_button = tk.Button(button_frame, text="Store", command=self.store_config)
        self.store_button.pack(side=tk.LEFT, padx=5)

        self.preview_button = tk.Button(button_frame, text="Generate Preview", command=self.generate_preview)
        self.preview_button.pack(side=tk.LEFT, padx=5)

        # Preview Image Placeholder
        self.preview_frame = tk.Frame(self, width=350, height=350, relief=tk.SUNKEN)
        self.preview_frame.grid(row=0, column=3, rowspan=12, padx=10, pady=10, sticky="nsew")
        self.preview_frame.grid_propagate(False)  # Prevent frame from resizing to fit content
        self.preview_label = tk.Label(self.preview_frame, text="Preview will be shown here")
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def validate_positive_number(self, P):
        if P.isdigit() and int(P) > 0:
            return True
        elif P == "":  # Allow deletion of all characters
            return True
        else:
            return False
        
    def validate_id(self, P):
        if P.isdigit() and 0 <= int(P) <= 48713:
            return True
        elif P == "":  # Allow deletion of all characters
            return True
        else:
            return False
        
    def all_fields_filled(self):
        if not self.id_entry.get():
            return False
        if not self.font_size_entry.get():
            return False
        for entry in self.text_entries:
            if entry.cget('state') == tk.NORMAL and not entry.get():
                return False
        return True

    def select_config_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.config_folder_entry.config(state='normal')
            self.config_folder_entry.delete(0, tk.END)
            self.config_folder_entry.insert(0, folder)
            self.config_folder_entry.config(state='readonly')
            self.template_var.set('')  # Clear the current selected template entry
            self.update_template_dropdown(folder)

    def update_template_dropdown(self, folder):
        try:
            files = [f for f in os.listdir(folder) if f.endswith('.json')]
            self.template_dropdown['values'] = files
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files in the folder: {e}")

    def reload_templates(self):
        folder = self.config_folder_entry.get()
        if folder:
            self.update_template_dropdown(folder)
        self.load_template()

    def load_template(self, event=None):
        template_name = self.template_var.get()
        folder = self.config_folder_entry.get()
        template_path = os.path.join(folder, template_name)

        # Load config from file
        if os.path.isfile(template_path):
            with open(template_path, 'r') as file:
                config = json.load(file)
                self.label_width_var.set(config.get('label_width', '24mm'))
                self.label_type_var.set(config.get('label_type', 'small'))
                self.num_text_boxes_var.set(config.get('text_lines', 1))
                self.font_size_entry.delete(0, tk.END)
                self.font_size_entry.insert(0, config.get('font_size', ''))
                self.update_text_boxes()
                for i, entry in enumerate(self.text_entries):
                    entry.delete(0, tk.END)
                    if i < len(config.get('text_entries', [])):
                        entry.insert(0, config['text_entries'][i])

        # Set the ID to zero
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, '0')
        # Generate preview
        self.generate_preview()
                

    def store_config(self):
        config = {
            'label_width': self.label_width_var.get(),
            'label_type': self.label_type_var.get(),
            'text_lines': self.num_text_boxes_var.get(),
            'font_size': self.font_size_entry.get(),
            'text_entries': [entry.get() for entry in self.text_entries]
        }
        folder = self.config_folder_entry.get() or os.getcwd()
        file_path = filedialog.asksaveasfilename(defaultextension=".json", initialdir=folder, filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(config, file)
            messagebox.showinfo("Info", "Configuration saved successfully.")

    def update_text_boxes(self, event=None):
        num_boxes = self.num_text_boxes_var.get()
        for i, entry in enumerate(self.text_entries):
            if i < num_boxes:
                entry.config(state=tk.NORMAL)
            else:
                entry.config(state=tk.DISABLED)

    def make_label(self):
        label_width = self.label_width_var.get()
        text_lines = int(self.num_text_boxes_var.get())
        font_size = int(self.font_size_entry.get())
        tag_number = int(self.id_entry.get())
        text = [entry.get() for entry in self.text_entries]

        #print("label_width: " + str(label_width))
        #print("text_lines: " + str(text_lines))
        #print("font_size: " + str(font_size))
        #print("tag_number: " + str(tag_number))
        #print("text" + str(text))

        if self.label_type_var.get() == "small":
            image = self.label_generator.make_small_label(label_width, text_lines, font_size, tag_number, text)
        elif self.label_type_var.get() == "large":
            image = self.label_generator.make_large_label(label_width, True, text_lines, font_size, tag_number, text)
        elif self.label_type_var.get() == "xl":
            image = self.label_generator.make_large_label(label_width, False, text_lines, font_size, tag_number, text)
        
        return image

    def print_label(self):
        # Only print label but dont cut it off the tape
        if not self.all_fields_filled():
            messagebox.showwarning("Warning", "Please fill all active text fields.")
            return
    
        image = self.make_label()
        image.save('temp_label.png')
        try:
            result = subprocess.run(['ptouch-print', '--image', 'temp_label.png', '--chain'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stderr + result.stdout

            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                if not (len(stdout_lines) == 1 and ptouch_print_pattern.match(stdout_lines[0])):
                    self.show_popup(output)
                    return

            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                if not (len(stderr_lines) == 1 and ptouch_print_stderr_pattern.match(stderr_lines[0])):
                    self.show_popup(output)
                    return
                
        except Exception as e:
            self.show_popup(f"Error executing print command: {e}")

        self.id_entry.delete(0, tk.END) # clear id
    

    def print_and_cut(self):
        # Print label and cut it off the tape
        if not self.all_fields_filled():
            messagebox.showwarning("Warning", "Please fill all active text fields.")
            return
        
        image = self.make_label()
        image.save('temp_label.png')
        try:
            result = subprocess.run(['ptouch-print', '--image', 'temp_label.png'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stderr + result.stdout
            
            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                if not (len(stdout_lines) == 1 and ptouch_print_pattern.match(stdout_lines[0])):
                    self.show_popup(output)
                    return

            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                if not (len(stderr_lines) == 1 and ptouch_print_stderr_pattern.match(stderr_lines[0])):
                    self.show_popup(output)
                    return
                                    
        except Exception as e:
            self.show_popup(f"Error executing print command: {e}")

        self.id_entry.delete(0, tk.END) # clear id

    def generate_preview(self):
        # Generate preview of current label
        if not self.all_fields_filled():
            messagebox.showwarning("Warning", "Please fill all active text fields.")
            return
        
        image = self.make_label()
        
        #image = Image.new("RGB", (100, 100), "white")
        img = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=img)
        self.preview_label.image = img
        #self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def check_printer(self):
        try:
            result = subprocess.run(['ptouch-print', '--info'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            printer_status = result.stderr + result.stdout
        except Exception as e:
            printer_status = f"Error checking printer status: {e}"

        # Show the result in a popup window
        self.show_popup(printer_status)

    def show_popup(self, text):
        popup = tk.Toplevel(self)
        popup.title("Printer Status")

        text_label = tk.Text(popup, wrap="word", width=50, height=10)
        text_label.pack(padx=10, pady=(10,0)) # Top padding: 10, Bottom padding: 0
        text_label.insert("1.0", text)
        text_label.config(state="disabled")

        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=4)

if __name__ == "__main__":
    app = LabelPrinterGUI()
    app.mainloop()