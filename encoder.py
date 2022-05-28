import cv2
import numpy as np
import face_recognition
import os
import pickle
# from datetime import datetime



def encode():
    try:
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
        curImg = cv2.imread(f'{path}/{cl}')
        img = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        
        print(type(encode))
        print(os.path.splitext(cl)[0])
        print(encode)
        encodeList.append(encode)
        classNames.append(((os.path.splitext(cl)[0]).split('@')[0]).upper())
        classRolls.append(int((os.path.splitext(cl)[0]).split('@')[1]))
        # classNames.append(os.path.splitext(cl)[0])
    
    with open("static/knownEncode", "wb") as fp:   
        pickle.dump(encodeList, fp)
    
    with open("static/knownNames","wb") as fp:
        pickle.dump(classNames, fp)
    
    with open("static/knownRolls","wb") as fp:
        pickle.dump(classRolls, fp)
    
    print(classNames)
    print(classRolls)
    return 

if __name__ == "__main__":
    encode()
        
        
        
        
    
   



