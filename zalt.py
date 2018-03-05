from enum import Enum

def zfuck(description) :
    print("Error: ", description)
    input("press any key to continue . . . ")
    quit(-1)

class ZFuncImpl :
    def __init__(self, paramList, funcBody) :
        self.paramList = paramList
        self.funcBody = funcBody

    def isBuiltin(self) :
        return False

class ZBuiltinFuncImpl :
    def __init__(self, func) :
        self.func = func

    def isBuiltin(self) :
        return True

class ZObjectKind(Enum) :
    Number = 1
    Id = 2
    List = 3
    Func = 4
    Eval = 5

class ZObject :
    def __init__(self, kind, value) :
        self.kind = kind
        self.value = value

    def isNumber(self) :
        return self.kind == ZObjectKind.Number

    def isIdent(self) :
        return self.kind == ZObjectKind.Id

    def isList(self) :
        return self.kind == ZObjectKind.List

    def isFunc(self) :
        return self.kind == ZObjectKind.Func

    def isEval(self) :
        return self.kind == ZObjectKind.Eval

class ZSymbolTableSector :
    def __init__(self) :
        self.symbols = dict()

    def set(self, name, theObject) :
        self.symbols[name] = theObject

    def query(self, name) :
        return self.symbols.get(name)

class ZSymbolTable :
    def __init__(self) :
        self.sectors = list()
        self.pushNewSector(ZSymbolTableSector())

    def pushNewSector(self, sector) :
        self.sectors.append(sector)

    def popSector(self) :
        if len(self.sectors) == 1 :
            zfuck("internal compiler error")
        self.sectors = self.sectors[0:len(self.sectors)-1]

    def set(self, name, theObject) :
        topSector = self.sectors[len(self.sectors)-1]
        topSector.set(name, theObject)

    def query(self, name) :
        reversedSectors = list(self.sectors)
        reversedSectors.reverse()
        for sector in reversedSectors :
            maybeEntry = sector.query(name)
            if maybeEntry != None :
                return maybeEntry
        return None

globalSymbolTable = ZSymbolTable()

class ZEvaluator :
    def __init__(self) :
        pass

    def evaluate(self, theObject) :
        if theObject.isNumber() :
            return theObject

        elif theObject.isList() :
            return theObject
        
        elif theObject.isIdent() :
            found = globalSymbolTable.query(theObject.value)
            if found is None :
                zfuck("undefined reference to " + theObject.value)
            return found
        
        elif theObject.isEval() :
            maybeList = self.evaluate(theObject.value)
            if not maybeList.isList() :
                zfuck("evaluaing unknown thing")
            theList = maybeList.value
            if len(theList) == 0 :
                zfuck("evaluating empty list")
            maybeFunc = self.evaluate(theList[0])
            if not maybeFunc.isFunc() :
                zfuck("not a function apply")
            funcImpl = maybeFunc.value
            if funcImpl.isBuiltin() :
                return funcImpl.func(theList[1:])
            else :
                return self.simpleCall(funcImpl, theList[1:])

    def simpleCall(self, funcImpl, argList) :
        if len(funcImpl.paramList) != len(argList) :
            zfuck("arguments not appropriate")

        newSector = ZSymbolTableSector()
        for i in range(0, len(argList)) :
            newSector.set(funcImpl.paramList[i], self.evaluate(argList[i]))
        globalSymbolTable.pushNewSector(newSector)
        result = self.evaluate(funcImpl.funcBody)
        globalSymbolTable.popSector()
        return result

evaluator = ZEvaluator()

def stdlibQuitFunc(argList) :
    input("press any key to continue . . . ")
    quit(0)

def stdlibAddFunc(argList) :
    theSum = 0
    for arg in argList :
        evaluatedArg = evaluator.evaluate(arg)
        if not evaluatedArg.isNumber() :
            zfuck("not a number")
        theSum += evaluatedArg.value
    return ZObject(ZObjectKind.Number, theSum)

