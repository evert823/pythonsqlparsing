# pythonsqlparsing
In this code, first the incoming SQL is decomposed into elements such as comments, string literals, variables etc,
--> which is stored into a list of class SQLToken.
Then there is a class PatternList, which should contain patterns that describe valid SQL syntax.
Patterns can include repeating tokens, optional tokens and subpatterns.
Then class SQLPatternMatcher has a method that searches for the patterns in the incoming SQL.

To test this:
python sqlparser_main.py myinutfolder myoutputfolder
