import os

def solveFile (fileName) :
    file = open(fileName);
    src = file.read();
    codeLines = src.split("\n");
    file.close();
    for i in range (1, len(codeLines)+1) :
        print("%4d %s"%(i, codeLines[i-1]));

userFile = str(raw_input("$ "));
solveFile(userFile);