def stdlibSubFunc(argList) :
    if len(argList) != 2 :
        zfuck("Incorrect arguments for -")
    evaluatedLhs = evaluator.evaluate(argList[0])
    evaluatedRhs = evaluator.evaluate(argList[1])
    if (not evaluatedLhs.isNumber()) or (not evaluatedRhs.isNumber()) :
        zfuck("Incorrect arguments for -")
    theDiff = evaluatedLhs.value - evaluatedRhs.value
    return ZObject(ZObjectKind.Number, theDiff)

def stdlibLtFunc(argList) :
    if len(argList) != 2 :
        zfuck("Incorrect arguments for <")
    evaluatedLhs = evaluator.evaluate(argList[0])
    evaluatedRhs = evaluator.evaluate(argList[1])
    if (not evaluatedLhs.isNumber()) or (not evaluatedRhs.isNumber()) :
        zfuck("Incorrect arguments for <")
    return ZObject(ZObjectKind.Number, evaluatedLhs.value < evaluatedRhs.value)

def stdlibNthElement(argList) :
    if len(argList) != 2 :
        zfuck("Incorrect arguments for []")
    maybeList = evaluator.evaluate(argList[0])
    maybeNumber = evaluator.evaluate(argList[1])
    if (not maybeList.isList()) or (not maybeNumber.isNumber()) :
        zfuck("Incorrect arguments for []")
    if maybeNumber.value >= len(maybeList.value) :
        zfuck("Index out of range")
    return maybeList.value[maybeNumber.value]

def stdlibConcat(argList) :
    if len(argList) < 2:
        zfuck("Incorrect argument count for @@")
    finalList = list()
    for arg in argList :
        evaluatedArg = evaluator.evaluate(arg)
        if not evaluatedArg.isList() :
            zfuck("Incorrect argument for @@ : not a list")
        finalList.extend(evaluatedArg.value)
    return ZObject(ZObjectKind.List, finalList)

def stdlibSlice(argList) :
    if len(argList) != 3 :
        zfuck("Incorrect argument count for [:]")
    maybeList = evaluator.evaluate(argList[0])
    maybeNumberBegin = evaluator.evaluate(argList[1])
    maybeNumberEnd = evaluator.evaluate(argList[2])
    if (not maybeList.isList()) or (not maybeNumberBegin.isNumber()) or (not maybeNumberEnd.isNumber()) :
        zfuck("Incorrect arguments for [:]")
    if (maybeNumberBegin.value < 0) or (maybeNumberBegin.value >= len(maybeList.value)) :
        zfuck("Begin index out of range in [:]")
    elif (maybeNumberEnd.value < 0) or (maybeNumberEnd.value >= len(maybeList.value)) :
        zfuck("End index out of range in [:]")
        
    return ZObject(ZObjectKind.List, maybeList.value[maybeNumberBegin.value:maybeNumberEnd.value])

def stdlibLenOf(argList) :
    if len(argList) != 1 :
        zfuck("Incorrect argument count for <=>")
    maybeList = evaluator.evaluate(argList[0])
    if not maybeList.isList() :
        zfuck("Incorrect argument for <=> : not a list")
    return ZObject(ZObjectKind.Number, len(maybeList.value))

def stdlibIfFunc(argList) :
    if len(argList) != 3 :
        zfuck("Incorrect arguments for if")
    condResult = evaluator.evaluate(argList[0]).value
    if bool(condResult) :
        return evaluator.evaluate(argList[1])
    else :
        return evaluator.evaluate(argList[2])

def stdlibDefun(argList) :
    if len(argList) != 3 :
        zfuck("Incorrect argument count for defun")
    if argList[0].kind != ZObjectKind.Id :
        zfuck("Incorrect arguments[0] for defun : not identifier")
    elif argList[1].kind != ZObjectKind.List :
        zfuck("Incorrect arguments[1] for defun : not paramater list")
    paramList = list()
    for arg in argList[1].value :
        if arg.kind != ZObjectKind.Id :
            zfuck("Incorrect arguments[1][x] for defun : not paramater id")
        paramList.append(arg.value)
    funcObject = ZObject(ZObjectKind.Func, ZFuncImpl(paramList, argList[2]))
    globalSymbolTable.set(argList[0].value, funcObject)
    return funcObject

