import sys
import Lexer

class ParserXML:
    """No comment"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.xml = open(file[0:-5] + ".xml", "w")
        self.xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    def jackclass(self):
        self.xml.write("<class>\n")
        self.process('class')
        self.className()
        self.process('{')
        while self.lexer.peek() in ['static', 'field']:
            self.classVarDec()
        while self.lexer.peek() in ['constructor', 'function', 'method']:
            self.subroutineDec()
        self.process('}')
        self.xml.write("</class>\n")

    def classVarDec(self):
        self.xml.write("<classVarDec>\n")
        self.process(self.lexer.peek())
        self.type()
        self.varName()
        while self.lexer.peek() == ',':
            self.process(',')
            self.varName()
        self.process(';')
        self.xml.write("</classVarDec>\n")

    def type(self):
        self.xml.write("<type>\n")
        if self.lexer.peek() in ['int', 'char', 'boolean']:
            self.process(self.lexer.peek())
        else:
            self.className()
        self.xml.write("</type>\n")

    def subroutineDec(self):
        self.xml.write("<subroutineDec>\n")
        self.process(self.lexer.peek())
        if self.lexer.peek() == 'void':
            self.process('void')
        else:
            self.type()
        self.subroutineName()
        self.process('(')
        self.parameterList()
        self.process(')')
        self.subroutineBody()
        self.xml.write("</subroutineDec>\n")

    def parameterList(self):
        self.xml.write("<parameterList>\n")
        if self.lexer.peek() != ')':
            self.type()
            self.varName()
            while self.lexer.peek() == ',':
                self.process(',')
                self.type()
                self.varName()
        self.xml.write("</parameterList>\n")

    def subroutineBody(self):
        self.xml.write("<subroutineBody>\n")
        self.process('{')
        while self.lexer.peek() == 'var':
            self.varDec()
        self.statements()
        self.process('}')
        self.xml.write("</subroutineBody>\n")

    def varDec(self):
        self.xml.write("<varDec>\n")
        self.process('var')
        self.type()
        self.varName()
        while self.lexer.peek() == ',':
            self.process(',')
            self.varName()
        self.process(';')
        self.xml.write("</varDec>\n")

    def className(self):
        self.xml.write("<className>")
        self.process(self.lexer.peek())
        self.xml.write("</className>")

    def subroutineName(self):
        self.xml.write("<subroutineName>")
        self.process(self.lexer.peek())
        self.xml.write("</subroutineName>")

    def varName(self):
        self.xml.write("<varName>")
        self.process(self.lexer.peek())
        self.xml.write("</varName>")

    def statements(self):
        self.xml.write("<statements>\n")
        while self.lexer.peek() in ['let', 'if', 'while', 'do', 'return']:
            self.statement()
        self.xml.write("</statements>\n")

    def statement(self):
        if self.lexer.peek() == 'let':
            self.letStatement()
        elif self.lexer.peek() == 'if':
            self.ifStatement()
        elif self.lexer.peek() == 'while':
            self.whileStatement()
        elif self.lexer.peek() == 'do':
            self.doStatement()
        elif self.lexer.peek() == 'return':
            self.returnStatement()

    def letStatement(self):
        self.xml.write("<letStatement>\n")
        self.process('let')
        self.varName()
        if self.lexer.peek() == '[':
            self.process('[')
            self.expression()
            self.process(']')
        self.process('=')
        self.expression()
        self.process(';')
        self.xml.write("</letStatement>\n")

    def ifStatement(self):
        self.xml.write("<ifStatement>\n")
        self.process('if')
        self.process('(')
        self.expression()
        self.process(')')
        self.process('{')
        self.statements()
        self.process('}')
        if self.lexer.peek() == 'else':
            self.process('else')
            self.process('{')
            self.statements()
            self.process('}')
        self.xml.write("</ifStatement>\n")

    def whileStatement(self):
        self.xml.write("<whileStatement>\n")
        self.process('while')
        self.process('(')
        self.expression()
        self.process(')')
        self.process('{')
        self.statements()
        self.process('}')
        self.xml.write("</whileStatement>\n")

    def doStatement(self):
        self.xml.write("<doStatement>\n")
        self.process('do')
        self.subroutineCall()
        self.process(';')
        self.xml.write("</doStatement>\n")

    def returnStatement(self):
        self.xml.write("<returnStatement>\n")
        self.process('return')
        if self.lexer.peek() != ';':
            self.expression()
        self.process(';')
        self.xml.write("</returnStatement>\n")

    def expression(self):
        self.xml.write("<expression>\n")
        self.term()
        while self.lexer.peek() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.op()
            self.term()
        self.xml.write("</expression>\n")

    def term(self):
        self.xml.write("<term>\n")
        if self.lexer.peek().isdigit():
            self.process(self.lexer.peek())
        elif self.lexer.peek().startswith('"'):
            self.process(self.lexer.peek())
        elif self.lexer.peek() in ['true', 'false', 'null', 'this']:
            self.KeywordConstant()
        elif self.lexer.peek() == '(':
            self.process('(')
            self.expression()
            self.process(')')
        elif self.lexer.peek() in ['-', '~']:
            self.unaryOp()
            self.term()
        else:
            self.varName()
            if self.lexer.peek() == '[':
                self.process('[')
                self.expression()
                self.process(']')
            elif self.lexer.peek() == '(':
                self.subroutineCall()
            elif self.lexer.peek() == '.':
                self.subroutineCall()
        self.xml.write("</term>\n")

    def subroutineCall(self):
        self.xml.write("<subroutineCall>\n")
        if self.lexer.peek() in ['className', 'varName']:
            self.className()
            self.process('.')
        self.subroutineName()
        self.process('(')
        self.expressionList()
        self.process(')')
        self.xml.write("</subroutineCall>\n")

    def expressionList(self):
        self.xml.write("<expressionList>\n")
        if self.lexer.peek() != ')':
            self.expression()
            while self.lexer.peek() == ',':
                self.process(',')
                self.expression()
        self.xml.write("</expressionList>\n")

    def op(self):
        self.xml.write("<op>\n")
        self.process(self.lexer.peek())
        self.xml.write("</op>\n")

    def unaryOp(self):
        self.xml.write("<unaryOp>\n")
        self.process(self.lexer.peek())
        self.xml.write("</unaryOp>\n")

    def KeywordConstant(self):
        self.xml.write("<KeywordConstant>\n")
        self.process(self.lexer.peek())
        self.xml.write("</KeywordConstant>\n")

    def process(self, str):
        token = self.lexer.next()
        if token is not None and token['token'] == str:
            self.xml.write(f"<{token['type']}>{token['token']}</{token['type']}>\n")
        else:
            self.error(token)

    def error(self, token):
        if token is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()


# Define a syntax tree structure for each grammar rule in Jack language

# Structure for the entire class
class_tree = {
    "type": "class",
    "name": "",
    "variables": [],
    "subroutines": []
}

# Structure for a class variable declaration
class_var_dec = {
    "type": "classVarDec",
    "kind": "",
    "varType": "",
    "names": []
}

# Structure for a subroutine declaration
subroutine_dec = {
    "type": "subroutineDec",
    "subroutineType": "",
    "returnType": "",
    "name": "",
    "parameters": [],
    "body": {}
}

# Structure for a parameter in a parameter list
parameter = {
    "type": "parameter",
    "paramType": "",
    "name": ""
}

# Structure for a subroutine body
subroutine_body = {
    "type": "subroutineBody",
    "variables": [],
    "statements": []
}

# Structure for a local variable declaration
var_dec = {
    "type": "varDec",
    "varType": "",
    "names": []
}


statement = {
    "type": "",
    "details": {}
}

# Structure for let statement
let_statement = {
    "type": "letStatement",
    "varName": "",
    "indexExpression": None,
    "expression": {}
}

# Structure for if statement
if_statement = {
    "type": "ifStatement",
    "condition": {},
    "ifStatements": [],
    "elseStatements": []
}

# Structure for while statement
while_statement = {
    "type": "whileStatement",
    "condition": {},
    "statements": []
}

# Structure for do statement
do_statement = {
    "type": "doStatement",
    "subroutineCall": {}
}

# Structure for return statement
return_statement = {
    "type": "returnStatement",
    "expression": None
}

# Structure for an expression
expression = {
    "type": "expression",
    "terms": []
}

# Structure for a term
term = {
    "type": "term",
    "kind": "",
    "value": None,
    "subExpression": None
}

# Structure for a subroutine call
subroutine_call = {
    "type": "subroutineCall",
    "caller": None,
    "subroutineName": "",
    "arguments": []
}

# Structure for an operator
operator = {
    "type": "op",
    "operator": ""
}

# Structure for a unary operator
unary_op = {
    "type": "unaryOp",
    "operator": ""
}

# Structure for a keyword constant (true, false, null, this)
keyword_constant = {
    "type": "keywordConstant",
    "value": ""
}


if __name__ == "__main__":
    file = sys.argv[0]
    print('-----debut')
    parser = ParserXML(file)
    parser.jackclass()
    print('-----fin')
