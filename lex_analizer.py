import re


class LexicalAnalyzer:
    # Token row
    lin_num = 1

    def tokenize(self, code):
        rules = [
            ('P1', r'#include'),
            ('P2', r'#define'),
            ('K1', r'break'),
            ('K2', r'const'),
            ('K3', r'continue'),
            ('K4', r'while'),
            ('K5', r'do'),
            ('K6', r'if'),
            ('K7', r'else'),
            ('K8', r'for'),
            ('K9', r'class'),
            ('K10', r'this'),
            ('K11', r'using'),
            ('K12', r'return'),
            ('K13', r'namespace'),
            ('K14', r'this'),
            ('K15', r'bool'),
            ('k16', r'char'),
            ('K17', r'int'),
            ('K18', r'float'),
            ('K19', r'double'),
            ('K20', r'void'),
            ('K21', r'true'),
            ('K22', r'string'),
            ('K23', r'false'),
            ('K24', r'cout'),
            ('K25', r'cin'),
            ('K26', r'std'),
            ('K27', r'new'),
            ('K28', r'null'),
            ('K29', r'private'),
            ('K30', r'protected'),
            ('K31', r'public'),
            ('K32', r'main'),
            # ('Q1', r'\''),            # '
            # ('Q2', r'\"'),            # "
            ('D1', r'\.'),            # .
            ('D2', r','),
            ('D3', r';'),
            ('D4', r'\{'),            # {
            ('D5', r'\}'),            # }
            ('D6', r'\('),            # (
            ('D7', r'\)'),            # )
            ('D8', r'\['),            # [
            ('D9', r'\]'),            # ]
            ('D10', r'[ \t]+'),       # SPACE and TABS

            ('O2', r'\+\+'),          # ++
            ('O3', r'\+='),           # +=
            ('O1', r'\+'),            # +
            ('O4', r'-'),
            ('O5', r'--'),
            ('O6', r'-='),
            ('O8', r'\*='),           # *=
            ('O7', r'\*'),            # *
            ('O10', r'\/='),          # /=
            ('O9', r'\/'),            # /
            ('O12', r'\%='),          # %=
            ('O11', r'\%'),           # %
            ('O14', r'\|\|'),         # ||
            ('O13', r'\|'),           # |
            ('O16', r'&&'),
            ('O15', r'&'),
            ('O17', r'!'),
            ('O18', r'!='),
            ('O26', r'>>'),
            ('O20', r'>='),
            ('O25', r'<<'),
            ('O22', r'<='),
            ('O24', r'=='),
            ('O21', r'<'),
            ('O19', r'>'),
            ('O23', r'\='),            # =
            ('O27', r'::'),
            ('O28', r'\n'),               # NEW LINE
            ('O29', r':'),
            ('N3', r'"([^"\\]*(\\.[^"\\]*)*)"'),           # String
            ('N4', r'\'\w\''),           # char
            ('ID', r'[a-zA-Z]\w*'),       # IDENTIFIERS
            ('N2', r'\d(\d)*\.\d(\d)*'),  # FLOAT
            ('N1', r'\d(\d)*'),           # INT
            ('NONAME', r'.'),            # noname


        ]

        tokens_join = '|'.join('(?P<%s>%s)' % x for x in rules)
        lin_start = 0

        # Lists of output for the program
        token = []
        lexeme = []
        row = []
        column = []

        # It analyzes the code to find the lexemes and their respective Tokens
        for m in re.finditer(tokens_join, code):
            token_type = m.lastgroup
            token_lexeme = m.group(token_type)

            if token_type == 'NEWLINE':
                lin_start = m.end()
                self.lin_num += 1
            elif token_type == 'SKIP':
                continue
            elif token_type == 'MISMATCH':
                raise RuntimeError('%r unexpected on \
line %d' % (token_lexeme, self.lin_num))
            else:
                col = m.start() - lin_start
                column.append(col)
                token.append(token_type)
                lexeme.append(token_lexeme)
                row.append(self.lin_num)
                # To print information about a Token
#                 print('Token = {0}, Lexeme = \'{1}\', Row = {2}, \
# Column = {3}'.format(token_type, token_lexeme, self.lin_num, col))
        return token, lexeme, row, column


class Buffer:
    def load_buffer(self):
        arq = open('program.cpp', 'r')
        text = arq.readline()

        buffer = []
        cont = 1

        # The buffer size can be changed by changing cont
        while text != "":
            buffer.append(text)
            text = arq.readline()
            cont += 1

            if cont == 10 or text == '':
                # Return a full buffer
                buf = ''.join(buffer)
                cont = 1
                yield buf

                # Reset the buffer
                buffer = []

        arq.close()