def stdlibPrintFunc(argList) :
    for arg in argList :
        evaluatedArg = evaluator.evaluate(arg)
        print(evaluatedArg.value, end = " ")
    print("\n");
    return ZObject(ZObjectKind.List, argList)

globalSymbolTable.set("+", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibAddFunc)))
globalSymbolTable.set("-", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibSubFunc)))
globalSymbolTable.set("<", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibLtFunc)))
globalSymbolTable.set("?", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibIfFunc)))
globalSymbolTable.set("[]", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibNthElement)))
globalSymbolTable.set("@@", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibConcat)))
globalSymbolTable.set("[:]", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibSlice)))
globalSymbolTable.set("<=>", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibLenOf)))
globalSymbolTable.set("->", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibDefun)))
globalSymbolTable.set("!", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibPrintFunc)))
globalSymbolTable.set("quit!", ZObject(ZObjectKind.Func, ZBuiltinFuncImpl(stdlibQuitFunc)))

class ZParser :
    IdChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/%?><=[]{}@:!"
    NumChars = "0123456789"
    BlankChars = " \t\v\f\n"
    
    def __init__(self) :
        pass

    def parseSource(self, source) :
        return self.parse(self.prelex(source))[0]

    def prelex(self, source) :
        tokens = list()
        i = 0
        while i < len(source) :
            ch = source[i]
            if ch in self.IdChars :
                s = ""
                while (i < len(source)) and ((ch in self.IdChars) or (ch in self.NumChars)) :
                    s = s + ch
                    i = i + 1
                    if (i < len(source)) :
                        ch = source[i]
                tokens.append(s)

            elif ch in self.NumChars :
                s = ""
                while (i < len(source)) and (ch in self.NumChars) :
                    s += ch
                    i = i + 1
                    if (i < len(source)) :
                        ch = source[i]
                tokens.append(s)

            elif ch == '(' or ch == ')' or ch == '$' :
                tokens.append(ch)
                i = i + 1
            
            elif ch in self.BlankChars :
                i = i + 1

            else :
                zfuck("ill character '" + ch + "'")

        return tokens

    def parse(self, tokens) :
        if len(tokens) == 0 :
            zfuck("empty")

        if tokens[0] == "$" :
            tokens = tokens[1:len(tokens)]
            (evaluated, tokens) = self.parse(tokens)
            return (ZObject(ZObjectKind.Eval, evaluated), tokens)

        elif tokens[0] == "(" :
            return self.parseList(tokens)

        elif tokens[0].isnumeric() :
            return (ZObject(ZObjectKind.Number, int(tokens[0])), tokens[1:len(tokens)])

        else : # identifier
            return (ZObject(ZObjectKind.Id, tokens[0]), tokens[1:len(tokens)])

    def parseList(self, tokens) :
        if len(tokens) == 0 or tokens[0] != "(" :
            zfuck("illformed list")

        tokens = tokens[1:len(tokens)]
        concreteList = list()
        while (len(tokens) != 0) and (tokens[0] != ")") :
            (newElement, tokens) = self.parse(tokens)
            concreteList.append(newElement)

        if len(tokens) == 0 :
            zfuck("unclosed list")
        tokens = tokens[1:len(tokens)]
    
        return (ZObject(ZObjectKind.List, concreteList), tokens)

parser = ZParser()

nth = 0
while True:
    src = input("In[" + str(nth) + "] ~ ")
    AST = parser.parseSource(src)
    print("Out[" + str(nth) + "] => " + str(evaluator.evaluate(AST).value))
    nth = nth + 1
