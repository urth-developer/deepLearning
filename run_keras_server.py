# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'
# Submita a request via Python:
#	python simple_request.py

# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os
import dbModule as db
from PIL import Image
import flask
import io
from flask_cors import CORS
import base64
# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
# cors = CORS(app, resources={
#   r"/v1/*": {"origin": "*"},
#   r"/api/*": {"origin": "*"},
# })
CORS(app)
model = None
output = None
mlb = None
def load_urth_model():
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
	global model
	global mlb
	model = load_model('./urth.model')
	mlb = pickle.loads(open('./mlb.pickle', "rb").read())

	

def prepare_image(image, target):
	global output
	#image = cv2.imread(image)
	output = imutils.resize(image, width=400)	
	image = cv2.resize(image, target)
	image = image.astype("float") / 255.0
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	# return the processed image
	return image

@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view

	data = {"success": False}
	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":
			print("......")
			print("......")
			if flask.request.form.get("image"):
				imageString = base64.b64decode(flask.request.form['image'])
				#  convert binary data to numpy array
				nparr = np.fromstring(imageString, np.uint8)

				#  let opencv decode image to correct format
				image = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR);
				
				# read the image in PIL format
				#image = flask.request.form["image"]
				# print("image:",image)
				# #image = Image.open(io.BytesIO(image))
				# with open("test.jpg","wb") as fo:
				# 	fo.write(image)
				
				#print('image :',type(image),"image shape :",image.shape)
				# preprocess the image and prepare it for classification
				image = prepare_image(image, target=(96, 96))
				print('image shape :',image.shape)
				# classify the input image and then initialize the list
				# of predictions to return to the client
				print("[INFO] classifying image...")
				proba = model.predict(image)[0]
				idxs = np.argsort(proba)[::-1][:2]
				json = {"prob":float(proba[np.argmax(proba)]),
				"item":mlb.classes_[np.argmax(proba)]}
				print(proba)
				print(mlb.classes_[np.argmax(proba)])
				return flask.jsonify(json)
			print("*********")
			print(flask.request.form) 
	return flask.jsonify({"status" : 500})

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	print(("* Loading Keras model and Flask starting server..."
		"please wait until server has fully started"))
	load_urth_model()
	app.run(host='0.0.0.0',debug = False, threaded = False)