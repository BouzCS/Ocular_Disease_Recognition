import os
import uuid
import flask
import urllib
from PIL import Image
import pandas as pd
from tensorflow.keras.models import load_model
from flask import Flask , render_template  , request , send_file
from tensorflow.keras.preprocessing.image import load_img , img_to_array
import cv2
import numpy as np
import os

app = Flask(__name__)

image_size=224


model=load_model(r'model(1).h5')


ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = ['normal', 'diabetes', 'glaucoma', 'cataract', 'age_related_macular', 'hypertension', 'pathological_myopia', 'other_abnormalities']


def predict(filename , model):



    image = cv2.imread(filename,cv2.IMREAD_COLOR)
    image = cv2.resize(image,(image_size,image_size))
    name=filename.split("/")[-1]
    cv2.imwrite(os.path.join(r"C:\Users\Dragox.RS\Desktop\Flask-app\static\images" , name), image)
    cv2.waitKey(0)
    result = model.predict(image.reshape(-1,image_size,image_size,3))
    temp = np.argpartition(-result.flatten(), 3)
    result_args = temp[:3]
    

    return result_args, result.flatten()



@app.route('/')
def home():
        return render_template("index.html")

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    target_img = os.path.dirname(os.path.realpath('app.py'))
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                target_img += r"\static\\images"
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename
                print(img)

                ind, prob_result = predict(img_path , model)

                predictions = {
                    "class_result1":classes[ind[0]],
                    "prob_result1":prob_result[ind[0]],
                    "class_result2":classes[ind[1]],
                    "prob_result2":prob_result[ind[1]],
                    "class_result3":classes[ind[2]],
                    "prob_result3":prob_result[ind[2]],
                }



            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index.html' , error = error) 

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                target_img += r"\static\\images"
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                ind, prob_result = predict(img_path , model)
                print(img_path)

                predictions = {
                    "class_result1":classes[ind[0]],
                    "prob_result1":prob_result[ind[0]],
                    "class_result2":classes[ind[1]],
                    "prob_result2":prob_result[ind[1]],
                    "class_result3":classes[ind[2]],
                    "prob_result3":prob_result[ind[2]],
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index.html' , error = error)

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)