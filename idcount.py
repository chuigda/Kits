# idcount : enumerate identifiers in files.

import os
import os.path

rwordSet = set(["asm", "auto", "bool", "break", "case", "catch", "char", "class",
               "const", "constexpr", "const_cast", "continue", "decltype", "default", "delete",
               "do", "double", "dynamic_cast", "else", "enum", "explicit", "extern", "false",
               "float", "for", "friend",  "goto", "if", "inline", "int", "long", "mutable",
               "namespace", "new", "noexcept", "nullptr", "operator", "private", "protected",
               "public", "register", "reinterpret_cast", "return", "short", "signed", "sizeof",
               "static", "static_assert", "static_cast", "struct", "switch", "template", "this",
               "throw", "true", "try", "typename", "using", "void", "volatile"])

identifierSet = set()

symbolList = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", "=", "[", "]",
              "{", "}", "|", "\\", ":", ";", "\"", "'", ",", ".", "<", ">", "/", "?", "~"]

def IterateFileSystem(path, method) :
    for parent, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            IterateFileSystem(os.path.join(parent, dirname), method)
        for filename in filenames:
            method(os.path.join(parent, filename))

def NoBlockComment(string) :
    commentStart = string.find("/*");
    while not (commentStart == -1) :
        commentEnd = string.find("*/");
        if not (commentEnd == -1) :
            string = string[0:commentStart] + string[commentEnd+2:]
            commentStart = string.find("/*");
        else :
            return ""
    return string

def NoLineComment(string) :
    return string.split("//")[0];

def NoText(string) :
    strList = string.split("\"");
    ret = "";
    i = 0;
    for section in strList :
        if (i % 2) == 0 :
            ret += section
        i = i + 1
    return ret

def ProcessFile(filename) :
    print(filename)
    file = open(filename, "r", encoding="UTF-8")
    text = file.read()
    text = NoBlockComment(text)
    text = NoText(text)

    lines = text.split("\n")
    for line in lines :
        line = line.strip()
        if line and line[0] == "#":
            continue
        line = NoLineComment(line)
        for symbol in symbolList :
            line = line.replace(symbol, " ")
        line = line.strip()

        tokens = line.split(" ")
        for token in tokens :
            if not (token in rwordSet) and len(token) > 3:
                identifierSet.add(token)
    file.close()

print("Path to solve : ", end="$ ")
path = input()
IterateFileSystem(path, ProcessFile)

identifierList = list(identifierSet)
identifierList.sort()

i = 0
for identifier in identifierList :
    print("%-30s"%(identifier), end="")
    i = i + 1
    if i == 3 :
        print("", end='\n')
        i = 0

print("", end='\n')
