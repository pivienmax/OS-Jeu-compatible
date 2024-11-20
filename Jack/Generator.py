"""No comment"""
import sys
import Parser


class Generator:
    """No comment"""

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()
            self.vmfile = open(self.arbre['name'] + '.vm', "w")
            self.symbolClassTable = []
            self.symbolRoutineTable = []

    def jackclass(self, arbre):
        """Handles the class structure."""
        self.vmfile.write("// class " + arbre['name'] + "\n")
        # Add class-level variables
        for var in arbre['varDec']:
            self.variable(var)
        # Process subroutines
        for subroutine in arbre['subroutine']:
            self.subroutineDec(subroutine)

    def variable(self, var):
        """Handles variable declarations (both instance and local variables)."""
        kind = var['kind']
        if kind == 'field':
            self.symbolClassTable.append(var)
        elif kind == 'static':
            self.symbolClassTable.append(var)
        else:
            self.symbolRoutineTable.append(var)

    def subroutineDec(self, routine):
        """Handles the subroutine declaration and its body."""
        self.vmfile.write("// Subroutine " + routine['name'] + "\n")
        self.symbolRoutineTable = []  # Reset local symbol table
        # Add arguments and locals
        for var in routine['argument']:
            self.variable(var)
        for var in routine['local']:
            self.variable(var)

        # Generate code for subroutine body
        self.vmfile.write("function " + self.arbre['name'] + "." + routine['name'] + " " +
                          str(len(routine['local'])) + "\n")

        if routine['type'] == 'constructor':
            # Handle constructor-specific initialization (allocating memory for fields)
            num_fields = len([var for var in self.symbolClassTable if var['kind'] == 'field'])
            self.vmfile.write("push constant " + str(num_fields) + "\n")
            self.vmfile.write("call Memory.alloc 1\n")
            self.vmfile.write("pop pointer 0\n")
        elif routine['type'] == 'method':
            # Handle method-specific initialization (setting 'this' to the current object)
            self.vmfile.write("push argument 0\n")
            self.vmfile.write("pop pointer 0\n")

        # Generate code for subroutine instructions
        for inst in routine['instructions']:
            self.statement(inst)

    def statement(self, inst):
        """Handles different types of statements."""
        if inst['type'] == 'let':
            self.letStatement(inst)
        elif inst['type'] == 'if':
            self.ifStatement(inst)
        elif inst['type'] == 'while':
            self.whileStatement(inst)
        elif inst['type'] == 'do':
            self.doStatement(inst)
        elif inst['type'] == 'return':
            self.returnStatement(inst)

    def letStatement(self, inst):
        """Handles let statements."""
        self.vmfile.write("// let " + inst['variable'] + "\n")
        # Handle index if present (array element assignment)
        if 'indice' in inst and inst['indice']:
            self.expression(inst['indice'])
            self.vmfile.write("pop temp 0\n")
            self.vmfile.write("push pointer 1\n")
            self.vmfile.write("add\n")
            self.vmfile.write("pop pointer 1\n")
        # Handle assignment value
        self.expression(inst['valeur'])
        self.vmfile.write("pop local " + str(self.getVarIndex(inst['variable'])) + "\n")

    def ifStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'if', 'condition': expression, 'true': [instruction],
        'false': [instruction]}
        """

    def whileStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'while', 'condition': expression,
        'instructions': [instruction]}
        """

    def doStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'do', 'classvar': className ou varName,
        'name': subroutineName, 'argument': [expression]}
        """

    def returnStatement(self, inst):
        """
        {'line':line, 'col': col, 'type': 'return', 'valeur': expression}
        """

    def expression(self, exp):
        """
        [term op ...]
            avec op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """

    def term(self, t):
        """
        {'line':line, 'col': col,
        'type': 'int'| 'string'| 'constant'| 'varName'|'call'| 'expression'|'-'|'~',
         'indice':expression, 'subroutineCall': subroutineCall}
        """

    def subroutineCall(self, call):
        """
        {'line':line, 'col': col, 'classvar': className ou varName,
        'name': subroutineName, 'argument': [expression]}
        """

    def error(self, message=''):
        print(f"SyntaxError: {message}")
        exit()


if __name__ == '__main__':
    file = sys.argv[1]
    print('-----debut')
    generator = Generator(file)
    generator.jackclass()
    print('-----fin')
