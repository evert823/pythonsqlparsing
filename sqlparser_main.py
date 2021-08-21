# 
# August 2021 Evert Jan Karman / evert823 / project to parse SQL using Python
# 
import os
import shutil
import sys
import re
from datetime import datetime
# from typing import ContextManager

#-----------------------------------------------------------------------------------------------
def InterpretElement(pprevline, pprevcol, pelttype, pcontent):
    pass
#-----------------------------------------------------------------------------------------------
def ReportElement(pprevline, pprevcol, pelttype, pcontent):
    if ReportAllElements == True:
        file_allrpt.write(infile + "," + str(pprevline) + "," + str(pprevcol) + "," + str(currentlinenumber) + "," + str(currentcolumnnumber) + "," + pelttype + "," + pcontent + "\n")
#-----------------------------------------------------------------------------------------------
def EndOfLineReached():
    global currentlinenumber
    global currentcolumnnumber
    if currentcolumnnumber > len(Lines[currentlinenumber]) - 1:
        return True
    elif currentcolumnnumber == len(Lines[currentlinenumber]) - 1 and Lines[currentlinenumber][currentcolumnnumber] == "\n":
        return True
    else:
        return False
#-----------------------------------------------------------------------------------------------
def EndOfFileReached():
    global currentlinenumber
    global currentcolumnnumber

    if currentlinenumber > len(Lines) - 1:
        return True
    elif currentlinenumber == len(Lines) - 1 and EndOfLineReached():
        return True
    else:
        return False
#-----------------------------------------------------------------------------------------------
def SampleIterateAllLinesColumns():
    global currentlinenumber
    global currentcolumnnumber

    while not EndOfFileReached():
        print(infile + " ln " + str(currentlinenumber) + " col " + str(currentcolumnnumber) + " " + Lines[currentlinenumber][currentcolumnnumber])
        currentcolumnnumber += 1
        if EndOfLineReached():
            currentlinenumber += 1
            currentcolumnnumber = 0
#-----------------------------------------------------------------------------------------------
def GoNextNonEmpty():
    global currentlinenumber
    global currentcolumnnumber
    while (not EndOfFileReached()) and (EndOfLineReached() or Lines[currentlinenumber][currentcolumnnumber] in ("\t", " ")):
        currentcolumnnumber += 1
        if EndOfLineReached():
            currentlinenumber += 1
            currentcolumnnumber = 0
#-----------------------------------------------------------------------------------------------
def IdentifyNextMultiLineComment():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    MultiLineCommentStarted = False
    GoNextNonEmpty()
    if EndOfFileReached():
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

    while MultiLineCommentStarted == True and not EndOfFileReached():
        col = Lines[currentlinenumber][currentcolumnnumber:].find("*/")
        if col == -1:
            currentlinenumber += 1
            currentcolumnnumber = 0
        else:
            currentcolumnnumber = currentcolumnnumber + col + 2
            if EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
            ReportElement(prevline, prevcol, "MULTILINECOMMENT", "")
            MultiLineCommentStarted = False
#-----------------------------------------------------------------------------------------------
def IdentifyNextSingleLineComment():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    GoNextNonEmpty()
    if EndOfFileReached():
        pass
    elif currentcolumnnumber > len(Lines[currentlinenumber]) - 2:
        pass
    elif Lines[currentlinenumber][currentcolumnnumber:currentcolumnnumber + 2] == "--":
        moved = True
        prevline = currentlinenumber
        prevcol = currentcolumnnumber
        currentlinenumber += 1
        currentcolumnnumber = 0
        ReportElement(prevline, prevcol, "SINGLELINECOMMENT", "")
    else:
        pass
