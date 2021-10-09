# 
# August 2021 Evert Jan Karman / evert823 / project to parse SQL using Python
# 
from re import S
from typing import MutableSequence
from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import SQLTokenInPattern
from sqlparser_commonclasses import PatternToken
from sqlparser_commonclasses import ParsePattern
from sqlparser_commonclasses import PatternList

class PatternIdentificationResult:
    def __init__(self):
        self.Matches = False
        self.newsqltokenidx = 0
        self.CandidateIdentifiedPattern = []

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
    def MatchPatternToken(self, psqlidx, ppatternidx, ppatterntokenidx, pCandidateFoundPatternIdx, pParentFoundPatternIdx):
        # MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx]
        # FoundTokens[psqlidx]

        MySubResult = PatternIdentificationResult()

        if FoundTokens[psqlidx].TokenType == "ILLEGALCHAR":
            MySubResult.Matches = False
            MySubResult.newsqltokenidx = psqlidx + 1
            return MySubResult
        
        ptype = MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenType

        if ptype == "PATTERN":
            subpi = 0
            while (subpi < len(MyPatternList.ValidPatterns) and MyPatternList.ValidPatterns[subpi].PatternName !=
                      MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].ExpressesPattern):
                subpi += 1
            if subpi >= len(MyPatternList.ValidPatterns):
                print("Found invalid subpattern reference " + MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].ExpressesPattern)
                MySubResult.Matches = False
                MySubResult.newsqltokenidx = psqlidx + 1
                return MySubResult
            else:
                return self.IdentifyNextPattern(psqlidx, subpi, pCandidateFoundPatternIdx) # INDIRECT RECURSION
        elif (ptype in ("STRINGLITERAL", "NUMBERLITERAL", "VARIABLE", "KEYWORD", "SINGLECHAR")
                        and FoundTokens[psqlidx].TokenType == ptype
                        and (FoundTokens[psqlidx].TokenContent ==
                                MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenContent
                                 or ptype in ("STRINGLITERAL", "NUMBERLITERAL", "VARIABLE"))):
            MySubResult.Matches = True
            MySubResult.newsqltokenidx = psqlidx + 1
            MySQLTokenInPattern = SQLTokenInPattern()
            MySQLTokenInPattern.PatternName = MyPatternList.ValidPatterns[ppatternidx].PatternName
            MySQLTokenInPattern.PatternTokenidx = ppatterntokenidx
            MySQLTokenInPattern.PatternTokenInterpretation = MyPatternList.ValidPatterns[ppatternidx].PatternTokens[ppatterntokenidx].PatternTokenInterpretation
            MySQLTokenInPattern.FoundPatternidx = pCandidateFoundPatternIdx
            MySQLTokenInPattern.ParentFoundPatternidx = pParentFoundPatternIdx
            MySQLTokenInPattern.originfilename = FoundTokens[psqlidx].originfilename
            MySQLTokenInPattern.bline = FoundTokens[psqlidx].bline
            MySQLTokenInPattern.bcol = FoundTokens[psqlidx].bcol
            MySQLTokenInPattern.eline = FoundTokens[psqlidx].eline
            MySQLTokenInPattern.ecol = FoundTokens[psqlidx].ecol
            MySQLTokenInPattern.TokenType = FoundTokens[psqlidx].TokenType
            MySQLTokenInPattern.TokenContent = FoundTokens[psqlidx].TokenContent
            MySQLTokenInPattern.IsQuotedIdentifier = FoundTokens[psqlidx].IsQuotedIdentifier
            MySubResult.CandidateIdentifiedPattern.append(MySQLTokenInPattern)
            return MySubResult
        else:
            MySubResult.Matches = False
            MySubResult.newsqltokenidx = psqlidx + 1
            return MySubResult
    #-----------------------------------------------------------------------------------------------
    def IdentifyNextPattern(self, psqltokenidx, ppatternidx, pParentFoundPatternIdx):
        global LastUsedFoundPatternIdx

        MyResult = PatternIdentificationResult()

        LastUsedFoundPatternIdx += 1
        CandidateFoundPatternIdx = LastUsedFoundPatternIdx

        patterntokenidx = 0
        sqlidx = psqltokenidx

        conflict = False

        while conflict == False and self.EndOfSQL(sqlidx) == False and self.EndOfPattern(ppatternidx,patterntokenidx) == False:
            while (self.EndOfSQL(sqlidx) == False and (FoundTokens[sqlidx].TokenType == "MULTILINECOMMENT" 
                                                 or FoundTokens[sqlidx].TokenType == "SINGLELINECOMMENT")):
                sqlidx += 1
            if self.EndOfSQL(sqlidx) == False:
                thismatches = self.MatchPatternToken(sqlidx,ppatternidx, patterntokenidx, CandidateFoundPatternIdx, pParentFoundPatternIdx)
                if thismatches.Matches == True:
                    MyResult.CandidateIdentifiedPattern.extend(thismatches.CandidateIdentifiedPattern)
                moved = False
                while (thismatches.Matches == True and
                             MyPatternList.ValidPatterns[ppatternidx].PatternTokens[patterntokenidx].IsRepeatingToken == True and
                             self.EndOfSQL(sqlidx) == False):
                    sqlidx =thismatches.newsqltokenidx
                    moved = True
                    thismatches = self.MatchPatternToken(sqlidx,ppatternidx, patterntokenidx, CandidateFoundPatternIdx, pParentFoundPatternIdx)
                    if thismatches.Matches == True:
                        MyResult.CandidateIdentifiedPattern.extend(thismatches.CandidateIdentifiedPattern)

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
            LastUsedFoundPatternIdx = CandidateFoundPatternIdx - 1
            MyResult.CandidateIdentifiedPattern.clear()
        MyResult.newsqltokenidx = sqlidx

        return MyResult
    #-----------------------------------------------------------------------------------------------
    def SQLPatternMatcher_main(self, pFoundTokens, pReportFile, pInputFileName):
        global FoundTokens
        global infile
        global file_allrpt
        global FoundTokensPointer
        global MyPatternList
        global LastUsedFoundPatternIdx

        LastUsedFoundPatternIdx = -1

        FoundTokensInPatterns = []

        FoundTokens = pFoundTokens
        file_allrpt = pReportFile
        infile = pInputFileName

        MyPatternList = PatternList()

        FoundTokensPointer = 0
        while self.EndOfSQL(FoundTokensPointer) == False:
            moved = False
            p = 0
            while p < len(MyPatternList.ValidPatterns) and moved == False:
                result = self.IdentifyNextPattern(FoundTokensPointer, p, -1)
                if result.Matches == True:
                    FoundTokensInPatterns.extend(result.CandidateIdentifiedPattern)
                    FoundTokensPointer = result.newsqltokenidx
                    moved = True
                p += 1
            if moved == False and p > len(MyPatternList.ValidPatterns) - 1:
                #Now you're in an illegal syntax, but let's move on anyways

                if FoundTokens[FoundTokensPointer].TokenType not in ("MULTILINECOMMENT", "SINGLELINECOMMENT"):
                    MySQLTokenInPattern = SQLTokenInPattern()
                    LastUsedFoundPatternIdx += 1
                    MySQLTokenInPattern.FoundPatternidx = LastUsedFoundPatternIdx
                    MySQLTokenInPattern.ParentFoundPatternidx = -1
                    MySQLTokenInPattern.originfilename = FoundTokens[FoundTokensPointer].originfilename
                    MySQLTokenInPattern.bline = FoundTokens[FoundTokensPointer].bline
                    MySQLTokenInPattern.bcol = FoundTokens[FoundTokensPointer].bcol
                    MySQLTokenInPattern.eline = FoundTokens[FoundTokensPointer].eline
                    MySQLTokenInPattern.ecol = FoundTokens[FoundTokensPointer].ecol
                    MySQLTokenInPattern.TokenType = FoundTokens[FoundTokensPointer].TokenType
                    MySQLTokenInPattern.TokenContent = FoundTokens[FoundTokensPointer].TokenContent
                    MySQLTokenInPattern.IsQuotedIdentifier = FoundTokens[FoundTokensPointer].IsQuotedIdentifier
                    FoundTokensInPatterns.append(MySQLTokenInPattern)
                
                FoundTokensPointer += 1

        f = 0

        while f < len(FoundTokensInPatterns):
            s = FoundTokensInPatterns[f].CsvLineFromSQLTokenInPattern() + "\n"
            file_allrpt.write(s)
            f += 1

        return FoundTokensInPatterns
