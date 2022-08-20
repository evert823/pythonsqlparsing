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

    def PatternContent(self):
        if self.TokenType in ["KEYWORD", "SINGLECHAR"]:
            return self.TokenContent
        else:
            return self.TokenType

    def CleanContent(self):
        if self.TokenType in ["STRINGLITERAL"]:
            return "'" + self.TokenContent.replace("'", "''") + "'"
        elif self.TokenType in ["VARIABLE"] and self.IsQuotedIdentifier == True:
            return '"' + self.TokenContent + '"'
        else:
            return self.TokenContent

class SQLStatement:
    def __init__(self):
        self.b_i = -1 #inclusive
        self.e_i = -1 #exclusive
        self.alltokens = []
        self.tokens = [] #all tokens without the comments
        self.StatementPattern = ""
        self.CleanStatement = ""


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
                              "INTO", "COLLECT", "STATISTICS", "COLUMN", "QUIT", "LABEL", "VALUES"}
