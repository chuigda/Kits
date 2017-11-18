import os

def solveFile (fileName) :
    file = open(fileName);
    src = file.read();
    codeLines = src.split("\n");
    file.close();
    for i in range (1, len(codeLines)+1) :
        if i >= 10000 :
            print("%s %s"%(str(i-10000).zfill(4), codeLines[i-1]));
        else :
            print("%s %s"%(str(i).zfill(4), codeLines[i-1]));

userFile = str(input("$ "));
solveFile(userFile);

