from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import SQLStatement
from sqlparser_commonclasses import NewInserts

#
# 1st abstraction level = CleanStatement: comments removed, whitespaces and line-ends standardized
# 2nd abstraction level = Instances of string literals, number literals, identifiers represented as "STRINGLITERAL", "NUMBERLITERAL", "IDENTIFIER"
# 3rd abstraction level = Instances of subqueries represented as "SUBQUERY", symantically equivalent keywords mappped together
#

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
            if pFoundStatements[i].Abstraction02[0:63] == "CREATE SET VOLATILE TABLE IDENTIFIER AS ( WITH IDENTIFIER AS ( ":
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
    def FindAsAlias(self, pSearchArg, pListOfStatements, pstnr, pFoundTokens):
        i = 0
        while i < len(pListOfStatements[pstnr].tokens):
            ff = pListOfStatements[pstnr].tokens[i]

            InSubQuery = False
            for stnr_sub in range(pstnr + 1, len(pListOfStatements)):
                if pListOfStatements[stnr_sub].ParentStatement == pstnr:
                    if ff in pListOfStatements[stnr_sub].tokens:
                        InSubQuery = True

            if (pFoundTokens[ff].TokenType == "IDENTIFIER" and InSubQuery == False
                and pFoundTokens[ff].TokenContent.upper() == pSearchArg.upper() and i >= 4):
                ffm4 = pListOfStatements[pstnr].tokens[i - 4]
                ffm3 = pListOfStatements[pstnr].tokens[i - 3]
                ffm2 = pListOfStatements[pstnr].tokens[i - 2]
                ffm1 = pListOfStatements[pstnr].tokens[i - 1]

                if (pFoundTokens[ffm4].TokenType == "IDENTIFIER" and 
                    pFoundTokens[ffm3].TokenType == "SINGLECHAR" and pFoundTokens[ffm3].TokenContent == "." and
                    pFoundTokens[ffm2].TokenType == "IDENTIFIER" and 
                    pFoundTokens[ffm1].TokenType == "KEYWORD" and pFoundTokens[ffm1].TokenContent == "AS"):
                    return pFoundTokens[ffm4].TokenContent + pFoundTokens[ffm3].TokenContent + pFoundTokens[ffm2].TokenContent
                if (pFoundTokens[ffm3].TokenType == "IDENTIFIER" and 
                    pFoundTokens[ffm2].TokenType == "SINGLECHAR" and pFoundTokens[ffm2].TokenContent == "." and
                    pFoundTokens[ffm1].TokenType == "IDENTIFIER"):
                    return pFoundTokens[ffm3].TokenContent + pFoundTokens[ffm2].TokenContent + pFoundTokens[ffm1].TokenContent
                if (pFoundTokens[ffm2].TokenType == "IDENTIFIER" and 
                    pFoundTokens[ffm1].TokenType == "KEYWORD" and pFoundTokens[ffm1].TokenContent == "AS"):
                    return pFoundTokens[ffm2].TokenContent
                if (pFoundTokens[ffm1].TokenType == "IDENTIFIER"):
                    return pFoundTokens[ffm1].TokenContent
            i += 1
        return ""

#-----------------------------------------------------------------------------------------------
    def SearchCleanStatement(self, pSearchArg, pListOfStatements, pstnr, pFoundTokens):
        #This returns a first match in the entire statement but ignores the possibility of multiple matches
        #within the same statement. Later we may need to extend this.
        MyResult = []
        if pListOfStatements[pstnr].CleanStatement.find(pSearchArg) == -1:
            return MyResult
        
        a = pSearchArg.split(" ")
        n = len(a)
        if a[n - 1] == "":
            a.pop()
            n -= 1

        AllIdentified = False
        i = -1
        while AllIdentified == False:
            i += 1
            Identified = True
            for m in range(n):
                ft = pListOfStatements[pstnr].tokens[i + m]
                if pFoundTokens[ft].CleanContent() != a[m]:
                    Identified = False
            if Identified == True:
                AllIdentified = True

        assert AllIdentified == True

        for m in range(n):
            MyResult.append(pListOfStatements[pstnr].tokens[i + m])

        return MyResult
