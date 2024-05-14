from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import folium
import piexif

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    option = request.form.get('option')
    custom_field = request.form.get('custom_field')
    image = request.files['image']

    # Save the uploaded image temporarily
    image_path = 'temp_image.jpg'
    image.save(image_path)

    # Process the image and get EXIF data
    exif = get_exif_data(image_path)

    # Save custom field to the image
    save_custom_field_to_image(image_path, custom_field)

    # Generate map if GPS data is available
    if 'GPSInfo' in exif:
        gps_info = exif['GPSInfo']
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

    # Delete the temporary image
    os.remove(image_path)

    response_data = {
        'exif': exif,
        'option': option,
        'map_file': map_file if 'map_file' in locals() else None
    }

    return jsonify(response_data)

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            exif = {
                piexif.TAGS[key]: exif_data[key] if isinstance(exif_data[key], str) else exif_data[key][0] for key in exif_data
            }
            return exif
        else:
            return {}
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
        return {}

def save_custom_field_to_image(image_path, custom_field):
    try:
        exif_data = piexif.load(image_path)
        custom_field_bytes = custom_field.encode('utf-8')
        exif_data['0th'][piexif.ImageIFD.CustomField] = custom_field_bytes
        exif_bytes = piexif.dump(exif_data)
        piexif.insert(exif_bytes, image_path)
    except Exception as e:
        print(f"Error saving custom field to image: {e}")

if __name__ == '__main__':
    app.run(debug=True)
