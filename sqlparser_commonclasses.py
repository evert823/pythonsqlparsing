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
                              "INTO", "COLLECT", "STATISTICS", "COLUMN", "QUIT", "LABEL"}
