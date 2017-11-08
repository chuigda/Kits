# nocomment : remove comments in C/C++ source files.

def NoBlockComment(str0) :
    str1 = str0.replace("/*", "@Simple#*#Cs@");
    str2 = str1.replace("*/", "@Simple#*#Cs@");

    blocks = str2.split("@Simple#*#Cs@");

    ret = ""
    i = 0;
    for block in blocks:
        if i%2 == 0 :
            ret = ret + block
        i = i + 1
    return ret;


def NoLineComment(str0) :
    lines = str0.split("\n");
    ret = ""
    for line in lines:
        parts = line.split("//");
        if parts[0].strip() != "" :
            ret = ret + parts[0] + "\n";
        elif len(parts) >= 2 :
            ret = ret + "\n";
    return ret;


def ProcessFile(fileName) :
    fileObject = open(fileName);
    code = fileObject.read();
    fileObject.close();

    return NoLineComment(NoBlockComment(code));

fileName = input("Input filename $ ");
print(ProcessFile(fileName));
