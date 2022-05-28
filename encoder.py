import cv2
import numpy as np
import face_recognition
import os
import pickle

def encode():
    '''
    Although register function in app.py is capable 
    of continuously storing encoding and streaming on website.
    But when we have images directory already with us with their name
    in format "firstName_secondName@Roll.jpeg or png or jpg", we can run this
    function one time and it will calculate and store encoding, names and 
    roll numbers in separate files and save them as well
    '''

    try:
        '''
        In order to remove possible duplicates.
        '''
        os.remove("static/knownEncode")
        os.remove("static/knownNames")
        os.remove("static/knownRolls")
    except OSError as e:
        pass

    path = "static/Train"
    myList = os.listdir(path)
    myList.remove('.DS_Store')

    images = []
    classNames = []
    classRolls = []
    encodeList = []
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}') # read current image
        img = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0] # assuming each registering image contains just one face

        # appending encoding, name and roll in corresponding list
        encodeList.append(encode)
        classNames.append(((os.path.splitext(cl)[0]).split('@')[0]).upper())
        classRolls.append(int((os.path.splitext(cl)[0]).split('@')[1]))
        
    
    with open("static/knownEncode", "wb") as fp:   
        pickle.dump(encodeList, fp)
    
    with open("static/knownNames","wb") as fp:
        pickle.dump(classNames, fp)
    
    with open("static/knownRolls","wb") as fp:
        pickle.dump(classRolls, fp)
    
    
    return 

if __name__ == "__main__":
    encode()
        
        
        
        
    
   



