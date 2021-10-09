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
        MyPattern.PatternName = "VOLATILE_V01"
        MyPattern.AddPatternToken("PATTERN", "", "", "STARTVOLATILE", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "SELECTCOLUMNSASALIASFROMTABLEWHERE", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ")", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "WITH", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "DATA", "", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "PRIMARYINDEX", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "ONCOMMITPRESERVEROWS", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ";", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "COMMA_COLUMNASALIAS"
        MyPattern.AddPatternToken("SINGLECHAR", ",", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "AS", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNALIAS", "", False, False)
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
        MyPattern.AddPatternToken("VARIABLE", "", "TABLEALIAS", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ";", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "PRIMARYINDEX"
        MyPattern.AddPatternToken("KEYWORD", "PRIMARY", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "INDEX", "", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", "(", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "COMMA_COLUMN", True, True)
        MyPattern.AddPatternToken("SINGLECHAR", ")", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "SELECTCOLUMNSFROMTABLEWHERE"
        MyPattern.AddPatternToken("KEYWORD", "SELECT", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "COMMA_COLUMN", True, True)
        MyPattern.AddPatternToken("KEYWORD", "FROM", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "SCHEMANAME", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ".", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "TABLENAME", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "WHERE", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", "=", "", "", False, False)
        MyPattern.AddPatternToken("STRINGLITERAL", "", "COMPAREVALUE", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "ANDCOLUMNEQUALS", True, True)
        #MyPattern.AddPatternToken("SINGLECHAR", ";", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "SELECTCOLUMNSASALIASFROMTABLEWHERE"
        MyPattern.AddPatternToken("KEYWORD", "SELECT", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "AS", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNALIAS", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "COMMA_COLUMNASALIAS", True, True)
        MyPattern.AddPatternToken("KEYWORD", "FROM", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "SCHEMANAME", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ".", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "TABLENAME", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "WHERE", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", "=", "", "", False, False)
        MyPattern.AddPatternToken("STRINGLITERAL", "", "COMPAREVALUE", "", False, False)
        MyPattern.AddPatternToken("PATTERN", "", "", "ANDCOLUMNEQUALS", True, True)
        #MyPattern.AddPatternToken("SINGLECHAR", ";", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "BTEQOUT"
        MyPattern.AddPatternToken("SINGLECHAR", ".", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "SET", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "ERROROUT", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "STDOUT", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "ERROROUT"
        MyPattern.AddPatternToken("KEYWORD", "IF", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "ERRORCODE", "", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", "<", "", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ">", "", "", False, False)
        MyPattern.AddPatternToken("NUMBERLITERAL", "", "ERRORCODEVALUE", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "THEN", "", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ".", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "GOTO", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "ERRORLABEL", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", ";", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "ANDCOLUMNEQUALS"
        MyPattern.AddPatternToken("KEYWORD", "AND", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "COLUMNNAME", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", "=", "", "", False, False)
        MyPattern.AddPatternToken("STRINGLITERAL", "", "COMPAREVALUE", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "ONCOMMITPRESERVEROWS"
        MyPattern.AddPatternToken("KEYWORD", "ON", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "COMMIT", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "PRESERVE", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "ROWS", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

        MyPattern = ParsePattern()
        MyPattern.PatternName = "STARTVOLATILE"
        MyPattern.AddPatternToken("KEYWORD", "CREATE", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "MULTISET", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "VOLATILE", "", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "TABLE", "", "", False, False)
        MyPattern.AddPatternToken("VARIABLE", "", "VOLATILETABLENAME", "", False, False)
        MyPattern.AddPatternToken("KEYWORD", "AS", "", "", False, False)
        MyPattern.AddPatternToken("SINGLECHAR", "(", "", "", False, False)
        self.ValidPatterns.append(MyPattern)
        del MyPattern

class SQLTokenInPattern:
    def __init__(self):
        self.PatternName = "" # Remains empty for unmatched tokens
        self.PatternTokenidx = -1 # Remains -1 for unmatched tokens
        self.PatternTokenInterpretation = "" # Remains empty for unmatched tokens
        self.FoundPatternidx = -1 # Unique identifier for identified pattern instance within the file
        self.ParentFoundPatternidx = -1 # This pattern is direct subpattern in ParentFoundPatternidx
        self.originfilename = "" #Added for tracing and debugging purpose
        self.bline = 0
        self.bcol = 0
        self.eline = 0
        self.ecol = 0 # eline and ecol are exclusive
        self.TokenType = ""
        self.TokenContent = ""
        self.IsQuotedIdentifier = False
    
    def CsvLineFromSQLTokenInPattern(self):
        a = (self.PatternName + "," + str(self.PatternTokenidx) + ","
                  + self.PatternTokenInterpretation + ","
                  + str(self.FoundPatternidx) + "," + str(self.ParentFoundPatternidx) + ",")
        a = a + (self.originfilename 
                   + "," + str(self.bline) + "," + str(self.bcol) 
                   + "," + str(self.eline) + "," + str(self.ecol) + ","
                   + self.TokenType + ",")
        if self.IsQuotedIdentifier == True:
            a = a + '"' + self.TokenContent + '"'
        else:
            a = a + self.TokenContent
        return a;

class KeywordList:
    def __init__(self):
        self.ValidKeyWords = {"SELECT", "INSERT", "UPDATE", "CREATE",
                              "DELETE", "FROM", "AS", "REPLACE", "OR", 
                              "VIEW", "TABLE", "PRIMARY", "INDEX", "PARTITION",
                              "SET", "ERROROUT", "STDOUT", "AND", "WHERE",
                              "MULTISET", "VOLATILE", "WITH", "DATA", "GROUP", "BY",
                              "IF", "ERRORCODE", "THEN", "GOTO", "ON", "COMMIT",
                              "PRESERVE", "ROWS", "NOT", "NULL", "SUBSTR", "CASE", "WHEN",
                              "END", "COALESCE", "TO_DATE", "CAST", "BETWEEN",
                              "SESSION", "INTO"}
