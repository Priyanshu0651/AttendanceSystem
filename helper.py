import pickle
import os
from encoder import encode

import pandas as pd
import string
  
def remove(string):
    return "".join(string.split())

def encoderCheck():
    encode()
    with open("static/knownEncode", "rb") as fp:
        knownEncode = pickle.load(fp)
    with open("static/knownNames", "rb") as fp:
        knownNames = pickle.load(fp)
    with open("static/knownRolls", "rb") as fp:
        knownRolls = pickle.load(fp)

    print(len(knownEncode))
    print(len(knownNames))
    print(len(knownRolls))



def helper1():
   
    dicti = {}
    root = "static/Train"
    l = []
    for i in os.listdir(root):
        if(i!=".DS_Store"):
            l.append(i)
    for items in l:
        path = os.path.join(root,items)
        firstname = path.split('/')[-1].split('.')[-2].split('@')[-2].split('_')[0]
        lastname = path.split('/')[-1].split('.')[-2].split('@')[-2].split('_')[-1]
        if(firstname!=lastname):
            name = firstname + " " + lastname
        else:
            name = firstname
        
        name = name.upper()
        roll = int(path.split('/')[-1].split('.')[-2].split('@')[-1])
        path = remove(path)
        dicti[roll] = [name, path]
    return dicti

def export_data(q):
    

    dicti = {}
    dicti['name'] = []
    dicti['roll'] = []
    dicti['status'] = []
    dicti['Time'] = []

    for i in q:
        dicti['name'].append(i.name)
        dicti['roll'].append(i.roll)
        dicti['status'].append(i.status)
        if(i.status!= "Present"):
            dicti['Time'].append("N/A")
        else:
            dicti['Time'].append(i.Time)


    print(dicti)
    df = pd.DataFrame.from_dict(dicti)

    df.to_csv("static/attendance.csv")
    # df.to_excel("static/attendance.xlsx")

    return


if __name__ == "__main__":
    # export_data()
    # encoderCheck()
    dicti = helper1()
    for key in dicti:
        print(key,'-',dicti[key])  