from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import SQLStatement
from sqlparser_commonclasses import NewInserts

class StatementHandler:
#-----------------------------------------------------------------------------------------------
    def FindFirstStatements(self, pFoundTokens, pFoundStatements, file_lll_rpt):
        for i in range(len(pFoundStatements)):
            for j in range(len(pFoundStatements[i].tokens)):
                ft = pFoundStatements[i].tokens[j]

                if j == 0:
                    file_lll_rpt.write(pFoundTokens[ft].PatternContent() + "\tFirst token of a statement" + pFoundTokens[ft].CsvLineFromToken() + "\n")
                if j > 0:
                    ft_prev = pFoundStatements[i].tokens[j - 1]
                    if pFoundTokens[ft_prev].TokenType == "SINGLECHAR" and pFoundTokens[ft_prev].TokenContent == "(":
                        file_lll_rpt.write(pFoundTokens[ft].PatternContent() + "\tFirst token after (" + pFoundTokens[ft].CsvLineFromToken() + "\n")
#-----------------------------------------------------------------------------------------------
    def AlterSQL(self, pFoundTokens, pFoundStatements):
        for i in range(len(pFoundStatements)):
            if pFoundStatements[i].StatementPattern[0:61] == "CREATE SET VOLATILE TABLE IDENTIFIER AS ( WITH IDENTIFIER AS ( ":
                ft = pFoundStatements[i].b_i
                s = pFoundTokens[ft].CsvLineFromToken()
                print(s + " " + pFoundStatements[i].CleanStatement)
#-----------------------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------
    def FindVolatileTables(self, pFoundStatements):
        volatiletables = []
        for s in pFoundStatements:
            if s.CleanStatement.find("VOLATILE TABLE") > -1:
                c1 = s.CleanStatement.find(" VOLATILE TABLE ") + 16
                c2 = s.CleanStatement[c1:].find(" ")
                volatiletables.append(s.CleanStatement[c1:c1 + c2].upper())
        return volatiletables
#-----------------------------------------------------------------------------------------------
    def FindCollectStatsOnVolatileTables(self, pFoundStatements):
        volatiletables = []
        for s in pFoundStatements:
            if (s.CleanStatement.find("COLLECT STATISTICS") > -1 or s.CleanStatement.find("COLLECT STATS") > -1) and s.CleanStatement.find("{") == -1:
                c1 = s.CleanStatement.find(" ON ") + 4
                c2 = s.CleanStatement[c1:].find(" ")
                volatiletables.append(s.CleanStatement[c1:c1 + c2].upper())
        return volatiletables
#-----------------------------------------------------------------------------------------------
    def IdentifySubqueries(self, pFoundTokens, pSubqueryTree, pparentnr):
        i = 0
        while i < len(pSubqueryTree[pparentnr].tokens) - 1:
            ft_i = pSubqueryTree[pparentnr].tokens[i]
            ft_ip1 = pSubqueryTree[pparentnr].tokens[i + 1]
            CreateTable = False
            if i > 0:
                ft_im1 = pSubqueryTree[pparentnr].tokens[i - 1]
                if pFoundTokens[ft_im1].TokenType == "KEYWORD" and pFoundTokens[ft_im1].TokenContent == "AS":
                    CreateTable = True

            if pFoundTokens[ft_i].TokenType == "SINGLECHAR" and pFoundTokens[ft_i].TokenContent == "(" and CreateTable == False:
                if pFoundTokens[ft_ip1].TokenType == "KEYWORD" and pFoundTokens[ft_ip1].TokenContent == "SELECT":
                    InSubQuery = True
                    j = i + 2
                    slevel = 0
                    while InSubQuery == True and j < len(pSubqueryTree[pparentnr].tokens):
                        ft_j = pSubqueryTree[pparentnr].tokens[j]
                        if pFoundTokens[ft_j].TokenType == "SINGLECHAR" and pFoundTokens[ft_j].TokenContent == "(":
                            slevel += 1
                        if pFoundTokens[ft_j].TokenType == "SINGLECHAR" and pFoundTokens[ft_j].TokenContent == ")":
                            slevel -= 1
                        if slevel < 0:
                            InSubQuery = False
                        j += 1
                    if InSubQuery == False:
                        mysq = SQLStatement()
                        mysq.b_i = ft_ip1
                        mysq.e_i = ft_j
                        i = j - 1
                        for ft in pSubqueryTree[pparentnr].alltokens:
                            if ft in range(mysq.b_i, mysq.e_i):
                                mysq.alltokens.append(ft)
                        for ft in pSubqueryTree[pparentnr].tokens:
                            if ft in range(mysq.b_i, mysq.e_i):
                                mysq.tokens.append(ft)
                                mysq.StatementPattern += pFoundTokens[ft].PatternContent() + " "
                                mysq.CleanStatement += pFoundTokens[ft].CleanContent() + " "
                        mysq.ParentStatement = pparentnr
                        mysq.NestedLevel = pSubqueryTree[pparentnr].NestedLevel + 1
                        pSubqueryTree.append(mysq)
                        youridx = len(pSubqueryTree) - 1
                        self.IdentifySubqueries(pFoundTokens, pSubqueryTree, youridx)
            i += 1
#-----------------------------------------------------------------------------------------------
    def BuildSubqueryTree(self, pFoundTokens, pFoundStatements):
        SubqueryTree = []

        for st_nr in range(len(pFoundStatements)):
            SubqueryTree.append(pFoundStatements[st_nr])
            youridx = len(SubqueryTree) - 1
            self.IdentifySubqueries(pFoundTokens, SubqueryTree, youridx)

        return SubqueryTree
#-----------------------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------
