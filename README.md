# pythonsqlparsing
In this code, first the incoming SQL is decomposed into elements such as comments, string literals, variables etc,
--> which is stored into a list of class SQLToken.

Then having this list in place it becomes more easy to scan SQL for patterns, and to make changes in the target SQL
that are a bit more complex than search and replace
