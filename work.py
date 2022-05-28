import os
lines = []

with open("requirements.txt","r+") as fp:
    for l in fp:
        if("@" not in l):
            lines.append(l)

os.remove("requirements.txt")
my_file = open("requirements.txt", "w")

for l in lines:
    my_file.write(l)