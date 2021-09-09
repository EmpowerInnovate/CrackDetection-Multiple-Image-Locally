import numpy as np
import cv2
import glob
from flask import Flask, Response, jsonify, render_template
from flask_restful import Resource, Api, reqparse
import os

app = Flask(__name__)
api = Api(app)

DATA = {
    'places':
        ['rome',
         'london',
         'new york city',
         'los angeles',
         'brisbane',
         'new delhi',
         'beijing',
         'paris',
         'berlin',
         'barcelona']
}

class Places(Resource):
    def get(self):
        # return our data and 200 OK HTTP code
        return {'data': DATA}, 200

    def post(self):
        # parse request arguments
        parser = reqparse.RequestParser()
        parser.add_argument('location', required=True)
        args = parser.parse_args()

        # check if we already have the location in places list
        if args['location'] in DATA['places']:
            # if we do, return 401 bad request
            return {
                'message': f"'{args['location']}' already exists."
            }, 401
        else:
            # otherwise, add the new location to places
            DATA['places'].append(args['location'])
            return {'data': DATA}, 200

    def delete(self):
        # parse request arguments
        parser = reqparse.RequestParser()
        parser.add_argument('location', required=True)
        args = parser.parse_args()

        # check if we have given location in places list
        if args['location'] in DATA['places']:
            # if we do, remove and return data with 200 OK
            DATA['places'].remove(args['location'])
            return {'data': DATA}, 200
        else:
            # if location does not exist in places list return 404 not found
            return {
                'message': f"'{args['location']}' does not exist."
                }, 404

@app.route("/", methods=['GET'])
def identifyCrackInFolder():
    inputFolder = 'static/Input-Set'
    outputFolder = 'static/Output-Set'
    inputPathsData = []
    outputPathsData = []
    files = [f for f in os.listdir('./'+inputFolder) if os.path.isfile(os.path.join('./'+inputFolder, f))]
    for imageName in files:
        optImg = identifyCrack(inputFolder,outputFolder,imageName)
        inputPathsData.append(inputFolder+'/'+imageName)
        outputPathsData.append(outputFolder+'/'+optImg)
    return render_template('crack.html', inputpaths=inputPathsData,  outputPaths=outputPathsData)

        
def identifyCrack(inputFolder,outputFolder, inputImage):
    # read a cracked sample image
    img = cv2.imread(inputFolder +'/'+ inputImage)

    # Convert into gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Image processing ( smoothing )
    # Averaging
    blur = cv2.blur(gray,(3,3))

    # Apply logarithmic transform
    img_log = (np.log(blur+1)/(np.log(1+np.max(blur))))*255

    # Specify the data type
    img_log = np.array(img_log,dtype=np.uint8)

    # Image smoothing: bilateral filter
    bilateral = cv2.bilateralFilter(img_log, 5, 75, 75)

    # Canny Edge Detection
    edges = cv2.Canny(bilateral,100,200)

    # Morphological Closing Operator
    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Create feature detecting method
    # sift = cv2.xfeatures2d.SIFT_create()
    # surf = cv2.xfeatures2d.SURF_create()
    orb = cv2.ORB_create(nfeatures=1500)

    # Make featured Image
    keypoints, descriptors = orb.detectAndCompute(closing, None)
    featuredImg = cv2.drawKeypoints(closing, keypoints, None)

    # Create an output image
    f = inputImage.replace(".","-processed.")
    cv2.imwrite(outputFolder +'/'+ f, featuredImg)
    return f; 


# identifyCrackInFolder('static/Input-Set','static/Output-Set')
api.add_resource(Places, '/places')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5050)))




# def identifyCrack(inputFolder,outputFolder, inputImage):
#     # read a cracked sample image
#     img = cv2.imread(inputFolder +'/'+ inputImage)

#     # Convert into gray scale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Image processing ( smoothing )
#     # Averaging
#     blur = cv2.blur(gray,(3,3))

#     # Apply logarithmic transform
#     img_log = (np.log(blur+1)/(np.log(1+np.max(blur))))*255

#     # Specify the data type
#     img_log = np.array(img_log,dtype=np.uint8)

#     # Image smoothing: bilateral filter
#     bilateral = cv2.bilateralFilter(img_log, 5, 75, 75)

#     # Canny Edge Detection
#     edges = cv2.Canny(bilateral,100,200)

#     # Morphological Closing Operator
#     kernel = np.ones((5,5),np.uint8)
#     closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

#     # Create feature detecting method
#     # sift = cv2.xfeatures2d.SIFT_create()
#     # surf = cv2.xfeatures2d.SURF_create()
#     orb = cv2.ORB_create(nfeatures=1500)

#     # Make featured Image
#     keypoints, descriptors = orb.detectAndCompute(closing, None)
#     featuredImg = cv2.drawKeypoints(closing, keypoints, None)

#     # Create an output image
#     f = inputImage.replace(".","-processed.")
#     cv2.imwrite(outputFolder +'/'+ f, featuredImg)

# def identifyCrackInFolder(inputFolder,outputFolder):
#     files = [f for f in os.listdir('./'+inputFolder) if os.path.isfile(os.path.join('./'+inputFolder, f))]
#     for imageName in files:
#         identifyCrack(inputFolder,outputFolder,imageName)
        
# identifyCrackInFolder('uploads/images/','static/Output-Set')