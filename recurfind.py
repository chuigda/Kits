import os
import os.path

keyword = ""
findPath = ""

def IterateFileSystem(path, method) :
    for parent, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            IterateFileSystem(os.path.join(parent, dirname), method)
        for filename in filenames:
            method(os.path.join(parent, filename))

def FindIdentifier(filename) :
    theFile = open(filename, "r", encoding="UTF-8")
    textLines = theFile.readlines()
    for i in range(0, len(textLines)) :
        line = textLines[i]
        stringPos = line.find(keyword)
        if stringPos != -1 :
            strPrompt = "[" + filename + ":" + str(i) + "]"
            print(strPrompt, line, end="")
            for count in range(0, len(strPrompt) + stringPos + 1):
                print(" ", end="")
            print("^", end="")
            for count in range(0, len(keyword)-1) :
                print("~", end="")
            print("", end="\n")

findPath = input("Input full path $ ")
keyword = input("Input keyword $ ")
IterateFileSystem(findPath, FindIdentifier)
