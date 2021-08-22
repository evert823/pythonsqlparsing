class SQLToken:
    def __init__(self):
        self.originfilename = "" #Added for tracing and debugging purpose
        self.bline = 0
        self.bcol = 0
        self.eline = 0
        self.ecol = 0 # eline and ecol are exclusive
        self.TokenType = ""
        self.TokenContent = ""
    
    def CsvLineFromToken(self):
        a = (self.originfilename 
                   + "," + str(self.bline) + "," + str(self.bcol) 
                   + "," + str(self.eline) + "," + str(self.ecol) + ","
                   + self.TokenType + "," + self.TokenContent)
        return a;

