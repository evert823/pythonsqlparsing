# 
# August 2021 Evert Jan Karman / evert823 / project to parse SQL using Python
# Class LowLevelLinesParser has the methods to break down the raw input code into comments, string and number literals, words
# and remaining key characters
# 
# From outside, call the ParseLines method with arguments (Lines, ReportFile, InputFileName)
# - Lines = list of strings resulting from yourfile.readlines()
# - ReportFile = an parsing report file object already open for write
# - InputFileName = a filename representing the input file from which the parsed code is coming
# 
# Method ParseLines returns a list of SQLTokens (see common classes)
# 
import re
from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import KeywordList

class LowLevelLinesParser:
    #-----------------------------------------------------------------------------------------------
    def InterpretElement(self, pprevline, pprevcol, pelttype, pcontent):
        MyToken = SQLToken()
        MyToken.originfilename = infile
        MyToken.bline = pprevline
        MyToken.bcol = pprevcol
        MyToken.eline = currentlinenumber
        MyToken.ecol = currentcolumnnumber
        if pelttype == "WORD":
            if pcontent in MyKeywordList.ValidKeyWords:
                MyToken.TokenType = "KEYWORD"
            else:
                MyToken.TokenType = "VARIABLE"
        elif pelttype == "QUOTEDIDENTIFIER":
            MyToken.TokenType = "VARIABLE"
            MyToken.IsQuotedIdentifier = True
        else:
            MyToken.TokenType = pelttype
        MyToken.TokenContent = pcontent
        FoundTokens.append(MyToken)
        if ReportAllElements == True:
            file_allrpt.write(MyToken.CsvLineFromToken() + "\n")
    #-----------------------------------------------------------------------------------------------
    def ReportElement(self, pprevline, pprevcol, pelttype, pcontent):
        file_allrpt.write(infile + "," + str(pprevline) + "," + str(pprevcol) + "," + str(currentlinenumber) + "," + str(currentcolumnnumber) + "," + pelttype + "," + pcontent + "\n")
    #-----------------------------------------------------------------------------------------------
    def EndOfLineReached(self):
        global currentlinenumber
        global currentcolumnnumber
        if currentcolumnnumber > len(Lines[currentlinenumber]) - 1:
            return True
        elif currentcolumnnumber == len(Lines[currentlinenumber]) - 1 and Lines[currentlinenumber][currentcolumnnumber] == "\n":
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def EndOfFileReached(self):
        global currentlinenumber
        global currentcolumnnumber
    
        if currentlinenumber > len(Lines) - 1:
            return True
        elif currentlinenumber == len(Lines) - 1 and self.EndOfLineReached():
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def GoNextNonEmpty(self):
        global currentlinenumber
        global currentcolumnnumber
        while (not self.EndOfFileReached()) and (self.EndOfLineReached() or Lines[currentlinenumber][currentcolumnnumber] in ("\t", " ")):
            currentcolumnnumber += 1
            if self.EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextMultiLineComment(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        MultiLineCommentStarted = False
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        elif currentcolumnnumber > len(Lines[currentlinenumber]) - 2:
            pass
        elif Lines[currentlinenumber][currentcolumnnumber:currentcolumnnumber + 2] == "/*":
            MultiLineCommentStarted = True
            moved = True
        else:
            pass
        
        prevline = currentlinenumber
        prevcol = currentcolumnnumber
    
        while MultiLineCommentStarted == True and not self.EndOfFileReached():
            col = Lines[currentlinenumber][currentcolumnnumber:].find("*/")
            if col == -1:
                currentlinenumber += 1
                currentcolumnnumber = 0
            else:
                currentcolumnnumber = currentcolumnnumber + col + 2
                if self.EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                self.InterpretElement(prevline, prevcol, "MULTILINECOMMENT", "")
                MultiLineCommentStarted = False
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextSingleLineComment(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        elif currentcolumnnumber > len(Lines[currentlinenumber]) - 2:
            pass
        elif Lines[currentlinenumber][currentcolumnnumber:currentcolumnnumber + 2] == "--":
            moved = True
            prevline = currentlinenumber
            prevcol = currentcolumnnumber
            currentlinenumber += 1
            currentcolumnnumber = 0
            self.InterpretElement(prevline, prevcol, "SINGLELINECOMMENT", "")
        else:
            pass
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextStringLiteral(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        StringLiteralStarted = False
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        elif Lines[currentlinenumber][currentcolumnnumber] == "'":
            StringLiteralStarted = True
            moved = True
            prevline = currentlinenumber
            prevcol = currentcolumnnumber
        else:
            pass
    
        if StringLiteralStarted == True:
            currentcolumnnumber += 1
        while StringLiteralStarted == True and not self.EndOfFileReached():
            if self.EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
    
            col = Lines[currentlinenumber][currentcolumnnumber:].find("''")
            check1 = Lines[currentlinenumber][currentcolumnnumber:].find("'")
            while col != -1 and col == check1:
                currentcolumnnumber = currentcolumnnumber + col + 2
                if self.EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                if ReportAllElements == True:
                    self.ReportElement(currentlinenumber, currentcolumnnumber - 2, "MESSAGE", "Double single quote inside string literal interpreted as one single quote")
                col = Lines[currentlinenumber][currentcolumnnumber:].find("''")
                check1 = Lines[currentlinenumber][currentcolumnnumber:].find("'")
    
            col = Lines[currentlinenumber][currentcolumnnumber:].find("'")
            if col == -1:
                currentlinenumber += 1
                currentcolumnnumber = 0
            else:
                currentcolumnnumber = currentcolumnnumber + col + 1
                l = prevline
                c = prevcol + 1
                strcontent = ""
                while l < currentlinenumber:
                    strcontent = strcontent + Lines[l][c:]
                    l += 1
                    c = 0
                strcontent = strcontent + Lines[currentlinenumber][c:currentcolumnnumber - 1]
                strcontent = strcontent.replace("''", "'")
                if self.EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                self.InterpretElement(prevline, prevcol, "STRINGLITERAL", strcontent)
                StringLiteralStarted = False
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextQuotedIdentifier(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        QuotedIdentifierStarted = False
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        elif Lines[currentlinenumber][currentcolumnnumber] == '"':
            QuotedIdentifierStarted = True
            moved = True
            prevline = currentlinenumber
            prevcol = currentcolumnnumber
        else:
            pass
    
        if QuotedIdentifierStarted == True:
            currentcolumnnumber += 1
        while QuotedIdentifierStarted == True and not self.EndOfFileReached():
            if self.EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
    
            col = Lines[currentlinenumber][currentcolumnnumber:].find('"')
            if col == -1:
                currentlinenumber += 1
                currentcolumnnumber = 0
            else:
                currentcolumnnumber = currentcolumnnumber + col + 1
                l = prevline
                c = prevcol + 1
                strcontent = ""
                while l < currentlinenumber:
                    strcontent = strcontent + Lines[l][c:]
                    l += 1
                    c = 0
                strcontent = strcontent + Lines[currentlinenumber][c:currentcolumnnumber - 1]
                if self.EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                self.InterpretElement(prevline, prevcol, "QUOTEDIDENTIFIER", strcontent)
                QuotedIdentifierStarted = False
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextNumberLiteral(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        else:
            a = re.search("(([-+]?[0-9]+[\.][0-9]+)|([-+]?[0-9]+))", Lines[currentlinenumber][currentcolumnnumber:])
            try:
                b = a.span()
            except:
                b = (-1, -1)
            if b[0] == 0:
                if currentcolumnnumber + b[1] > len(Lines[currentlinenumber]) - 1 or Lines[currentlinenumber][currentcolumnnumber + b[1]] not in ("?", "a"):
                #To be decided is there a list of chars that are not allowed after a number without blank in between
                    moved = True
                    prevline = currentlinenumber
                    prevcol = currentcolumnnumber
                    eltcontent = Lines[currentlinenumber][currentcolumnnumber:currentcolumnnumber + b[1]]
                    currentcolumnnumber = currentcolumnnumber + b[1]
                    if self.EndOfLineReached():
                        currentlinenumber += 1
                        currentcolumnnumber = 0
                    self.InterpretElement(prevline, prevcol, "NUMBERLITERAL", eltcontent)
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextWord(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        else:
            a = re.search("[a-z|A-Z|_][0-9|a-z|A-Z|_]*", Lines[currentlinenumber][currentcolumnnumber:])
            try:
                b = a.span()
            except:
                b = (-1, -1)
            if b[0] == 0:
                if currentcolumnnumber + b[1] > len(Lines[currentlinenumber]) - 1 or Lines[currentlinenumber][currentcolumnnumber + b[1]] not in ("?", "a"):
                #To be decided is there a list of chars that are not allowed after a word without blank in between
                    moved = True
                    prevline = currentlinenumber
                    prevcol = currentcolumnnumber
                    eltcontent = Lines[currentlinenumber][currentcolumnnumber:currentcolumnnumber + b[1]].upper()
                    currentcolumnnumber = currentcolumnnumber + b[1]
                    if self.EndOfLineReached():
                        currentlinenumber += 1
                        currentcolumnnumber = 0
                    self.InterpretElement(prevline, prevcol, "WORD", eltcontent)
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextSingleChar(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        else:
            if Lines[currentlinenumber][currentcolumnnumber] in ('"', '{', '}', '[', ']', '?', '.', '*', '(', ')', ',', '-', '+', '/', '\\', '<', '>', '!', '=', '|', ';'):
                moved = True
                prevline = currentlinenumber
                prevcol = currentcolumnnumber
                currentcolumnnumber += 1
                if self.EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                self.InterpretElement(prevline, prevcol, "SINGLECHAR", Lines[prevline][prevcol])
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextIllegalChar(self):
        global currentlinenumber
        global currentcolumnnumber
        global moved
        self.GoNextNonEmpty()
        if self.EndOfFileReached():
            pass
        else:
            moved = True
            prevline = currentlinenumber
            prevcol = currentcolumnnumber
            currentcolumnnumber += 1
            if self.EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
            self.InterpretElement(prevline, prevcol, "ILLEGALCHAR", Lines[prevline][prevcol])
    #-----------------------------------------------------------------------------------------------
    def ParseLines(self, pLines, pReportFile, pInputFileName):
        global infile
        global Lines
        global file_allrpt
        global currentlinenumber
        global currentcolumnnumber
        global moved
        global ReportAllElements
        global FoundTokens
        global MyKeywordList

        MyKeywordList = KeywordList()
        
        ReportAllElements = False
        Lines = pLines
        file_allrpt = pReportFile
        infile = pInputFileName

        currentlinenumber = 0
        currentcolumnnumber = 0
    
        self.ReportElement(currentlinenumber, currentcolumnnumber, "MESSAGE", "start parsing file")

        FoundTokens = []

        tokencounter = 0

        while self.EndOfFileReached() == False:
            moved = False
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextMultiLineComment()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextSingleLineComment()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextStringLiteral()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextQuotedIdentifier()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextNumberLiteral()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextWord()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextSingleChar()
            if moved == False and self.EndOfFileReached() == False:
                self.IdentifyNextIllegalChar()
            tokencounter += 1
            if tokencounter % 100000 == 0:
                print(str(tokencounter) + " tokens found in " + infile)
        
        return FoundTokens
    #-----------------------------------------------------------------------------------------------
