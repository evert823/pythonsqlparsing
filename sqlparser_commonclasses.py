class SQLToken:
    def __init__(self):
        self.originfilename = "" #Added for tracing and debugging purpose
        self.bline = 0
        self.bcol = 0
        self.eline = 0
        self.ecol = 0 # eline and ecol are exclusive
        self.TokenType = ""
        self.TokenContent = ""
        self.IsQuotedIdentifier = False
    
    def CsvLineFromToken(self):
        a = (self.originfilename 
                   + "," + str(self.bline) + "," + str(self.bcol) 
                   + "," + str(self.eline) + "," + str(self.ecol) + ","
                   + self.TokenType + ",")
        if self.IsQuotedIdentifier == True:
            a = a + '"' + self.TokenContent + '"'
        else:
            a = a + self.TokenContent
        return a;

class PatternToken:
    def __init__(self):
        self.PatternTokenType = ""
        self.PatternTokenContent = ""
        self.PatternTokenInterpretation = ""
        self.ExpressesPattern = ""
        self.IsOptionalToken = False
        self.IsRepeatingToken = False
    def PatternTokenAsString(self):
        s = (self.PatternTokenType + "," + self.PatternTokenContent + "," + self.PatternTokenInterpretation + ","
                              + self.ExpressesPattern + ",Optional=" + str(self.IsOptionalToken) + ",Repeating=" + str(self.IsRepeatingToken))
        return s

class ParsePattern:
    def __init__(self):
        self.PatternName = ""
        self.PatternTokens = []
    
    def AddPatternToken(self, ptype, pcontent, pinterpretation, pexpressespattern, pisoptional, pisrepeating):
        MyPatternToken = PatternToken()
        MyPatternToken.PatternTokenType = ptype
        MyPatternToken.PatternTokenContent = pcontent
        MyPatternToken.PatternTokenInterpretation = pinterpretation
        MyPatternToken.ExpressesPattern = pexpressespattern
        MyPatternToken.IsOptionalToken = pisoptional
        MyPatternToken.IsRepeatingToken = pisrepeating
        self.PatternTokens.append(MyPatternToken)
    def ParsePatternAsString(self):
        s = self.PatternName + "\n"
        for tk in self.PatternTokens:
            s = s + tk.PatternTokenAsString() + "\n"
        return s

class PatternList:
    def __init__(self):
        self.ValidPatterns = []
        MyPattern = ParsePattern()
        MyPattern.PatternName = "COMMA_COLUMN"
        MyPattern.AddPatternToken("SINGLECHAR", ",", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "SELECTCOLUMNSFROMTABLEALIAS"
        MyPattern.AddPatternToken("KEYWORD", "SELECT", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "COMMA_COLUMN", True, True)
        MyPattern.AddPatternToken("KEYWORD", "FROM", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "SCHEMANAME", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ".", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "TABLENAME", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "AS", "", "", True, False)
        MyPattern.AddPatternToken("VARIABLE", "", "ALIAS", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ";", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

class KeywordList:
    def __init__(self):
        self.ValidKeyWords = {"SELECT", "INSERT", "UPDATE", "CREATE",
                              "DELETE", "FROM", "AS", "REPLACE", "OR", "CREATE", 
                              "VIEW", "TABLE", "INDEX", "PARTITION"}
