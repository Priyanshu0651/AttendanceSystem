import pickle
import os
import string
  
def remove(string):
    '''
    removes all the spaces from a string
    '''
    return "".join(string.split())



def helper1():

   '''
    from Train folder it gets images of registered students,
    and from name of images it extracts roll number and name
    of students and 
    then it maps roll number to name and absolute path of those images
    and return a dictionary which will be further used to display 
    images of students on website.

   '''
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

if __name__ == "__main__":
    dicti = helper1()
    for key in dicti:
        print(key,'-',dicti[key])  