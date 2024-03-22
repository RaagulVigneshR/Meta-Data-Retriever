import tkinter as tk
from tkinter import filedialog, messagebox
import os
import csv
import webbrowser
from PIL import Image
from core.exif import Exif
from core.configs import Config
import folium

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

        # Map display button
        self.open_map_button = tk.Button(self.master, text="Open Map", command=self.open_map, font=('Arial', 12))
        self.open_map_button.pack(pady=5)
        self.open_map_button.config(state=tk.DISABLED)  # Initially disabled

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
        filename = filedialog.askopenfilename(initialdir="D:/8th SEM/ProActive cloud security Threat Mitigation/EXIF HEIST/images", title="Select a File", filetypes=(("All files", "*.*"), ("all files", "*.*")))
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

                # Enable the map button if GPS data is available
                if 'GPSInfo' in exif_data:
                    self.open_map_button.config(state=tk.NORMAL)
                else:
                    self.open_map_button.config(state=tk.DISABLED)

    def open_map(self):
        filename = filedialog.askopenfilename(initialdir="D:/8th SEM/ProActive cloud security Threat Mitigation/EXIF HEIST/images", title="Select a File", filetypes=(("All files", "*.*"), ("all files", "*.*")))
        if filename:
            image_path = filename
            exif = Exif()
            exif_data = exif.extract_data(image_path)
            if 'GPSInfo' in exif_data:
                gps_info = exif_data['GPSInfo']
                if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                    latitude = gps_info['GPSLatitude']
                    longitude = gps_info['GPSLongitude']
                    
                    # Create a map centered at the GPS coordinates
                    map_obj = folium.Map(location=[latitude, longitude], zoom_start=15)

                    # Add a marker for the GPS coordinates
                    folium.Marker(location=[latitude, longitude], popup='Image Location').add_to(map_obj)

                    # Save the map to an HTML file
                    map_file = os.path.splitext(image_path)[0] + "_map.html"
                    map_obj.save(map_file)

                    # Open the map in the default web browser
                    webbrowser.open('file://' + os.path.realpath(map_file))

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

    def quit_app(self):
        self.on_close()

    def on_close(self):
        print("The application has been completed and aborted.")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExifViewerApp(root)
    root.mainloop()
