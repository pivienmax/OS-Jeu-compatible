import re
import sys
import Reader

'''No comment'''


class Lexer:
    """No comment"""

    def __init__(self, file):
        with open(file, 'r') as f:
            self.lines = f.readlines()
        self.current_line = 0
        self.current_char = 0

    def process(self, str):
        token = self.lexer.next()
        print(f"Processing token: {token}")  # Ajout de débogage
        if token is not None and token['token'] == str:
            self.xml.write(f"<{token['type']}>{token['token']}</{token['type']}>\n")
        else:
            self.error(token)

    def _comment(self):
        # No comment
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return None
        match t['char']:
            case '/':
                while t is not None and t['char'] != '\n':
                    t = self.reader.next()
                return None
            case '*':
                while True:
                    while t is not None and t['char'] != '*':
                        t = self.reader.next()
                    t = self.reader.next()
                    if t is None or t['char'] == '/':
                        return
            case _:
                return '/'

    def _skip(self):
        # No comment
        self.reader.next()
        return

    def _toke(self):
        # No comment
        res = ''
        t = self.reader.look()
        while t is not None and re.fullmatch(r'[a-zA-Z0-9_]', t['char']):
            t = self.reader.next()
            res += t['char']
            t = self.reader.look()
        return res

    def _stringConstant(self):
        res = '"'
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return '""'
        while t is not None and t['char'] != '\"':
            res += t['char']
            t = self.reader.next()
        return res + '"'

    def next(self):
        # Skip whitespace and comments
        self.skip_whitespace_and_comments()

        # Capture the current token
        current_token = self.get_current_token()
        if not current_token:
            raise SyntaxError("Unexpected end of input or empty token")

        # Check if the token matches specific patterns
        if current_token in ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',
                             'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while',
                             'return']:
            return {'type': 'keyword', 'token': current_token}
        elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', current_token):  # Identifiant valide
            return {'type': 'identifier', 'token': current_token}
        elif current_token.isdigit():  # Constantes numériques
            return {'type': 'integerConstant', 'token': current_token}
        elif current_token.startswith('"') and current_token.endswith('"'):  # Constantes chaîne
            return {'type': 'stringConstant', 'token': current_token[1:-1]}
        else:
            raise SyntaxError(f"Unknown token: {current_token}")

    def skip_whitespace_and_comments(self):
        """
            Avance le pointeur dans le fichier source pour sauter les espaces blancs,
            les nouvelles lignes, et les commentaires.
            """
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # Ignore les lignes vides ou les espaces blancs
            line = line.lstrip()
            if not line:
                self.current_line += 1
                self.current_char = 0
                continue

            # Vérifie les commentaires
            if line.startswith("//"):  # Commentaire sur une seule ligne
                self.current_line += 1
                self.current_char = 0
                continue

            if line.startswith("/*"):  # Début d'un commentaire multi-ligne
                while self.current_line < len(self.lines):
                    end_comment = line.find("*/")
                    if end_comment != -1:
                        # Fin du commentaire multi-ligne trouvé
                        self.current_char = end_comment + 2
                        line = line[end_comment + 2:]
                        break
                    else:
                        # Avance jusqu'à la fin de la ligne et passe à la suivante
                        self.current_line += 1
                        if self.current_line < len(self.lines):
                            line = self.lines[self.current_line]
                else:
                    raise SyntaxError("Unterminated multi-line comment")

                continue

            # Si nous sommes ici, la ligne n'est ni un commentaire ni vide
            self.lines[self.current_line] = line
            break

        if self.current_line >= len(self.lines):
            return  # Fin du fichier

    def get_current_token(self):
        if self.current_line >= len(self.lines):  # Fin du fichier
            return None
        line = self.lines[self.current_line].strip()
        if not line:  # Ligne vide, passer à la suivante
            self.current_line += 1
            return self.get_current_token()
        # Extraire un token de la ligne actuelle
        token = line[self.current_char:].split()[0]  # Exemple simple
        return token if token else None

    def _read(self):
        # No comment
        token = None
        while self.reader.hasNext() and token is None:
            self.line = self.reader._line
            self.col = self.reader._col
            t = self.reader.look()
            char = t['char']
            match char:
                case '/':
                    if self._comment() is not None:
                        token = "/"
                case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ';' | '=' | '.' | '+' | '-' | '*' | '&' | '|' | '~' | '<' | '>':
                    token = char
                    self._skip()
                case ' ' | '\t' | '\n':
                    self._skip()
                case char if re.fullmatch(r'[a-zA-Z0-9_]', char):
                    token = self._toke()
                case '"':
                    token = self._stringConstant()
                case _:
                    print(f'SyntaxError : line={self.line}, col={self.col}')
                    exit()

        if token is None:
            return None
        else:
            pattern = self._pattern()
            group = pattern.fullmatch(token)
            if group is None:
                print(f'SyntaxError (line={self.line}, col={self.col}): {token}')
                exit()
            else:
                return {'line': self.line, 'col': self.col, 'type': group.lastgroup, 'token': token}

    def hasNext(self):
        """ No comment """
        return self.tokens[0] is not None

    def hasNext2(self):
        """ No comment """
        return self.tokens[1] is not None

    def look(self):
        """ No comment """
        return self.tokens[0]

    def look2(self):
        """ No comment """
        return self.tokens[1]

    def peek(self):
        """
        Retourne le prochain jeton sans le consommer.
        """
        return self.tokens[0] if self.tokens[0] else None

    def _pattern(self):
        # No comment
        return re.compile(r"""
            (?P<symbol>[()[\]{},;=.+\-*/&|~<>])|
            (?P<keyword>class|constructor|method|function|int|boolean|char|void|var|static|field|let|do|if|else|while|return|true|false|null|this) |
            (?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*) | # identifiant
            (?P<StringConstant>\"[^\n]*\") | # chaine de caracteres sans retour a la ligne
            (?P<IntegerConstant>[0-9]+) | # des entiers  
        """, re.X)

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration


if __name__ == "__main__":
    file = sys.argv[0]
    print('-----debut')
    lexer = Lexer(file)
    for token in lexer:
        print(token)
    print('-----fin')
