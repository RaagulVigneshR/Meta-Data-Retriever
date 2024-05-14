import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import csv
import webbrowser
from PIL import Image, ImageTk
from core.exif import Exif
from core.configs import Config
import folium

class ExifViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EXIF Data Viewer")
        self.master.geometry("600x400")

        self.option_var = tk.StringVar()
        self.option_var.set("1")  # Default option

        # Menu Bar
        self.create_menu_bar()

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Add tabs
        self.tab_view = ttk.Frame(self.notebook)
        self.tab_edit = ttk.Frame(self.notebook)
        self.tab_view.pack(fill=tk.BOTH)
        self.tab_edit.pack(fill=tk.BOTH)
        self.notebook.add(self.tab_view, text='View')
        self.notebook.add(self.tab_edit, text='Edit')

        # View tab
        self.create_view_tab()

        # Edit tab
        self.create_edit_tab()

    def create_menu_bar(self):
        menubar = tk.Menu(self.master)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_metadata)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.master.config(menu=menubar)

    def create_view_tab(self):
        # View tab layout
        view_frame = tk.Frame(self.tab_view)
        view_frame.pack(padx=10, pady=10)

        # Banner
        banner_label = tk.Label(view_frame, text="EXIF Data Viewer", font=('Arial', 16, 'bold'))
        banner_label.pack(pady=10)

        # Option selection
        option_frame = tk.Frame(view_frame)
        option_frame.pack(pady=10)

        tk.Label(option_frame, text="Select an option:", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)

        view_radio = tk.Radiobutton(option_frame, text="View Metadata", variable=self.option_var, value="1", font=('Arial', 12))
        view_radio.grid(row=0, column=1, padx=5, pady=5)

        # File selection
        select_file_button = tk.Button(view_frame, text="Select Image File", command=self.process_image_view, font=('Arial', 12))
        select_file_button.pack(pady=10)

        # Thumbnail preview
        self.thumbnail_label = tk.Label(view_frame)
        self.thumbnail_label.pack()

        # Image information
        self.info_label = tk.Label(view_frame, font=('Arial', 12))
        self.info_label.pack()

        # Metadata display
        metadata_frame = tk.Frame(view_frame)
        metadata_frame.pack(pady=10)

        tk.Label(metadata_frame, text="Metadata:", font=('Arial', 12)).pack()
        self.metadata_text = tk.Text(metadata_frame, width=40, height=10, font=('Arial', 12))
        self.metadata_text.pack()

    def create_edit_tab(self):
        # Edit tab layout
        edit_frame = tk.Frame(self.tab_edit)
        edit_frame.pack(padx=10, pady=10)

        # Banner
        banner_label = tk.Label(edit_frame, text="EXIF Data Editor", font=('Arial', 16, 'bold'))
        banner_label.pack(pady=10)

        # Option selection
        option_frame = tk.Frame(edit_frame)
        option_frame.pack(pady=10)

        tk.Label(option_frame, text="Select an option:", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)

        edit_radio = tk.Radiobutton(option_frame, text="Edit Metadata", variable=self.option_var, value="2", font=('Arial', 12))
        edit_radio.grid(row=0, column=1, padx=5, pady=5)

        # Custom field entry
        self.custom_field_label = tk.Label(edit_frame, text="Custom Field:", font=('Arial', 12))
        self.custom_field_label.pack(pady=5)

        self.custom_field_entry = tk.Entry(edit_frame, font=('Arial', 12))
        self.custom_field_entry.pack(pady=5)

        # File selection
        select_file_button = tk.Button(edit_frame, text="Select Image File", command=self.process_image_edit, font=('Arial', 12))
        select_file_button.pack(pady=10)

        # Metadata display
        metadata_frame = tk.Frame(edit_frame)
        metadata_frame.pack(pady=10)

        tk.Label(metadata_frame, text="Metadata:", font=('Arial', 12)).pack()
        self.metadata_text_edit = tk.Text(metadata_frame, width=40, height=10, font=('Arial', 12))
        self.metadata_text_edit.pack()

        # Save metadata button
        save_button = tk.Button(edit_frame, text="Save Metadata", command=self.save_metadata, font=('Arial', 12))
        save_button.pack(pady=5)

        # Delete metadata button
        delete_button = tk.Button(edit_frame, text="Delete Metadata", command=self.delete_metadata, font=('Arial', 12))
        delete_button.pack(pady=5)

    def process_image_view(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select an Image File", filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.gif"), ("All files", "*.*")))
        if filename:
            self.image_path = filename
            exif = Exif()
            self.exif_data = exif.extract_data(self.image_path)
            if not self.exif_data:
                messagebox.showinfo("Info", f"No EXIF data found in '{self.image_path}'")
                return
            self.display_image_info()
            self.display_thumbnail()
            self.display_metadata_view()

    def display_image_info(self):
        image = Image.open(self.image_path)
        width, height = image.size
        self.info_label.config(text=f"Size: {width}x{height}, Format: {image.format}")

    def display_thumbnail(self):
        image = Image.open(self.image_path)
        image.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(image)
        self.thumbnail_label.config(image=photo)
        self.thumbnail_label.image = photo

    def display_metadata_view(self):
        self.metadata_text.delete(1.0, tk.END)  # Clear previous content
        for key, value in self.exif_data.items():
            self.metadata_text.insert(tk.END, f"{key}: {value}\n")

    def process_image_edit(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select an Image File", filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.gif"), ("All files", "*.*")))
        if filename:
            self.image_path = filename
            exif = Exif()
            self.exif_data = exif.extract_data(self.image_path)
            if not self.exif_data:
                messagebox.showinfo("Info", f"No EXIF data found in '{self.image_path}'")
                return
            self.display_metadata_edit()

    def display_metadata_edit(self):
        self.metadata_text_edit.delete(1.0, tk.END)  # Clear previous content
        for key, value in self.exif_data.items():
            self.metadata_text_edit.insert(tk.END, f"{key}: {value}\n")
        # If CustomField is present, display it for editing
        if 'CustomField' in self.exif_data:
            custom_field_value = self.exif_data['CustomField']
            self.custom_field_entry.delete(0, tk.END)
            self.custom_field_entry.insert(0, custom_field_value.decode('utf-8'))

    def save_metadata(self):
        metadata = self.metadata_text_edit.get(1.0, tk.END)
        custom_field = self.custom_field_entry.get()
        # Update CustomField in the EXIF data
        self.exif_data['CustomField'] = custom_field.encode('utf-8')

        # Save metadata to the image
        exif = Exif()
        exif.save_data(self.image_path, self.exif_data)

        # Save metadata to a CSV file
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if save_path:
            with open(save_path, "w", newline="") as f:
                f.write(metadata)
            messagebox.showinfo("Info", f"Metadata saved to CSV file: {save_path}")

    def delete_metadata(self):
        self.metadata_text_edit.delete(1.0, tk.END)  # Clear metadata text
        self.custom_field_entry.delete(0, tk.END)     # Clear custom field entry
        self.exif_data = {}  # Clear the metadata dictionary
        messagebox.showinfo("Info", "Metadata deleted successfully")

    def quit_app(self):
        self.on_close()

    def on_close(self):
        print("The application has been completed and aborted.")
        self.master.destroy()

    def open_file(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select a File", filetypes=(("All files", "*.*"), ("all files", "*.*")))
        if filename:
            
            pass

    def show_about(self):
        messagebox.showinfo("About", "EXIF Data Viewer v1.0\nDeveloped by Raagul Vignesh")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExifViewerApp(root)
    root.mainloop()
