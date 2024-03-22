import tkinter as tk
from tkinter import filedialog, messagebox
import os
import csv
from PIL import Image
from core.exif import Exif
from core.configs import Config

class ExifViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("EXIF Data Viewer")

        self.option_var = tk.StringVar()
        self.option_var.set("1")  # Default option

        # Banner
        self.banner_label = tk.Label(self.master, text=Config.banner(), font=('Arial', 14))
        self.banner_label.pack(pady=10)

        # Option selection frame
        self.option_frame = tk.Frame(self.master)
        self.option_frame.pack(pady=10)

        tk.Label(self.option_frame, text="Select an option:", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5)

        self.view_radio = tk.Radiobutton(self.option_frame, text="View Metadata", variable=self.option_var, value="1", font=('Arial', 12))
        self.view_radio.grid(row=0, column=1, padx=5, pady=5)

        self.delete_radio = tk.Radiobutton(self.option_frame, text="Delete Metadata", variable=self.option_var, value="2", font=('Arial', 12))
        self.delete_radio.grid(row=0, column=2, padx=5, pady=5)

        # File selection button
        self.select_file_button = tk.Button(self.master, text="Select Image File", command=self.process_image, font=('Arial', 12))
        self.select_file_button.pack(pady=10)

        # Metadata display text widget
        self.metadata_text = tk.Text(self.master, width=40, height=10, font=('Arial', 12))
        self.metadata_text.pack(pady=10)

        # Save metadata button
        self.save_button = tk.Button(self.master, text="Save Metadata", command=self.save_metadata, font=('Arial', 12))
        self.save_button.pack(pady=5)

        # Quit button
        self.quit_button = tk.Button(self.master, text="Quit", command=self.quit_app, font=('Arial', 12))
        self.quit_button.pack(pady=10)

        # Bind closing event of the window
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def process_image(self):
        option = self.option_var.get()
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("All files", "*.*"), ("all files", "*.*")))
        if filename:
            image_path = filename
            exif = Exif()
            exif_data = exif.extract_data(image_path)
            if not exif_data:
                messagebox.showinfo("Info", f"No Exif data found in '{image_path}'")
                return

            if option == "1":
                # View metadata
                self.display_metadata(exif_data)

            elif option == "2":
                # Delete metadata
                new_path = self.remove_metadata(image_path)
                save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
                if save_path:
                    os.rename(new_path, save_path)
                    messagebox.showinfo("Info", f"Image saved without metadata at: {save_path}")

    def display_metadata(self, exif_data):
        self.metadata_text.delete(1.0, tk.END)  # Clear previous content
        for key, value in exif_data.items():
            self.metadata_text.insert(tk.END, f"{key}: {value}\n")

    def save_metadata(self):
        metadata = self.metadata_text.get(1.0, tk.END)
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if save_path:
            with open(save_path, "w", newline="") as f:
                f.write(metadata)
            messagebox.showinfo("Info", f"Metadata saved to CSV file: {save_path}")

    def remove_metadata(self, image_path):
        # Open the image using PIL
        image = Image.open(image_path)
        
        # Create a copy of the image without metadata
        image_without_metadata = Image.new(image.mode, image.size)
        image_without_metadata.putdata(list(image.getdata()))
        
        # Save the image without metadata to a new file
        new_path = os.path.splitext(image_path)[0] + "_without_metadata" + os.path.splitext(image_path)[1]
        image_without_metadata.save(new_path)
        
        return new_path

    def quit_app(self):
        self.on_close()

    def on_close(self):
        print("The application has been completed and aborted.")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExifViewerApp(root)
    root.mainloop()
