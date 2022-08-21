from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import SQLStatement
from sqlparser_commonclasses import NewInserts

class StatementHandler:

    def AddStatsForVolatileTable(self, pFoundTokens, pFoundStatements, pvtname):
        MyNewInsert = NewInserts()
        i_create = -1
        for i in range(len(pFoundStatements)):
            if pFoundStatements[i].CleanStatement.upper().find("VOLATILE TABLE " + pvtname + " ") > -1:
                i_create = i
        
        if i_create == -1:
            return MyNewInsert

        if i_create < len(pFoundStatements) - 1 and pFoundStatements[i_create + 1].CleanStatement == "IF ERRORCODE < > 0 THEN . GOTO Error_Exit ; ":
            i_insert = pFoundStatements[i_create + 1].e_i - 1
        else:
            i_insert = pFoundStatements[i_create].e_i - 1

        s = pFoundStatements[i_create].CleanStatement
        c1 = s.find(" PRIMARY INDEX ( ") + 17
        if c1 < 17:
            return MyNewInsert

        c2 = s[c1:].find(" ) ")
        a = s[c1:c1 + c2].split(",")
        picolumns = []
        for i in range(len(a)):
            picolumns.append(a[i].strip())
        
        if len(picolumns) == 0:
            return MyNewInsert
        
        MyNewInsert.aftertoken = i_insert

        csline = "COLLECT STATISTICS "

        for i in range(len(picolumns)):
            csline += "COLUMN(" + picolumns[i] + ")"
            if i < len(picolumns) - 1:
                csline += ", "
            else:
                csline += " "
        
        csline += "ON " + pvtname + ";"
        MyNewInsert.insertlines.append(csline)
        MyNewInsert.insertlines.append("IF ERRORCODE <> 0 THEN .GOTO Error_Exit;")

        return MyNewInsert
    
    def FindVolatileTables(self, pFoundStatements):
        volatiletables = []
        for s in pFoundStatements:
            if s.CleanStatement.find("VOLATILE TABLE") > -1:
                c1 = s.CleanStatement.find(" VOLATILE TABLE ") + 16
                c2 = s.CleanStatement[c1:].find(" ")
                volatiletables.append(s.CleanStatement[c1:c1 + c2].upper())
        return volatiletables

    def FindCollectStatsOnVolatileTables(self, pFoundStatements):
        volatiletables = []
        for s in pFoundStatements:
            if (s.CleanStatement.find("COLLECT STATISTICS") > -1 or s.CleanStatement.find("COLLECT STATS") > -1) and s.CleanStatement.find("{") == -1:
                c1 = s.CleanStatement.find(" ON ") + 4
                c2 = s.CleanStatement[c1:].find(" ")
                volatiletables.append(s.CleanStatement[c1:c1 + c2].upper())
        return volatiletables

    def BuildStatements(self, pFoundTokens):

        FoundStatements = []

        s = SQLStatement()

        for i in range(len(pFoundTokens)):
            if s.b_i == -1:
                s.b_i = i
            
            s.alltokens.append(i)

            if pFoundTokens[i].TokenType in ["SINGLELINECOMMENT", "MULTILINECOMMENT"]:
                pass
            else:
                s.tokens.append(i)
                s.StatementPattern += pFoundTokens[i].PatternContent() + " "
                s.CleanStatement += pFoundTokens[i].CleanContent() + " "
            if pFoundTokens[i].TokenType == "SINGLECHAR" and pFoundTokens[i].TokenContent == ";":
                s.e_i = i + 1 #e_i is exclusive
                FoundStatements.append(s)
                del s
                s = SQLStatement()
        
        if len(s.alltokens) > 0:
            s.e_i = i + 1 #e_i is exclusive
            FoundStatements.append(s)

        return FoundStatements
