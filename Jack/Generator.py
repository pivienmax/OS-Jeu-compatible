import sys
import ParserN


def error(message=''):
    print(f"SyntaxError: {message}")
    exit()


class Generator:
    def __init__(self, arbre=None):
        self.labelCounter = 0
        if arbre is not None:
            self.arbre = arbre
            self.vmfile = open(self.arbre['name'] + '.vm', "w")
            self.symbolClassTable = []
            self.symbolRoutineTable = []
        else:
            self.arbre = None

    def jackclass(self, arbre):
        """Handles the class structure."""
        if not isinstance(arbre, dict):
            raise TypeError("L'objet 'arbre' doit être un dictionnaire, reçu : " + str(type(arbre)))

        if 'name' not in arbre or 'variables' not in arbre or 'subroutines' not in arbre:
            raise KeyError(
                "L'objet 'arbre' doit contenir les clés 'name', 'variables', et 'subroutines'. Reçu : " + str(arbre))

        self.vmfile.write("// class " + arbre['name'] + "\n")

        # Add class-level variables
        for var in arbre['variables']:  # Remplace 'varDec' par 'variables'
            self.variable(var)

        # Process subroutines
        for subroutine in arbre['subroutines']:  # Remplace 'subroutine' par 'subroutines'
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
        """Handles if statements."""
        label_true = self.newLabel()
        label_end = self.newLabel()
        self.vmfile.write("// if " + str(inst['condition']) + "\n")
        self.expression(inst['condition'])
        self.vmfile.write("if-goto " + label_true + "\n")
        self.vmfile.write("goto " + label_end + "\n")
        self.vmfile.write("label " + label_true + "\n")
        for true_inst in inst['true']:
            self.statement(true_inst)
        self.vmfile.write("label " + label_end + "\n")

    def whileStatement(self, inst):
        """Handles while statements."""
        label_start = self.newLabel()
        label_end = self.newLabel()
        self.vmfile.write("// while " + str(inst['condition']) + "\n")
        self.vmfile.write("label " + label_start + "\n")
        self.expression(inst['condition'])
        self.vmfile.write("not\n")
        self.vmfile.write("if-goto " + label_end + "\n")
        for while_inst in inst['instructions']:
            self.statement(while_inst)
        self.vmfile.write("goto " + label_start + "\n")
        self.vmfile.write("label " + label_end + "\n")

    def doStatement(self, inst):
        """Handles do statements."""
        self.vmfile.write("// do " + str(inst['name']) + "\n")
        self.subroutineCall(inst)

    def returnStatement(self, inst):
        """Handles return statements."""
        self.vmfile.write("// return\n")
        if inst['valeur']:
            self.expression(inst['valeur'])
        else:
            self.vmfile.write("push constant 0\n")
        self.vmfile.write("return\n")

    def expression(self, exp):
        """Handles expressions and operations."""
        for term in exp:
            self.term(term)

    def term(self, t):
        """Handles terms in an expression."""
        if t['type'] == 'int':
            self.vmfile.write("push constant " + str(t['value']) + "\n")
        elif t['type'] == 'string':
            self.vmfile.write("push constant " + str(len(t['value'])) + "\n")
            self.vmfile.write("call String.new 1\n")
            for char in t['value']:
                self.vmfile.write("push constant " + str(ord(char)) + "\n")
                self.vmfile.write("call String.appendChar 2\n")
        elif t['type'] == 'constant':
            self.vmfile.write("push constant " + str(t['value']) + "\n")
        elif t['type'] == 'varName':
            self.vmfile.write("push " + t['kind'] + " " + str(self.getVarIndex(t['name'])) + "\n")
        elif t['type'] == 'call':
            self.subroutineCall(t)
        elif t['type'] == 'expression':
            self.vmfile.write("(")
            self.expression(t['indice'])
            self.vmfile.write(")")

    def subroutineCall(self, call):
        """Handles subroutine calls."""
        self.vmfile.write("call " + call['classvar'] + "." + call['name'] + " " + str(len(call['argument'])) + "\n")
        for arg in call['argument']:
            self.expression(arg)
    def getVarIndex(self, varName):
        """Find the variable's index in the symbol table."""
        for idx, var in enumerate(self.symbolRoutineTable):
            if var['name'] == varName:
                return idx
        for idx, var in enumerate(self.symbolClassTable):
            if var['name'] == varName:
                return idx
        return -1

    def newLabel(self):
        """Generates a new label for control flow."""
        label = "LABEL" + str(self.labelCounter)
        self.labelCounter += 1
        return label


if __name__ == '__main__':
    file = sys.argv[0]
    print('-----debut')
    parser = ParserN.Parser(file)
    arbre = parser.jackclass()
    generator = Generator(arbre)
    generator.jackclass(generator.arbre)
    print('-----fin')
