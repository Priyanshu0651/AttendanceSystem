import encodings
from flask import Flask, render_template, Response, request, redirect, flash, send_file
import cv2
import os
import numpy as np
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import face_recognition
import pickle
import pytz

from helper import helper1, remove
import shutil


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///attendance.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)

# defining timezone
tz = pytz.timezone('Asia/Kolkata')

global camera


class attendanceRegister(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    roll = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(200), nullable=False, default="Absent")
    Time = db.Column(db.String(200), default=str(
        datetime.now(tz)).split(" ")[-1].split(".")[-2])

    def __repr__(self) -> str:
        return f"{self.name},{self.roll},{self.status},{self.Time}"


def gen_frames():  # generate frame by frame from camera
    while True:
        global camera
        success, frame = camera.read()
        if success:
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                try:
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except:
                    pass
            except Exception as e:
                pass

        else:
            pass


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('Register') == 'Register':
            global camera
            success, frame = camera.read()
            if(success):
                name = request.form['Name']
                roll = request.form['RollNumber']

                print(name)
                print(roll)

                if (len(name)<=0 or len(roll)<=0):
                    flash("Fill in the details before registering!",'error')
                
                else:
                    roll = int(request.form['RollNumber'])
                    name = name.upper() 
                                        
                    with open("static/knownRolls", "rb") as fp:
                        knownRolls = pickle.load(fp)

                    if(roll in knownRolls):
                        # if student with same roll number is already registered
                        flash("Student with same roll number is already registered!",'error')
                        
                    else:
                        temp = name + '@' + str(roll) + '.png'
                        p = os.path.sep.join(['static/Train', temp])
                        p = remove(p)
                        t = remove(temp)

                        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        encode = face_recognition.face_encodings(img)[0]

                        if(len(encode) > 0):
                            cv2.imwrite(p, frame)
                            with open("static/knownEncode", "rb") as fp:
                                knownEncode = pickle.load(fp)
                            with open("static/knownNames", "rb") as fp:
                                knownNames = pickle.load(fp)

                            knownEncode.append(encode)
                            knownNames.append(name)
                            knownRolls.append(roll)
                            with open("static/knownEncode", "wb") as fp:
                                pickle.dump(knownEncode, fp)

                            with open("static/knownNames", "wb") as fp:
                                pickle.dump(knownNames, fp)

                            with open("static/knownRolls", "wb") as fp:
                                pickle.dump(knownRolls, fp)

                            a = attendanceRegister(name=name, roll=roll)
                            db.session.add(a)
                            db.session.commit()
                            flash("You are successfully registered!", 'success')

                        else:
                            # if face has not been detected then len(encoding) = 0
                            flash("Your face has not been detected, kindly focus camera a bit more!", 'error')

    dicti = helper1()
    return render_template('registeration.html', dicti=dicti)



# rsl: registered student list
@app.route('/rsl', methods=['GET', 'POST'])
def rsl():
    dicti = helper1()
    return render_template('rsl.html', dicti=dicti)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/download", methods=["GET", "POST"])
def download():

    q = attendanceRegister.query.all()
    dicti = {}
    dicti['name'] = []
    dicti['roll'] = []
    dicti['status'] = []
    dicti['Time'] = []

    for i in q:
        dicti['name'].append(i.name)
        dicti['roll'].append(i.roll)
        dicti['status'].append(i.status)
        if(i.status != "Present"):
            dicti['Time'].append("N/A")
        else:
            dicti['Time'].append(i.Time)

    print(dicti)
    df = pd.DataFrame.from_dict(dicti)

    df.to_csv("static/attendance.csv")

    return send_file("static/attendance.csv", as_attachment=True)



@app.route('/delete/<int:roll>')
def delete(roll):
    dicti = helper1()
    file_path = dicti[roll][1]

    if os.path.exists(file_path):
        os.remove(file_path)

    with open("static/knownRolls", "rb") as fp:
        knownRolls = pickle.load(fp)

    id = knownRolls.index(roll)

    with open("static/knownEncode", "rb") as fp:
        knownEncode = pickle.load(fp)
    with open("static/knownNames", "rb") as fp:
        knownNames = pickle.load(fp)

    del knownRolls[id]
    del knownNames[id]
    del knownEncode[id]

    with open("static/knownEncode", "wb") as fp:
        pickle.dump(knownEncode, fp)

    with open("static/knownNames", "wb") as fp:
        pickle.dump(knownNames, fp)

    with open("static/knownRolls", "wb") as fp:
        pickle.dump(knownRolls, fp)

    a = attendanceRegister.query.filter_by(roll=roll).first()
    if(a is not None):
        db.session.delete(a)
        db.session.commit()
        queries = attendanceRegister.query.all()

    return redirect("/rsl")


@app.route('/deleteAttendance/<int:roll>')
def deleteattendance(roll):
    a = attendanceRegister.query.filter_by(roll=roll).first()
    if(a.status == "Absent"):
        flash('Attendance is already marked absent!', 'error')
        return redirect("/attendance")
    else:
        a.status = "Absent"
        flash('Attendance has been successfully marked absent!', 'success')
        db.session.add(a)
        db.session.commit()
        queries = attendanceRegister.query.all()
        return redirect("/attendance")




def do(p):
    curImg = p  # cv2.imread(p)
    imgS = cv2.resize(curImg, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    # img = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
    # testEncode = face_recognition.face_encodings(img)[0]
    with open("static/knownEncode", "rb") as fp:
        knownEncode = pickle.load(fp)
    with open("static/knownNames", "rb") as fp:
        knownNames = pickle.load(fp)
    with open("static/knownRolls", "rb") as fp:
        knownRolls = pickle.load(fp)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(knownEncode, encodeFace)
        faceDis = face_recognition.face_distance(knownEncode, encodeFace)

        matchIndex = np.argmin(faceDis)

        if (matchIndex < len(matches) and matches[matchIndex]):
            name = knownNames[matchIndex].upper()
            roll = knownRolls[matchIndex]
            a = attendanceRegister.query.filter_by(
                name=name, roll=roll).first()
            a.status = "Present"
            flash('You have successfully marked attendance!','success')
            a.Time = str(datetime.now(tz)).split(" ")[-1].split(".")[-2]
            db.session.add(a)
            db.session.commit()
            queries = attendanceRegister.query.all()
        
        else:
            flash('This student is not registered!', 'error')

    return


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    global camera
    if request.method == 'POST':
        if request.form.get('Submit') == 'Submit':
            success, frame = camera.read()
            if(success):
                do(frame)

    queries = attendanceRegister.query.all()
    return render_template('attendance.html', queries=queries)



if __name__ == '__main__':
    camera = cv2.VideoCapture(0)
    app.run(debug=True, port=8000)
