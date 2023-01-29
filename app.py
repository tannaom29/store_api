import torch
from matplotlib import pyplot as plt
import numpy as np
import cv2
from flask import Flask,request, jsonify
import werkzeug
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

model = torch.hub.load('ultralytics/yolov5','custom',path='best.pt', force_reload=True)

app=Flask(__name__)


@app.route('/upload', methods=["POST","GET"])
def upload():
    if(request.method=="POST"):
        
        products = []
        abc=""
        iden=""
        
        imagefile = request.files['image']
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        x = str(datetime.datetime.now())
        filename = "image.jpeg"
        imagefile.save(filename)

        results = model('image.jpeg')
        print(results)

        p_name=results.pandas().xyxy[0]['name']
        conf = results.pandas().xyxy[0]['confidence']


        if(len(p_name)>0 and conf>0.7):
            
            iden = p_name[0]
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate('finalproject-18d82-firebase-adminsdk-d2n4c-e48e696b83.json')
            # Initialize the app with a service account, granting admin privileges
            firebase_admin.initialize_app(cred)

            db = firestore.client()

            collection = f"{iden}"  # object identified by YOLOv5m 

            users_ref = db.collection(f'{collection}')
            docs = users_ref.stream()
            
            for doc in docs:
                dic_details = doc.to_dict()
                dic_name = {'product_name' : f'{doc.id}'}
                dic_details.update(dic_name)
                products.append(dic_details)
                
        else:
            iden="Error"
        abc = {
              "message" : f"{iden}",
              "variants": f"{products}"
        }
        print(abc)
        
        return jsonify(abc)
    

if __name__=="__main__":
    app.run()