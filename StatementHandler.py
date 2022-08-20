from sqlparser_commonclasses import SQLToken
from sqlparser_commonclasses import SQLStatement

class StatementHandler:
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
