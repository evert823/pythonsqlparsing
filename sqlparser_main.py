# 
# August 2021 Evert Jan Karman / evert823 / project to parse SQL using Python
# 
import os
import shutil
import sys
from datetime import datetime
from LowLevelLinesParser import LowLevelLinesParser
from sqlparser_commonclasses import SQLToken
# from typing import ContextManager

#-----------------------------------------------------------------------------------------------
def emulatestring(pstrcontent):
    return "'" + pstrcontent.replace("'", "''") + "'"
#-----------------------------------------------------------------------------------------------
def AlterSQL(pFoundTokens):
    for ff in range(len(pFoundTokens)):
        if pFoundTokens[ff].TokenType == "MULTILINECOMMENT":
            continue
        if pFoundTokens[ff].TokenType == "SINGLELINECOMMENT":
            continue

        Next10Tokens = ""
        RealStatement = ""
        ff2 = ff
        snum = 0
        while ff2 < len(pFoundTokens) and snum < 11:
            if pFoundTokens[ff2].TokenType == "MULTILINECOMMENT":
                ff2 += 1
            elif pFoundTokens[ff2].TokenType == "SINGLELINECOMMENT":
                ff2 += 1
            elif pFoundTokens[ff2].TokenType == "KEYWORD":
                Next10Tokens += pFoundTokens[ff2].TokenContent + " "
                RealStatement += pFoundTokens[ff2].TokenContent + " "
                snum += 1
                ff2 += 1
            elif pFoundTokens[ff2].TokenType == "VARIABLE":
                Next10Tokens += pFoundTokens[ff2].TokenType + " "
                RealStatement += pFoundTokens[ff2].TokenContent + " "
                snum += 1
                ff2 += 1
            elif pFoundTokens[ff2].TokenType == "SINGLECHAR":
                Next10Tokens += pFoundTokens[ff2].TokenContent + " "
                RealStatement += pFoundTokens[ff2].TokenContent + " "
                snum += 1
                ff2 += 1
            else:
                ff2 += 1
        
        if Next10Tokens == "CREATE SET VOLATILE TABLE VARIABLE AS ( WITH VARIABLE AS ( ":
            s = pFoundTokens[ff].CsvLineFromToken()
            print(s + " " + RealStatement)
#-----------------------------------------------------------------------------------------------
def write_new_file_from_FoundTokens(pFoundTokens, poutfile):
    currentlinenumber = 0
    currentcolumnnumber = 0

    file2 = open(poutfile, 'w')
    #file2.write(myheader)

    for ff in range(len(pFoundTokens)):
        while currentlinenumber < pFoundTokens[ff].bline:
            file2.write(Lines[currentlinenumber][currentcolumnnumber:])
            currentlinenumber += 1
            currentcolumnnumber = 0
        if currentcolumnnumber < pFoundTokens[ff].bcol:
            file2.write(Lines[currentlinenumber][currentcolumnnumber:pFoundTokens[ff].bcol])
        if pFoundTokens[ff].TokenType == "STRINGLITERAL":
            file2.write(emulatestring(pFoundTokens[ff].TokenContent))
        elif pFoundTokens[ff].IsQuotedIdentifier == True:
            file2.write('"' + pFoundTokens[ff].TokenContent + '"')
        else:
            file2.write(pFoundTokens[ff].TokenContent)
        currentlinenumber = pFoundTokens[ff].eline
        currentcolumnnumber = pFoundTokens[ff].ecol
        if currentcolumnnumber == 0:
            file2.write("\n")

    l_e = len(Lines) - 1
    c_e = len(Lines[l_e]) - 1

    while currentlinenumber < l_e:
        file2.write(Lines[currentlinenumber][currentcolumnnumber:])
        currentlinenumber += 1
        currentcolumnnumber = 0

    file2.close()
#-----------------------------------------------------------------------------------------------
def parse_one_file():
    # Lines will be accessed in other functions
    global Lines
    global moved

    file1 = open(infile, 'r')
    Lines = file1.readlines()
    file1.close()

    MyLowLevelLinesParser = LowLevelLinesParser()

    FoundTokens = MyLowLevelLinesParser.ParseLines(Lines, file_lll_rpt, infile)

    AlterSQL(FoundTokens)
    write_new_file_from_FoundTokens(FoundTokens, outfile)
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
    global file_lll_rpt

    file_lll_rpt_name = outfolder + "/" + sys.argv[0] + "_lll.report"
    file_lll_rpt = open(file_lll_rpt_name, 'w')
    file_lll_rpt.write(infolder + ",0,0,0,0," + "MESSAGE,WARNING linenumbers and columnnumbers in this report are zero-based\n")


    for root, subdirectories, files in os.walk(infolder):
        for file in files:
            infile = os.path.join(root, file)
            outfile = infile.replace(infolder, outfolder)
            parse_one_file()
    file_lll_rpt.close()
#-----------------------------------------------------------------------------------------------

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
