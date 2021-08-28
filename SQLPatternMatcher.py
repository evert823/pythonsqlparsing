# 
# August 2021 Evert Jan Karman / evert823 / project to parse SQL using Python
# 
from re import S
from typing import MutableSequence
from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import PatternToken
from sqlparser_commonclasses import ParsePattern
from sqlparser_commonclasses import PatternList

class PatternIdentificationResult:
    def __init__(self):
        self.Matches = False
        self.newsqltokenidx = 0

class SQLPatternMatcher:
    #-----------------------------------------------------------------------------------------------
    def EndOfPattern(self, ppatternidx, ppatterntokenidx):
        if ppatternidx >= len(MyPatternList.ValidPatterns):
            return True
        elif ppatterntokenidx >= len(MyPatternList.ValidPatterns[ppatternidx].PatternTokens):
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def EndOfSQL(self, pidx):
        if pidx >= len(FoundTokens):
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def MatchPatternToken(self, psqlidx, ppatternidx, ppatterntokenidx):
        # MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx]
        # FoundTokens[psqlidx]
        MySubResult = PatternIdentificationResult()

        if FoundTokens[psqlidx].TokenType == "ILLEGALCHAR":
            MySubResult.Matches = False
            MySubResult.newsqltokenidx = psqlidx + 1
            return MySubResult

        if MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenType == "PATTERN":
            subpi = 0
            while (MyPatternList.ValidPatterns[subpi].PatternName !=
                      MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].ExpressesPattern and
                      subpi < len(MyPatternList.ValidPatterns)):
                subpi += 1
            if subpi >= len(MyPatternList.ValidPatterns):
                MySubResult.Matches = False
                MySubResult.newsqltokenidx = psqlidx + 1
                return MySubResult
            else:
                return self.IdentifyNextPattern(psqlidx, subpi) # INDIRECT RECURSION
        elif (MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenType 
                        in ("STRINGLITERAL", "NUMBERLITERAL", "VARIABLE")
                        and FoundTokens[psqlidx].TokenType ==
                                MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenType):
            MySubResult.Matches = True
            MySubResult.newsqltokenidx = psqlidx + 1
            return MySubResult
        elif (MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenType 
                        in ("KEYWORD", "SINGLECHAR")
                        and FoundTokens[psqlidx].TokenType ==
                                MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenType
                        and FoundTokens[psqlidx].TokenContent ==
                                MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenContent):
            MySubResult.Matches = True
            MySubResult.newsqltokenidx = psqlidx + 1
            return MySubResult
        else:
            MySubResult.Matches = False
            MySubResult.newsqltokenidx = psqlidx + 1
            return MySubResult
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextPattern(self, psqltokenidx, ppatternidx):

        MyResult = PatternIdentificationResult()

        patterntokenidx = 0
        sqlidx = psqltokenidx

        conflict = False

        while conflict == False and self.EndOfSQL(sqlidx) == False and self.EndOfPattern(ppatternidx,patterntokenidx) == False:
            while (self.EndOfSQL(sqlidx) == False and (FoundTokens[sqlidx].TokenType == "MULTILINECOMMENT" 
                                                 or FoundTokens[sqlidx].TokenType == "SINGLELINECOMMENT")):
                sqlidx += 1
            if self.EndOfSQL(sqlidx) == False:
                thismatches = self.MatchPatternToken(sqlidx,ppatternidx, patterntokenidx)
                s = ("Matching token SQL=" + FoundTokens[sqlidx].CsvLineFromToken() +
                                   " Patterntoken=" + MyPatternList.ValidPatterns[ppatternidx].PatternTokens[patterntokenidx].PatternTokenAsString() +
                                   " Result=" + str(thismatches.Matches) + "," + str(thismatches.newsqltokenidx) + "\n")
                file_allrpt.write(s)
                moved = False
                while (thismatches.Matches == True and
                             MyPatternList.ValidPatterns[ppatternidx].PatternTokens[patterntokenidx].IsRepeatingToken == True and
                             self.EndOfSQL(sqlidx) == False):
                    sqlidx =thismatches.newsqltokenidx
                    moved = True
                    thismatches = self.MatchPatternToken(sqlidx,ppatternidx, patterntokenidx)
                    s = ("Matching token SQL=" + FoundTokens[sqlidx].CsvLineFromToken() +
                                       " Patterntoken=" + MyPatternList.ValidPatterns[ppatternidx].PatternTokens[patterntokenidx].PatternTokenAsString() +
                                       " Result=" + str(thismatches.Matches) + "," + str(thismatches.newsqltokenidx) + "\n")
                    file_allrpt.write(s)

                if moved == True:
                    patterntokenidx += 1
                elif thismatches.Matches == False and MyPatternList.ValidPatterns[ppatternidx].PatternTokens[patterntokenidx].IsOptionalToken == True:
                    patterntokenidx += 1
                elif thismatches.Matches == True:
                    patterntokenidx += 1
                    sqlidx = thismatches.newsqltokenidx
                else:
                    patterntokenidx +=1
                    conflict = True
        
        if conflict == False and self.EndOfPattern(ppatternidx,patterntokenidx) == True:
            MyResult.Matches = True
        else:
            MyResult.Matches = False
        MyResult.newsqltokenidx = sqlidx

        s = ("IdentifyNextPattern SQL " + str(psqltokenidx) + " Pattern " + str(ppatternidx) +
                                          " Match=" + str(MyResult.Matches) + " newsqlidx=" + str(MyResult.newsqltokenidx)
                                          + "\n")
        file_allrpt.write(s)

        return MyResult
    #-----------------------------------------------------------------------------------------------
    def SQLPatternMatcher_main(self, pFoundTokens, pReportFile, pInputFileName):
        global FoundTokens
        global infile
        global file_allrpt
        global FoundTokensPointer
        global MyPatternList

        FoundTokens = pFoundTokens
        file_allrpt = pReportFile
        infile = pInputFileName

        MyPatternList = PatternList()

        FoundTokensPointer = 0
        while self.EndOfSQL(FoundTokensPointer) == False:
            moved = False
            p = 0
            while p < len(MyPatternList.ValidPatterns) and moved == False:
                result = self.IdentifyNextPattern(FoundTokensPointer, p)
                if result.Matches == True:
                    FoundTokensPointer = result.newsqltokenidx
                    moved = True
                p += 1
            if moved == False and p > len(MyPatternList.ValidPatterns) - 1:
                #Now you're in an illegal syntax, but let's move on anyways
                FoundTokensPointer += 1