#-----------------------------------------------------------------------------------------------
    def SearchAbstraction02(self, pSearchArg, pListOfStatements, pstnr, pFoundTokens):
        #This returns a first match in the entire statement but ignores the possibility of multiple matches
        #within the same statement. Later we may need to extend this.
        MyResult = []
        if pListOfStatements[pstnr].Abstraction02.find(pSearchArg) == -1:
            return MyResult
        
        a = pSearchArg.split(" ")
        n = len(a)
        if a[n - 1] == "":
            a.pop()
            n -= 1

        AllIdentified = False
        i = -1
        while AllIdentified == False:
            i += 1
            Identified = True
            for m in range(n):
                ft = pListOfStatements[pstnr].tokens[i + m]
                if pFoundTokens[ft].PatternContent() != a[m]:
                    Identified = False
            if Identified == True:
                AllIdentified = True

        assert AllIdentified == True

        for m in range(n):
            MyResult.append(pListOfStatements[pstnr].tokens[i + m])

        return MyResult
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_Stats02(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("COLLECT STATISTICS IDENTIFIER . IDENTIFIER FROM IDENTIFIER",
                                       pListOfStatements, pstnr, pFoundTokens)
        if len(a) == 0:
            a = self.SearchAbstraction02("COLLECT STATS IDENTIFIER . IDENTIFIER FROM IDENTIFIER",
                                           pListOfStatements, pstnr, pFoundTokens)
        if len(a) > 0:
            ff1 = a[2]
            ff2 = a[3]
            ff3 = a[4]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
            return;

        a = self.SearchAbstraction02("COLLECT STATISTICS IDENTIFIER FROM IDENTIFIER",
                                       pListOfStatements, pstnr, pFoundTokens)
        if len(a) == 0:
            a = self.SearchAbstraction02("COLLECT STATS IDENTIFIER FROM IDENTIFIER",
                                           pListOfStatements, pstnr, pFoundTokens)
        if len(a) > 0:
            ff1 = a[2]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            return;
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_Stats(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("COLLECT STATISTICS", pListOfStatements, pstnr, pFoundTokens)
        if len(a) == 0:
            a = self.SearchAbstraction02("COLLECT STATS", pListOfStatements, pstnr, pFoundTokens)
        
        if len(a) == 0:
            return
        
        b = self.SearchAbstraction02("ON IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        c = self.SearchAbstraction02("ON IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)

        if len(c) == 0:
            return

        if len(b) == 0:
            ff = c[1]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            ff1 = b[1]
            ff2 = b[2]
            ff3 = b[3]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_Update01(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("UPDATE IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(a) > 0:
            ff1 = a[1]
            ff2 = a[2]
            ff3 = a[3]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
            return

        a = self.SearchAbstraction02("UPDATE IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(a) > 0 and pListOfStatements[pstnr].Abstraction03.find("FROM") == -1:
            ff1 = a[1]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            return

        a = self.SearchAbstraction02("UPDATE IDENTIFIER FROM", pListOfStatements, pstnr, pFoundTokens)

        if len(a) == 0:
            return
        
        ff = a[1]
        s = self.FindAsAlias(pFoundTokens[ff].TokenContent, pListOfStatements, pstnr, pFoundTokens)

        if s == "":
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            pListOfStatements[pstnr].QualifiedTargetObjectName = s
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_Delete02(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("DELETE IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(a) > 0:
            ff1 = a[1]
            ff2 = a[2]
            ff3 = a[3]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
            return

        a = self.SearchAbstraction02("DELETE IDENTIFIER FROM", pListOfStatements, pstnr, pFoundTokens)

        if len(a) == 0:
            return
        
        ff = a[1]
        s = self.FindAsAlias(pFoundTokens[ff].TokenContent, pListOfStatements, pstnr, pFoundTokens)

        if s == "":
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            pListOfStatements[pstnr].QualifiedTargetObjectName = s
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_Delete01(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("DELETE FROM IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)

        if len(a) == 0:
            return
        
        b = self.SearchAbstraction02("DELETE FROM IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        
        if len(b) == 0:
            ff = a[2]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            ff1 = b[2]
            ff2 = b[3]
            ff3 = b[4]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_CreateTable(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("CREATE", pListOfStatements, pstnr, pFoundTokens)
        b = self.SearchAbstraction02("TABLE IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        c = self.SearchAbstraction02("TABLE IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)

        if len(a) == 0 or len(b) == 0:
            return

        if len(c) == 0:
            ff = b[1]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            ff1 = c[1]
            ff2 = c[2]
            ff3 = c[3]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_View(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("REPLACE VIEW IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(a) == 0:
            a = self.SearchAbstraction02("CREATE VIEW IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)

        if len(a) == 0:
            return
        
        b = self.SearchAbstraction02("REPLACE VIEW IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(b) == 0:
            b = self.SearchAbstraction02("CREATE VIEW IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        
        if len(b) == 0:
            ff = a[2]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            ff1 = b[2]
            ff2 = b[3]
            ff3 = b[4]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName_Insert_Merge(self, pFoundTokens, pListOfStatements, pstnr):
        a = self.SearchAbstraction02("INSERT INTO IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(a) == 0:
            a = self.SearchAbstraction02("MERGE INTO IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)

        if len(a) == 0:
            return
        
        b = self.SearchAbstraction02("INSERT INTO IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        if len(b) == 0:
            b = self.SearchAbstraction02("MERGE INTO IDENTIFIER . IDENTIFIER", pListOfStatements, pstnr, pFoundTokens)
        
        if len(b) == 0:
            ff = a[2]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff].TokenContent
        else:
            ff1 = b[2]
            ff2 = b[3]
            ff3 = b[4]
            pListOfStatements[pstnr].QualifiedTargetObjectName = pFoundTokens[ff1].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff2].TokenContent
            pListOfStatements[pstnr].QualifiedTargetObjectName += pFoundTokens[ff3].TokenContent
#-----------------------------------------------------------------------------------------------
    def Set_QualifiedTargetObjectName(self, pFoundTokens, pListOfStatements):
        for stnr in range(len(pListOfStatements)):
            if pListOfStatements[stnr].ParentStatement == -1:
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_Insert_Merge(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_View(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_CreateTable(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_Delete01(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_Delete02(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_Update01(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_Stats(pFoundTokens, pListOfStatements, stnr)
                if pListOfStatements[stnr].QualifiedTargetObjectName == "":
                    self.Set_QualifiedTargetObjectName_Stats02(pFoundTokens, pListOfStatements, stnr)
#-----------------------------------------------------------------------------------------------
    def StatementUsesObject(self, pFoundTokens, pListOfStatements, pstnr, pTableViewName):
        schemaname = ""
        tableviewname = ""
        a = pTableViewName.split(".")
        if len(a) == 1:
            tableviewname = a[0]
        else:
            schemaname = a[0]
            tableviewname = a[1]

        if pListOfStatements[pstnr].CleanStatement.upper().find(" " + tableviewname.upper() + " ") > -1:
            for i in range(len(pListOfStatements[pstnr].tokens)):
                ff = pListOfStatements[pstnr].tokens[i]
                if pFoundTokens[ff].TokenType == "IDENTIFIER" and pFoundTokens[ff].TokenContent.upper() == tableviewname.upper():
                    if schemaname == "":
                        return True
                    if i < 2:
                        return True
                    ffm1 = pListOfStatements[pstnr].tokens[i - 1]
                    ffm2 = pListOfStatements[pstnr].tokens[i - 2]
                    if pFoundTokens[ffm1].TokenType == "SINGLECHAR" and pFoundTokens[ffm1].TokenContent == ".":
                        pass
                    else:
                        return True
                    if pFoundTokens[ffm2].TokenType != "IDENTIFIER":
                        return True
                    if pFoundTokens[ffm2].TokenContent.upper() == schemaname.upper():
                        return True
                    else:
                        return False

        return False
#-----------------------------------------------------------------------------------------------
    def BuildAbstraction03(self, pFoundTokens, pSubqueryTree):
        #Here we represent a subquery by "SUBQUERY"
        for stnr in range(len(pSubqueryTree)):
            cursor = pSubqueryTree[stnr].b_i
            stnr2 = stnr + 1

            while cursor < pSubqueryTree[stnr].e_i:
                while stnr2 < len(pSubqueryTree) and pSubqueryTree[stnr2].ParentStatement != stnr:
                    stnr2 += 1
                if stnr2 >= len(pSubqueryTree):
                    for i in range(cursor, pSubqueryTree[stnr].e_i):
                        if i in pSubqueryTree[stnr].tokens:
                            pSubqueryTree[stnr].Abstraction03 += pFoundTokens[i].PatternContent() + " "
                    cursor = pSubqueryTree[stnr].e_i
                else:
                    for i in range(cursor, pSubqueryTree[stnr2].b_i):
                        if i in pSubqueryTree[stnr].tokens:
                            pSubqueryTree[stnr].Abstraction03 += pFoundTokens[i].PatternContent() + " "
                    pSubqueryTree[stnr].Abstraction03 += "SUBQUERY "
                    cursor = pSubqueryTree[stnr2].e_i
                    stnr2 += 1
        #Next to be implemented here: semantically interchangeable keywords to be represented by one common tag.
        #E.g. MIN() and MAX(), or LOWER() and UPPER()
#-----------------------------------------------------------------------------------------------
    def IdentifySubqueries(self, pFoundTokens, pSubqueryTree, pparentnr):
        i = 0
        while i < len(pSubqueryTree[pparentnr].tokens) - 1:
            ft_i = pSubqueryTree[pparentnr].tokens[i]
            ft_ip1 = pSubqueryTree[pparentnr].tokens[i + 1]
            NoSubqueryStart = False
            if i > 0:
                ft_im1 = pSubqueryTree[pparentnr].tokens[i - 1]
                if pFoundTokens[ft_im1].TokenType == "KEYWORD" and pFoundTokens[ft_im1].TokenContent in ["AS", "USING"]:
                    NoSubqueryStart = True

            if (pFoundTokens[ft_i].TokenType == "SINGLECHAR" and pFoundTokens[ft_i].TokenContent == "("
                                                     and NoSubqueryStart == False):
                if pFoundTokens[ft_ip1].TokenType == "KEYWORD" and pFoundTokens[ft_ip1].TokenContent in ["SELECT", "SEL"]:
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
                                mysq.Abstraction02 += pFoundTokens[ft].PatternContent() + " "
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
                s.Abstraction02 += pFoundTokens[i].PatternContent() + " "
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