#-----------------------------------------------------------------------------------------------
def IdentifyNextStringLiteral_allows_multiline():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    StringLiteralStarted = False
    GoNextNonEmpty()
    if EndOfFileReached():
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
    while StringLiteralStarted == True and not EndOfFileReached():
        if EndOfLineReached():
            currentlinenumber += 1
            currentcolumnnumber = 0

        col = Lines[currentlinenumber][currentcolumnnumber:].find("''")
        check1 = Lines[currentlinenumber][currentcolumnnumber:].find("'")
        while col != -1 and col == check1:
            currentcolumnnumber = currentcolumnnumber + col + 2
            if EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
            ReportElement(currentlinenumber, currentcolumnnumber - 2, "MESSAGE", "Double single quote inside string literal interpreted as one single quote")
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
            if EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
            ReportElement(prevline, prevcol, "STRINGLITERAL", strcontent)
            InterpretElement(prevline, prevcol, "STRINGLITERAL", strcontent)
            StringLiteralStarted = False
#-----------------------------------------------------------------------------------------------
def IdentifyNextStringLiteral():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    StringLiteralStarted = False
    GoNextNonEmpty()
    if EndOfFileReached():
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

        col = Lines[currentlinenumber][currentcolumnnumber:].find("''")
        check1 = Lines[currentlinenumber][currentcolumnnumber:].find("'")
        while col != -1 and col == check1:
            currentcolumnnumber = currentcolumnnumber + col + 2
            ReportElement(currentlinenumber, currentcolumnnumber - 2, "MESSAGE", "Double single quote inside string literal interpreted as one single quote")
            col = Lines[currentlinenumber][currentcolumnnumber:].find("''")
            check1 = Lines[currentlinenumber][currentcolumnnumber:].find("'")

        col = Lines[currentlinenumber][currentcolumnnumber:].find("'")
        if col == -1:
            ReportElement(currentlinenumber, currentcolumnnumber, "MESSAGE", "ERROR no closing quote found for starting string literal")
            currentlinenumber += 1
            currentcolumnnumber = 0
        else:
            strcontent = Lines[currentlinenumber][prevcol + 1:currentcolumnnumber + col]
            strcontent = strcontent.replace("''", "'")
            currentcolumnnumber = currentcolumnnumber + col + 1
            if EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
            ReportElement(prevline, prevcol, "STRINGLITERAL", strcontent)
            InterpretElement(prevline, prevcol, "STRINGLITERAL", strcontent)
#-----------------------------------------------------------------------------------------------
def IdentifyNextNumberLiteral():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    GoNextNonEmpty()
    if EndOfFileReached():
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
                if EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                ReportElement(prevline, prevcol, "NUMBERLITERAL", eltcontent)
                InterpretElement(prevline, prevcol, "NUMBERLITERAL", eltcontent)
#-----------------------------------------------------------------------------------------------
def IdentifyNextWord():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    GoNextNonEmpty()
    if EndOfFileReached():
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
                if EndOfLineReached():
                    currentlinenumber += 1
                    currentcolumnnumber = 0
                ReportElement(prevline, prevcol, "WORD", eltcontent)
                InterpretElement(prevline, prevcol, "WORD", eltcontent)
#-----------------------------------------------------------------------------------------------
def IdentifyNextSingleChar():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    GoNextNonEmpty()
    if EndOfFileReached():
        pass
    else:
        if Lines[currentlinenumber][currentcolumnnumber] in ('"', '{', '}', '[', ']', '?', '.', '*', '(', ')', ',', '-', '+', '/', '\\', '<', '>', '!', '=', '|', ';'):
            moved = True
            prevline = currentlinenumber
            prevcol = currentcolumnnumber
            currentcolumnnumber += 1
            if EndOfLineReached():
                currentlinenumber += 1
                currentcolumnnumber = 0
            ReportElement(prevline, prevcol, "SINGLECHAR", Lines[prevline][prevcol])
            InterpretElement(prevline, prevcol, "SINGLECHAR", Lines[prevline][prevcol])
#-----------------------------------------------------------------------------------------------
def IdentifyNextIllegalChar():
    global currentlinenumber
    global currentcolumnnumber
    global moved
    GoNextNonEmpty()
    if EndOfFileReached():
        pass
    else:
        moved = True
        prevline = currentlinenumber
        prevcol = currentcolumnnumber
        currentcolumnnumber += 1
        if EndOfLineReached():
            currentlinenumber += 1
            currentcolumnnumber = 0
        ReportElement(prevline, prevcol, "ILLEGALCHAR", Lines[prevline][prevcol])
        InterpretElement(prevline, prevcol, "ILLEGALCHAR", Lines[prevline][prevcol])
