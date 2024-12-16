import sys
import Lexer
import todot


class Parser:
    """A parser for the Jack programming language."""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)


    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        token=self.lexer.look()
        vardec=[]
        subroutine=[]
        self.process('class')
        Name=self.className()
        self.process('{')
        while self.lexer.hasNext() and self.lexer.look()['token'] in ['static', 'field']:
            vardec+=self.classVarDec()
        while self.lexer.hasNext() and self.lexer.look()['token'] in ['constructor', 'function', 'method']:
            subroutine.append(self.subroutineDec())
        self.process('}')

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        token=self.lexer.look()
        if self.lexer.hasNext() and self.lexer.look()['token'] in ['static', 'field']:
            kind=self.process(self.lexer.look()['token'])
        else:
            self.error(self.lexer.look()['token'])
        type = self.type()
        Name = []
        Name.append(self.varName())
        while self.lexer.hasNext() and self.lexer.look()['token'] ==',':
            self.process(',')
            Name.append(self.varName())
        self.process(';')
        res=[]
        for name in Name :
            res.append({'line':token['line'],'col':token['col'],'type':type,'name':name,'kind':kind})
        return res
    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        if self.lookahead('int', 'char', 'boolean'):
            return self.lexer.next()['token']
        return self.className()

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        token = self.lexer.look()
        if self.lexer.hasNext() and self.lexer.look()['token'] in ['constructor', 'function','method']:
            type=self.lexer.next()['token']
        else:
            self.error(self.lexer.look()['token'])
        if self.lexer.hasNext() and self.lexer.look()['token'] in ['void']:
            typereturn =self.process(self.lexer.look()['token'])
        else :
            typereturn =self.type()
        name=self.className()
        self.process('(')
        argument=self.parameterList()
        self.process(')')
        local,instructions=self.subroutineBody()

        return {'line': token['line'], 'col': token['col'], 'type': type, 'return': typereturn, 'name': name, 'argument' : argument, 'local':local, 'instructions': instructions}

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        line=self.lexer.look()['line']
        col=self.lexer.look()['col']
        params=[]
        if self.lexer.hasNext() and self.lexer.look()['token'] != ')':
            type=self.type()
            varName=self.varName()
            params=[{'line': line, 'col': col, 'name': varName, 'kind': 'argument', 'type': type}]
            while self.lexer.hasNext() and self.lexer.look()['token'] == ',':
                self.process(',')
                type=self.type()
                varName=self.varName()
                params.append({'line': line, 'col': col, 'name': varName, 'kind': 'argument', 'type': type})
        return params

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.process('{')
        vars = []
        while self.lookahead('var'):
            vars.append(self.varDec())
        statements = self.statements()
        self.process('}')
        return {'type': 'subroutineBody', 'vars': vars, 'statements': statements}

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        variables=[]
        self.process('var')
        varType=self.type()
        name=self.varName()
        variables.append({'type': varType, 'name': name})
        while self.lexer.hasNext() and self.lexer.look()['token'] == ',':
            self.process(',')
            name=self.varName()
            variables.append({'type': varType, 'name': name})
        self.process(';')
        return variables

    def className(self):
        """
        className: identifier
        """
        if self.lexer.hasNext() and self.lexer.look()['type'] == 'identifier':
            return self.lexer.next()['token']
        else:
            self.error(self.lexer.look()['token'])

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        token = self.lexer.next()
        if self.lexer.hasNext() and self.lexer.look()['type'] == 'identifier':
            return self.lexer.next()['token']
        else:
            self.error(token)

    def varName(self):
        """
        varName: identifier
        """
        token = self.lexer.next()
        if self.lexer.hasNext() and self.lexer.look()['type'] == 'identifier':
            return self.lexer.next()['token']
        else:
            self.error(token)

    def statements(self):
        """
        statements : statement*
        """
        stmts = []
        while self.lexer.hasNext() and self.lexer.look()['token'] in ['let', 'if', 'while','do','return']:
            stmts.append(self.statement())
        return stmts

    def statement(self):
        """
        statement : letStatement|ifStatement|whileStatement|doStatement|returnStatement
        """
        if self.lexer.look()['token'] == 'let':
            rep=self.letStatement()
        elif self.lexer.look()['token'] == 'if':
            rep=self.ifStatement()
        elif self.lexer.look()['token'] == 'while':
            rep=self.whileStatement()
        elif self.lexer.look()['token'] == 'do':
            rep=self.doStatement()
        else:
            rep=self.returnStatement()
        return rep

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        line=self.lexer.look()['line']
        colonne=self.lexer.look()['col']
        expression1=None
        self.process('let')
        name=self.varName()
        if self.lexer.hasNext() and self.lexer.look()['token'] == '[':
            self.process('[')
            expression1=self.expression()
            self.process(']')
        self.process('=')
        expression2=self.expression()
        self.process(';')
        if expression1 is None :
            return {'line': line, 'col': colonne, 'type': 'let', 'variable': name,'valeur': expression2}
        return {'line':line, 'col': colonne,'type': 'let', 'variable': name, 'indice': expression1, 'valeur':expression2}

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.process('if')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        if_statements = self.statements()
        self.process('}')
        else_statements = None
        if self.lookahead('else'):
            self.process('else')
            self.process('{')
            else_statements = self.statements()
            self.process('}')
        return {'type': 'ifStatement', 'condition': condition, 'ifStatements': if_statements,
                'elseStatements': else_statements}

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.process('while')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        body = self.statements()
        self.process('}')
        return {'line':self.lexer.look()['line'], 'col': self.lexer.look()['col'],'type': 'while', 'condition': self.expression(), 'instructions':self.statements()}

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        self.process('do')
        print(f"Expecting subroutine call after 'do'")
        call = self.subroutineCall()
        self.process(';')
        return {'type': 'doStatement', 'call': call}

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.process('return')
        expr = None
        if not self.lookahead(';'):
            expr = self.expression()
        self.process(';')
        return {'type': 'returnStatement', 'expression': expr}

    def expression(self):
        """
        Parses an expression.
        expression: term (op term)*
        """
        expr = {'type': 'expression', 'terms': []}

        # Parse the first term
        expr['terms'].append(self.term())

        # Parse (op term)* - handle additional terms
        while self.lookahead('+', '-', '*', '/', '&', '|', '<', '>', '='):  # Check for operator
            op = self.processOperator()
            term = self.term()  # Parse the next term
            expr['terms'].append({'op': op})
            expr['terms'].append(term)

        return expr

    def term(self):
        """
        term : integerConstant | stringConstant | keywordConstant
               | varName | varName '[' expression ']' | subroutineCall
               | '(' expression ')' | unaryOp term
        """
        res={}
        res["line"]=self.lexer.look()['line']
        res["col"]=self.lexer.look()['col']
        if self.lexer.hasNext() and self.lexer.look()['token'] in ['true', 'false', 'null', 'this']:
            res["type"]="constant"
            res["valeur"]=self.KeywordConstant()
            return res
        elif self.lexer.hasNext() and self.lexer.look()['token'] in ['-', '~']:
            res["type"]=self.lexer.next()['token']
            res["valeur"]=self.term()
            return res
        elif self.lexer.hasNext() and self.lexer.look()['token'] == '(':
            self.process('(')
            res["type"]="expression"
            res["valeur"]=self.expression()
            self.process(')')
            return res
        elif self.lexer.hasNext() and self.lexer.look()['type'] in ['StringConstant', 'IntegerConstant']:
            token=self.lexer.next()
            res["type"]=token['type']
            res["valeur"]=token['token']
            return res
        elif self.lexer.hasNext() and self.lexer.look()['type'] == 'identifier':
            if self.lexer.hasNext() and self.lexer.look2()['token'] == '[':
                res["type"]="tableau"
                res["valeur"]=self.varName()
                self.process('[')
                res["indice"]=self.expression()
                self.process(']')
                return res
            elif self.lexer.hasNext() and self.lexer.look2()['token'] in ['(', '.']:
                res["type"]="subroutineCall"
                res["valeur"]=self.subroutineCall()
                return res
            else:
                res["valeur"]=self.varName()
                res["type"]="variable"
                return res

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                        | (className|varName) '.' subroutineName '(' expressionList ')'
        """
        identifier = self.process(self.lexer.look()['token'])  # Consume identifier
        if self.lookahead() == '.':
            self.process('.')  # Consume '.'
            subroutine_name = self.subroutineName()
            self.process('(')
            expr_list = self.expressionList()
            self.process(')')
            return {
                'type': 'subroutineCall',
                'caller': identifier,
                'subroutineName': subroutine_name,
                'arguments': expr_list
            }
        elif self.lookahead() == '(':
            self.process('(')
            expr_list = self.expressionList()
            self.process(')')
            return {
                'type': 'subroutineCall',
                'subroutineName': identifier,
                'arguments': expr_list
            }
        else:
            self.error(self.lexer.look())

    def lookahead_identifier(self):
        """
        Checks if the next token is an identifier.
        Returns:
            bool: True if the next token's type is 'identifier', otherwise False.
        """
        next_token = self.lookahead()  # Peek at the next token without consuming it
        return next_token and next_token.get('type') == 'identifier'

    def lookahead_keyword(self, expected_keyword):
        """
        Checks if the next token is a specific keyword.
        Args:
            expected_keyword (str): The keyword to check for.
        Returns:
            bool: True if the next token matches the keyword, otherwise False.
        """
        next_token = self.lookahead()
        return next_token and next_token.get('type') == 'keyword' and next_token.get('token') == expected_keyword

    def lookahead_symbol(self, expected_symbol):
        """
        Checks if the next token is a specific symbol.
        Args:
            expected_symbol (str): The symbol to check for (e.g., '(' or ')').
        Returns:
            bool: True if the next token matches the symbol, otherwise False.
        """
        next_token = self.lookahead()
        return next_token and next_token.get('type') == 'symbol' and next_token.get('token') == expected_symbol

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        expressions = []
        if self.lookahead() != ')':  # If it's not an empty list
            expressions.append(self.expression())
            while self.lookahead() == ',':
                self.process(',')  # Consume ','
                expressions.append(self.expression())
        return expressions

    def op(self):
        """
        op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """
        return self.process(self.lexer.next()['token'])

    def unaryOp(self):
        """
        unaryOp: '-' | '~'
        """
        token = self.lexer.next()
        if token['token'] in ('-', '~'):
            return token['token']
        else:
            self.error(token)

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true'|'false'|'null'|'this'
        """
        return self.lexer.next()['token']

    def process(self, expected):
        token = self.lexer.next()
        if token is not None and token['token'] == expected:
            return token['token']
        else:
            self.error(token)

    def processOperator(self):
        """
        Consumes an operator token and returns its value.
        Valid operators: +, -, *, /, &, |, <, >, =
        """
        token = self.lexer.look()  # Peek at the current token
        if token['token'] in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            return self.lexer.next()['token']  # Consume and return the operator
        else:
            self.error(f"Unexpected token: {token}, expected an operator.")

    def processIdentifier(self):
        token = self.lexer.next()
        if token is not None and token['type'] == 'identifier':
            return token['token']
        else:
            self.error(token)

    def lookahead(self, *expected):
        """
        Checks if the next token matches one of the expected tokens.
        Supports both token and type matching.
        Expected can include:
        - Strings (token values)
        - Tuples (type, token value)
        """
        token = self.lexer.look()
        if token is None:
            print(f"Lookahead failed: No token available, expected {expected}")
            return False

        for exp in expected:
            if isinstance(exp, tuple):  # Match (type, value)
                if token['type'] == exp[0] and token['token'] == exp[1]:
                    print(f"Lookahead matched: {token} (expected {exp})")
                    return True
            elif token['token'] == exp:  # Match token value
                print(f"Lookahead matched: {token['token']} (expected {exp})")
                return True

        print(f"Lookahead failed: {token} not in {expected}")
        return False

    def process(self, expected):
        """Consumes the next token if it matches the expected value."""
        token = self.lexer.next()
        if token['token'] == expected:
            return token['token']
        else:
            raise SyntaxError(f"Expected {expected}, got {token}")

    def error(self, token):
        if token is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = Parser(file)
    arbre = parser.jackclass()
    todot = todot.Todot(file)
    todot.todot(arbre)
    print('-----fin')


