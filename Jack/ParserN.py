import sys
import Lexer
import todot

class Parser:
    """Parser to calculate the simplified syntax tree of a Jack program."""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.syntax_tree = None  # Root of the syntax tree

    def jackclass(self):
        # Process the main class rule and return its structure as a dictionary
        self.process('class')
        class_name = self.className()
        self.process('{')
        variables = []
        subroutines = []
        while self.lexer.peek() in ['static', 'field']:
            variables.append(self.classVarDec())
        while self.lexer.peek() in ['constructor', 'function', 'method']:
            subroutines.append(self.subroutineDec())
        self.process('}')

        self.syntax_tree = {
            "type": "class",
            "name": class_name,
            "variables": variables,
            "subroutines": subroutines
        }
        return self.syntax_tree

    def classVarDec(self):
        # Process class variable declarations
        kind = self.lexer.peek()
        self.process(kind)
        var_type = self.type()
        names = [self.varName()]
        while self.lexer.peek() == ',':
            self.process(',')
            names.append(self.varName())
        self.process(';')
        return {
            "type": "classVarDec",
            "kind": kind,
            "varType": var_type,
            "names": names
        }

    def type(self):
        # Process types
        if self.lexer.peek() in ['int', 'char', 'boolean']:
            type_name = self.lexer.peek()
            self.process(type_name)
            return type_name
        else:
            return self.className()

    def subroutineDec(self):
        # Process subroutine declarations
        subroutine_type = self.lexer.peek()
        self.process(subroutine_type)
        return_type = self.type() if self.lexer.peek() != 'void' else self.process('void')
        name = self.subroutineName()
        self.process('(')
        parameters = self.parameterList()
        self.process(')')
        body = self.subroutineBody()
        return {
            "type": "subroutineDec",
            "subroutineType": subroutine_type,
            "returnType": return_type,
            "name": name,
            "parameters": parameters,
            "body": body
        }

    def parameterList(self):
        # Process parameter list
        parameters = []
        if self.lexer.peek() != ')':
            param_type = self.type()
            param_name = self.varName()
            parameters.append({"type": "parameter", "paramType": param_type, "name": param_name})
            while self.lexer.peek() == ',':
                self.process(',')
                param_type = self.type()
                param_name = self.varName()
                parameters.append({"type": "parameter", "paramType": param_type, "name": param_name})
        return parameters

    def subroutineBody(self):
        # Process subroutine body
        self.process('{')
        variables = []
        statements = []
        while self.lexer.peek() == 'var':
            variables.append(self.varDec())
        statements = self.statements()
        self.process('}')
        return {
            "type": "subroutineBody",
            "variables": variables,
            "statements": statements
        }

    def varDec(self):
        # Process variable declarations in subroutines
        self.process('var')
        var_type = self.type()
        names = [self.varName()]
        while self.lexer.peek() == ',':
            self.process(',')
            names.append(self.varName())
        self.process(';')
        return {
            "type": "varDec",
            "varType": var_type,
            "names": names
        }

    def className(self):
        # Process class name
        name = self.lexer.peek()
        self.process(name)
        return name

    def subroutineName(self):
        # Process subroutine name
        name = self.lexer.peek()
        self.process(name)
        return name

    def varName(self):
        # Process variable name
        name = self.lexer.peek()
        self.process(name)
        return name

    def statements(self):
        # Process statements
        statements = []
        while self.lexer.peek() in ['let', 'if', 'while', 'do', 'return']:
            statements.append(self.statement())
        return statements

    def statement(self):
        # Process individual statement based on type
        if self.lexer.peek() == 'let':
            return self.letStatement()
        elif self.lexer.peek() == 'if':
            return self.ifStatement()
        elif self.lexer.peek() == 'while':
            return self.whileStatement()
        elif self.lexer.peek() == 'do':
            return self.doStatement()
        elif self.lexer.peek() == 'return':
            return self.returnStatement()

    def letStatement(self):
        self.process('let')
        var_name = self.varName()
        index_expression = None
        if self.lexer.peek() == '[':
            self.process('[')
            index_expression = self.expression()
            self.process(']')
        self.process('=')
        expression = self.expression()
        self.process(';')
        return {
            "type": "letStatement",
            "varName": var_name,
            "indexExpression": index_expression,
            "expression": expression
        }

    def ifStatement(self):
        self.process('if')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        if_statements = self.statements()
        self.process('}')
        else_statements = []
        if self.lexer.peek() == 'else':
            self.process('else')
            self.process('{')
            else_statements = self.statements()
            self.process('}')
        return {
            "type": "ifStatement",
            "condition": condition,
            "ifStatements": if_statements,
            "elseStatements": else_statements
        }

    def whileStatement(self):
        self.process('while')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        statements = self.statements()
        self.process('}')
        return {
            "type": "whileStatement",
            "condition": condition,
            "statements": statements
        }

    def doStatement(self):
        self.process('do')
        subroutine_call = self.subroutineCall()
        self.process(';')
        return {
            "type": "doStatement",
            "subroutineCall": subroutine_call
        }

    def returnStatement(self):
        self.process('return')
        expression = self.expression() if self.lexer.peek() != ';' else None
        self.process(';')
        return {
            "type": "returnStatement",
            "expression": expression
        }

    def expression(self):
        terms = [self.term()]
        while self.lexer.peek() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            operator = self.op()
            term = self.term()
            terms.append({"operator": operator, "term": term})
        return {"type": "expression", "terms": terms}

    def term(self):
        # Simplified for different term types
        if self.lexer.peek().isdigit():
            value = self.lexer.peek()
            self.process(value)
            return {"type": "integerConstant", "value": value}
        elif self.lexer.peek().startswith('"'):
            value = self.lexer.peek()
            self.process(value)
            return {"type": "stringConstant", "value": value}
        elif self.lexer.peek() in ['true', 'false', 'null', 'this']:
            value = self.KeywordConstant()
            return {"type": "keywordConstant", "value": value}
        elif self.lexer.peek() == '(':
            self.process('(')
            expression = self.expression()
            self.process(')')
            return {"type": "expression", "expression": expression}
        elif self.lexer.peek() in ['-', '~']:
            operator = self.unaryOp()
            term = self.term()
            return {"type": "unaryOp", "operator": operator, "term": term}
        else:
            var_name = self.varName()
            if self.lexer.peek() == '[':
                self.process('[')
                index_expression = self.expression()
                self.process(']')
                return {"type": "arrayAccess", "varName": var_name, "indexExpression": index_expression}
            elif self.lexer.peek() in ['(', '.']:
                return self.subroutineCall()
            return {"type": "varName", "name": var_name}

    def subroutineCall(self):
        # Similar to term, handles subroutine calls
        caller = self.className() if self.lexer.peek() == '.' else None
        if caller:
            self.process('.')
        subroutine_name = self.subroutineName()
        self.process('(')
        arguments = self.expressionList()
        self.process(')')
        return {
            "type": "subroutineCall",
            "caller": caller,
            "subroutineName": subroutine_name,
            "arguments": arguments
        }

    def expressionList(self):
        arguments = []
        if self.lexer.peek() != ')':
            arguments.append(self.expression())


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = Parser(file)
    arbre = parser.jackclass()
    todot = todot.Todot(file)
    todot.todot(arbre)
    print('-----fin')