#-----------------------------------------------------------------------------------------------
def parse_one_file():
    # Lines will be accessed in other functions
    # currentlinenumber and currentcolumnnumber will be accessed and changed in other functions
    global Lines
    global currentlinenumber
    global currentcolumnnumber
    global moved

    file1 = open(infile, 'r')
    Lines = file1.readlines()
    file1.close()


    currentlinenumber = 0
    currentcolumnnumber = 0

    ReportElement(currentlinenumber, currentcolumnnumber, "MESSAGE", "start parsing file")

    while EndOfFileReached() == False:
        moved = False
        if moved == False and EndOfFileReached() == False:
            IdentifyNextMultiLineComment()
        if moved == False and EndOfFileReached() == False:
            IdentifyNextSingleLineComment()
        #if moved == False and EndOfFileReached() == False:
        #    IdentifyNextStringLiteral()
        if moved == False and EndOfFileReached() == False:
            IdentifyNextStringLiteral_allows_multiline()
        if moved == False and EndOfFileReached() == False:
            IdentifyNextNumberLiteral()
        if moved == False and EndOfFileReached() == False:
            IdentifyNextWord()
        if moved == False and EndOfFileReached() == False:
            IdentifyNextSingleChar()
        if moved == False and EndOfFileReached() == False:
            IdentifyNextIllegalChar()
    


    file2 = open(outfile, 'w')
    file2.write(myheader)

    for line in Lines:
        line1 = line.replace("S", "s")
        line1 = line1.replace("E", "x")
        file2.write(line1)

    file2.close()
#-----------------------------------------------------------------------------------------------
def prepare_folders(GetUserConfirmation):
    # Validation
    if infolder == outfolder:
        print("Outputfolder must be different from inputfolder")
        sys.exit()
    if os.path.isdir(infolder) == False:
        print("Inputfolder must exist")
        sys.exit()

    # Conditionally get user confirmation
    if GetUserConfirmation == True:
        val = input(outfolder + " will be removed, type yes if you're OK with that: ")
    else:
        val = "yes"

    # Remove specified outputfolder, get user confirmation
    if os.path.isdir(outfolder) == True:
        if val != "yes":
            print("Program will stop now")
            sys.exit()
        try:
            shutil.rmtree(outfolder)
        except OSError as e:
            print("Error: %s : %s" % (outfolder, e.strerror))

    # Recreate the specified outputfolder with entire subdirectory structure
    # from the specified inputfolder
    os.mkdir(outfolder)

    for root, subdirectories, files in os.walk(infolder):
        for subdirectory in subdirectories:
            dir_in = os.path.join(root, subdirectory)
            dir_out = dir_in.replace(infolder, outfolder)
            os.mkdir(dir_out)
#-----------------------------------------------------------------------------------------------
def process_folders():
    # Walk through the files from the input directory structure and for each file call the main function
    # for one single file
    global infile
    global outfile
    global reportfile
    global allreportfile
    global file_allrpt

    allreportfile = outfolder + "/allreport_" + sys.argv[0] + ".report"
    file_allrpt = open(allreportfile, 'w')
    file_allrpt.write(infolder + ",0,0,0,0," + "MESSAGE,WARNING linenumbers and columnnumbers in this report are zero-based\n")

    for root, subdirectories, files in os.walk(infolder):
        for file in files:
            infile = os.path.join(root, file)
            outfile = infile.replace(infolder, outfolder)
            reportfile = outfile + ".report"
            parse_one_file()
    file_allrpt.close()
#-----------------------------------------------------------------------------------------------

ReportAllElements = True
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
myheader = "--Generated by " + sys.argv[0] + " " + dt_string + "\n"

if len(sys.argv) != 3:
    print(sys.argv[0] + " requires parameters for input foldername and output foldername relative to current dir")
    sys.exit()

infolder = './' + sys.argv[1]
outfolder = './' + sys.argv[2]

prepare_folders(False)
process_folders()
