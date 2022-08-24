# 
# August 2021 Evert Jan Karman / evert823 / project to parse SQL using Python
# 
import os
import shutil
import sys
from datetime import datetime
from LowLevelLinesParser import LowLevelLinesParser
from StatementHandler import StatementHandler
from sqlparser_commonclasses import SQLToken
# from typing import ContextManager

#-----------------------------------------------------------------------------------------------
def write_clean_file(pFoundStatements, poutfile):
    file2 = open(poutfile, 'w')

    for s in pFoundStatements:
        file2.write("-- " + s.StatementPattern + "\n")
        file2.write(s.CleanStatement + "\n")
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

        file2.write(pFoundTokens[ff].CleanContent())

        currentlinenumber = pFoundTokens[ff].eline
        currentcolumnnumber = pFoundTokens[ff].ecol

        if currentcolumnnumber == 0:
            file2.write("\n")

        for n in NewInserts:
            if n.aftertoken == ff:
                file2.write("\n")
                for s in n.insertlines:
                    file2.write(s + "\n")

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
    global NewInserts
    global moved

    NewInserts = []

    file1 = open(infile, 'r')
    Lines = file1.readlines()
    file1.close()

    MyLowLevelLinesParser = LowLevelLinesParser()
    MyStatementHandler = StatementHandler()

    FoundTokens = MyLowLevelLinesParser.ParseLines(Lines, file_lll_rpt, infile)
    FoundStatements = MyStatementHandler.BuildStatements(FoundTokens)
    MySubqueryTree = MyStatementHandler.BuildSubqueryTree(FoundTokens, FoundStatements)
    for sq in MySubqueryTree:
        ft = sq.tokens[0]
        Message = FoundTokens[ft].CsvLineFromToken()
        Message += " IS SUBQUERY IN "
        if sq.ParentStatement > -1:
            ft_parent = MySubqueryTree[sq.ParentStatement].tokens[0]
            Message += FoundTokens[ft_parent].CsvLineFromToken()
        Message += " NestedLevel : " + str(sq.NestedLevel)
        if sq.NestedLevel > 0:
            print(Message)

#    MyStatementHandler.FindFirstStatements(FoundTokens, FoundStatements, file_lll_rpt)

#    vt1 = MyStatementHandler.FindVolatileTables(FoundStatements)
#    vt2 = MyStatementHandler.FindCollectStatsOnVolatileTables(FoundStatements)

#    for s in vt1:
#        if s not in vt2:
#            print(infile + "|" + s + "| Trying to add statistics")
#            MyNewInsert = MyStatementHandler.AddStatsForVolatileTable(FoundTokens, FoundStatements, s)
#            if MyNewInsert.aftertoken > -1:
#                NewInserts.append(MyNewInsert)
    
    write_new_file_from_FoundTokens(FoundTokens, outfile)

    write_clean_file(FoundStatements, outfile_clean)
#-----------------------------------------------------------------------------------------------
def prepare_folders(GetUserConfirmation):
    # Validation
    if infolder == outfolder:
        print("Outputfolder must be different from inputfolder")
        sys.exit()
    if infolder == cleanfolder:
        print("Clean outputfolder must be different from inputfolder")
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
            shutil.rmtree(cleanfolder)
        except OSError as e:
            print("Error: %s : %s" % (outfolder, e.strerror))

    # Recreate the specified outputfolder with entire subdirectory structure
    # from the specified inputfolder
    os.mkdir(outfolder)
    os.mkdir(cleanfolder)

    for root, subdirectories, files in os.walk(infolder):
        for subdirectory in subdirectories:
            dir_in = os.path.join(root, subdirectory)
            dir_out = dir_in.replace(infolder, outfolder)
            os.mkdir(dir_out)
            dir_clean = dir_in.replace(infolder, cleanfolder)
            os.mkdir(dir_clean)
#-----------------------------------------------------------------------------------------------
def process_folders():
    # Walk through the files from the input directory structure and for each file call the main function
    # for one single file
    global infile
    global outfile
    global outfile_clean
    global file_lll_rpt

    file_lll_rpt_name = cleanfolder + "/" + sys.argv[0] + "_lll.report"
    file_lll_rpt = open(file_lll_rpt_name, 'w')
    file_lll_rpt.write(infolder + ",0,0,0,0," + "MESSAGE,WARNING linenumbers and columnnumbers in this report are zero-based\n")


    for root, subdirectories, files in os.walk(infolder):
        for file in files:
            infile = os.path.join(root, file)
            outfile = infile.replace(infolder, outfolder)
            outfile_clean = infile.replace(infolder, cleanfolder)
            parse_one_file()
    file_lll_rpt.close()
#-----------------------------------------------------------------------------------------------

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
myheader = "--Generated by " + sys.argv[0] + " " + dt_string + "\n"

if len(sys.argv) != 4:
    print(sys.argv[0] + " requires parameters for input foldername, output foldername and clean output foldername relative to current dir")
    sys.exit()

infolder = './' + sys.argv[1]
outfolder = './' + sys.argv[2]
cleanfolder = './' + sys.argv[3]

prepare_folders(False)
process_folders()
