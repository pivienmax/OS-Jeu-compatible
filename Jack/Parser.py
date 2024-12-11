import Lexer
import sys
import todot

def unaryOp():
    """
    unaryop : '-'|'~'
    """
    return ['-', '~']


class Parser:
    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.syntax_tree = None  # Root of the syntax tree

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.process('class')
        class_name = self.className()
        self.process('{')
        class_vars = []
        while self.lexer.peek()['token'] in ['static', 'field']:
            class_vars.append(self.classVarDec())
        subroutines = []
        while self.lexer.peek()['token'] in ['constructor', 'function', 'method']:
            subroutines.append(self.subroutineDec())
        self.process('}')
        return {'type': 'class', 'name': class_name, 'classVars': class_vars, 'subroutines': subroutines}

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        kind = self.process(self.lexer.peek()['token'])
        var_type = self.type()
        names = [self.varName()]
        while self.lexer.peek()['token'] == ',':
            self.process(',')
            names.append(self.varName())
        self.process(';')
        return {'type': 'classVarDec', 'kind': kind, 'varType': var_type, 'names': names}

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        token = self.lexer.peek()
        if token['token'] in ['int', 'char', 'boolean']:
            return self.process(token['token'])
        return self.className()

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        kind = self.process(self.lexer.peek()['token'])
        return_type = self.process('void') if self.lexer.peek()['token'] == 'void' else self.type()
        name = self.subroutineName()
        self.process('(')
        parameters = self.parameterList()
        self.process(')')
        body = self.subroutineBody()
        return {'type': 'subroutineDec', 'kind': kind, 'returnType': return_type, 'name': name, 'parameters': parameters, 'body': body}

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        parameters = []
        if self.lexer.peek()['token'] != ')':
            param_type = self.type()
            param_name = self.varName()
            parameters.append({'type': param_type, 'name': param_name})
            while self.lexer.peek()['token'] == ',':
                self.process(',')
                param_type = self.type()
                param_name = self.varName()
                parameters.append({'type': param_type, 'name': param_name})
        return parameters

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.process('{')
        vars = []
        while self.lexer.peek()['token'] == 'var':
            vars.append(self.varDec())
        statements = self.statements()
        self.process('}')
        return {'type': 'subroutineBody', 'vars': vars, 'statements': statements}

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.process('var')
        var_type = self.type()
        names = [self.varName()]
        while self.lexer.peek()['token'] == ',':
            self.process(',')
            names.append(self.varName())
        self.process(';')
        return {'type': 'varDec', 'varType': var_type, 'names': names}

    def className(self):
        """
        className: identifier
        """
        return self.process(self.lexer.peek()['token'])

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        return self.process(self.lexer.peek()['token'])

    def varName(self):
        """
        varName: identifier
        """
        return self.process(self.lexer.peek()['token'])

    def statements(self):
        """
        statements : statements*
        """
        stmts = []
        while self.lexer.peek()['token'] in ['let', 'if', 'while', 'do', 'return']:
            stmts.append(self.statement())
        return stmts

    def statement(self):
        """
        statement : letStatements|ifStatement|whileStatement|doStatement|returnStatement
        """
        token = self.lexer.peek()['token']
        if token == 'let':
            return self.letStatement()
        elif token == 'if':
            return self.ifStatement()
        elif token == 'while':
            return self.whileStatement()
        elif token == 'do':
            return self.doStatement()
        elif token == 'return':
            return self.returnStatement()
        else:
            self.error(token)

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.process('let')
        var_name = self.varName()
        index_expr = None
        if self.lexer.peek()['token'] == '[':
            self.process('[')
            index_expr = self.expression()
            self.process(']')
        self.process('=')
        expr = self.expression()
        self.process(';')
        return {'type': 'letStatement', 'varName': var_name, 'index': index_expr, 'expression': expr}

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.process('if')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        if_body = self.statements()
        self.process('}')
        else_body = None
        if self.lexer.peek()['token'] == 'else':
            self.process('else')
            self.process('{')
            else_body = self.statements()
            self.process('}')
        return {'type': 'ifStatement', 'condition': condition, 'ifBody': if_body, 'elseBody': else_body}

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
        return {'type': 'whileStatement', 'condition': condition, 'body': body}

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        self.process('do')
        call = self.subroutineCall()
        self.process(';')
        return {'type': 'doStatement', 'call': call}

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.process('return')
        expr = None
        if self.lexer.peek()['token'] != ';':
            expr = self.expression()
        self.process(';')
        return {'type': 'returnStatement', 'expression': expr}

    def expression(self):
        """
        expression : term (op term)*
        """
        terms = [self.term()]
        ops = []
        while self.lexer.peek()['token'] in unaryOp():
            ops.append(self.process(self.lexer.peek()['token']))
            terms.append(self.term())
        return {'type': 'expression', 'terms': terms, 'ops': ops}

    def term(self):
        """
        term : integerConstant|stringConstant|keywordConstant
                |varName|varName '[' expression ']'|subroutineCall
                | '(' expression ')' | unaryOp term
        """
        token = self.lexer.peek()
        if token['type'] == 'integerConstant':
            return self.process(token['token'])
        elif token['type'] == 'stringConstant':
            return self.process(token['token'])
        elif token['token'] in ['true', 'false', 'null', 'this']:
            return self.process(token['token'])
        elif token['type'] == 'identifier':
            next_token = self.lexer.peek()
            if next_token['token'] == '[':
                var_name = self.process(token['token'])
                self.process('[')
                index_expr = self.expression()
                self.process(']')
                return {'type': 'arrayAccess', 'varName': var_name, 'index': index_expr}
            elif next_token['token'] in ['(', '.']:
                return self.subroutineCall()
            else:
                return self.process(token['token'])
        elif token['token'] == '(':
            self.process('(')
            expr = self.expression()
            self.process(')')
            return expr
        elif token['token'] in unaryOp():
            op = self.process(token['token'])
            term = self.term()
            return {'type': 'unaryOp', 'op': op, 'term': term}
        else:
            self.error(token)

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                | (className|varName) '.' subroutineName '(' expressionList ')'
        """
        token = self.lexer.peek()
        if self.lexer.peek()['token'] == '.':
            caller = self.process(token['token'])
            self.process('.')
            subroutine_name = self.subroutineName()
            self.process('(')
            expr_list = self.expressionList()
            self.process(')')
            return {'type': 'methodCall', 'caller': caller, 'subroutine': subroutine_name, 'arguments': expr_list}
        else:
            subroutine_name = self.subroutineName()
            self.process('(')
            expr_list = self.expressionList()
            self.process(')')
            return {'type': 'functionCall', 'subroutine': subroutine_name, 'arguments': expr_list}

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        expressions = []
        if self.lexer.peek()['token'] != ')':
            expressions.append(self.expression())
            while self.lexer.peek()['token'] == ',':
                self.process(',')
                expressions.append(self.expression())
        return expressions

    def process(self, expected_token):
        """
        Consomme le jeton attendu depuis le lexer.
        Si le jeton correspond, il est consommé et retourné.
        Sinon, une erreur de syntaxe est levée.

        Args:
            expected_token (str): Le jeton attendu.

        Returns:
            dict: Le jeton consommé.

        Raises:
            SyntaxError: Si le jeton attendu n'est pas trouvé.
        """
        token = self.lexer.next()
        if token is not None and token['token'] == expected_token:
            return token
        else:
            self.error(token['token'])

    def error(self, token):
        """
        Affiche une erreur de syntaxe avec des détails sur le jeton fautif.

        Args:
            token (dict): Le jeton courant ou None si EOF.

        Raises:
            SystemExit: Termine le programme avec un message d'erreur.
        """
        if token is None:
            print("Syntax error: unexpected end of file")
        else:
            print(f"Syntax error (line={token['line']}, col={token['col']}): unexpected token '{token['token']}'")
        sys.exit(1)

if __name__ == "__main__":
    file = sys.argv[0]
    print('-----debut')
    parser = Parser(file)
    arbre = parser.jackclass()
    todot = todot.Todot(file)
    todot.todot(arbre)
    print('-----fin')
