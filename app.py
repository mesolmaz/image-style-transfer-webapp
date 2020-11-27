from flask import Flask, render_template, redirect, request, url_for, abort
from werkzeug.utils import secure_filename
import functools
import os
import imghdr

import matplotlib.pylab as plt
from matplotlib import gridspec

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from utils import crop_center, load_image, show_n

output_image_size = 384  # @param {type:"integer"}
content_img_size = (output_image_size, output_image_size)
style_img_size = (256, 256)

# Load TF-Hub module.
hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_module = hub.load(hub_handle)

### Some code was taken from https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images/content'
app.config['STYLE_PATH'] = 'static/images/style'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['img_file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_image(uploaded_file.stream):
                print("file not validated")
                abort(400)
            if os.path.isfile(os.path.join(app.config['UPLOAD_PATH'], 'uploaded_image'+ file_ext)):
                os.remove(os.path.join(app.config['UPLOAD_PATH'], 'uploaded_image'+ file_ext))
            if os.path.isfile(os.path.join(app.config['UPLOAD_PATH'], filename)):
                os.remove(os.path.join(app.config['UPLOAD_PATH'], filename))
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            os.rename(os.path.join(app.config['UPLOAD_PATH'], filename), os.path.join(app.config['UPLOAD_PATH'], 'uploaded_image'+ file_ext))
        return render_template('index.html', filename = os.path.join(app.config['UPLOAD_PATH'], 'uploaded_image'+ file_ext))
    else:
        return render_template('index.html')

@app.route('/styleimage', methods=["GET", "POST"])
def styleimage():
    global imageid
    imageid = request.form.get('imageurl')
    return redirect(url_for('index'))

@app.route('/createart', methods=["GET", "POST"])
def createart():
    global imageid
    content_image = load_image(os.path.join(app.config['UPLOAD_PATH'], 'uploaded_image.jpg'), content_img_size)
    # content_image = load_image(url_for('static', filename='images/content/' + 'uploaded_image.jpg'), content_img_size)
    # style_image = load_image(url_for(imageid), style_img_size)
    style_image = load_image(os.path.join(app.config['STYLE_PATH'], os.path.basename(imageid)), style_img_size)
    style_image = tf.nn.avg_pool(style_image, ksize=[3,3], strides=[1,1], padding='SAME')
    outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
    stylized_image = outputs[0]
    show_n([content_image, style_image, stylized_image], titles=['Original content image', 'Style image', 'Stylized image'])
    return render_template('stylechange.html', styleimage = 'static/images/content/finalimage.jpg')


if __name__ == "__main__":
    app.run(debug=True)
