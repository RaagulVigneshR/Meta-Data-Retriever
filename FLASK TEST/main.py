from flask import Flask, render_template, request
import subprocess
import tkinter as tk
from process_images import ExifViewerApp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    option = request.form['option']
    image_path = request.form['image_path']
    if image_path:
        if option == "1":
            root = tk.Tk()
            obj = ExifViewerApp(root)
            root.mainloop()
            # View metadata
            subprocess.run(["python", "process_image.py", "--option", option, "--image_path", image_path])
        elif option == "2":
            # Delete metadata
            subprocess.run(["python", "process_image.py", "--option", option, "--image_path", image_path])
    return "Image processing initiated."

if __name__ == "__main__":
    app.run(debug=True)
