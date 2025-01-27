from lex_analizer import Buffer, LexicalAnalyzer
from typing import List
from syntax_analaizer import Parser, Token, Node
from generator import CodeGenerator


def preproc(pretokens) -> List[Token]:
    '''удаляет пробелы и переносы строки в токенах'''
    tokens: List[Token] = []
    for i in range(len(pretokens)):
        if pretokens[i].token != 'D10':
            # надо еще подумать над тем как убирать переносы строки, так как
            # где-то они должны быть обязательно. с пробелами такой проблемы
            # нет, потому что если лексемы распознались правильно, значит
            # пробелы были там где надо
            if not (pretokens[i].token == 'O28'
                    and pretokens[i - 1].token != 'O19'):
                tokens.append(pretokens[i])
    return tokens


def find_type(root, type):
    found_nodes = []
    if root.node_type == type:
        found_nodes.append(root)
    for child in root.children:
        found_nodes.extend(find_type(child, type))
    return found_nodes


def find_value(root, value):
    if root.value == value:
        return root
    for child in root.children:
        result = find_value(child, value)
        if result is not None:
            return result
    return None


def preproc_cin(program_node):
    '''в джаве нет обычного чтения, там нужно явно указывать
    тип данных, который мы читаем. поэтому тут я написала функцию,
    которая после построения дерева ищет в нем все узлы Cin и затем
    ищет, в каком узле объявляется переменная, которую нужно считать.
    после этого в узел Cin добавляется потомок с типом этой переменной'''
    finds = find_type(program_node, 'Cin')
    if finds:
        for find in finds:
            id = find.children[0].value
            node = find.parent.parent
            find2 = find_value(node, id)
            if find2:
                type = find2.parent.children[0].value
                find.add_child(Node('Type', type))
            else:
                raise Exception(f'нельзя считать необъявленную переменную{id}')


if __name__ == '__main__':

    # считываем исходную программу
    buffer = Buffer()
    Analyzer = LexicalAnalyzer()

    fullTokens: List[Token] = []

    token = []
    lexeme = []
    row = []
    column = []

    print(buffer.load_buffer())
    for i in buffer.load_buffer():
        t, lex, lin, col = Analyzer.tokenize(i)
        token += t
        lexeme += lex
        row += lin
        column += col

    # создаем массив токенов
    for i in range(len(token)):
        fullToken = Token(token[i], lexeme[i], row[i], column[i])
        fullTokens.append(fullToken)

    # удаляем пробелы и переносы строки
    tokens = preproc(fullTokens)

    # печать токенов
    for i in range(len(tokens)):
        print(tokens[i])

    # создаем парсер
    parser = Parser(tokens)

    # строим дерево
    program_node = parser.parse_program()

    # выводим дерево
    parser.print_syntax_tree(program_node)

    # обрабатываем все cin, чтобы добавить к ним тип данных
    preproc_cin(program_node)

    # еще раз печатаем дерево для проверки синов
    parser.print_syntax_tree(program_node)

    # генерируем джава-код
    generator = CodeGenerator()
    generator.generate(program_node)
    java_code = generator.get_code()
    print(java_code)
