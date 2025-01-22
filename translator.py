from lex_analizer import Buffer, LexicalAnalyzer
from typing import List
from syntax_analaizer import Parser, Token, Node
from generator import CodeGenerator
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTextEdit, QPushButton)


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


class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C++ to Java Translator")

        # Установка основного макета
        main_layout = QVBoxLayout()

        # Левая панель для кода на C++
        self.cpp_text = QTextEdit()
        cpp_label = QLabel("Код на C++:")

        # Правая панель для кода на Java
        self.java_output = QTextEdit()
        java_label = QLabel("Код на Java:")

        # Кнопки
        self.translate_button = QPushButton("Транслировать")
        self.clear_button = QPushButton("Очистить")

        # Ошибки
        self.error_output = QTextEdit()
        error_label = QLabel("Ошибки:")
        self.error_output.setStyleSheet("background-color: lightpink;")
        self.error_output.setReadOnly(True)  # По желанию, сделаем поле только для чтения

        # Установка макета для панели с кодом
        code_layout = QHBoxLayout()
        code_layout.addWidget(cpp_label)
        code_layout.addWidget(self.cpp_text)
        code_layout.addWidget(java_label)
        code_layout.addWidget(self.java_output)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.translate_button)
        button_layout.addWidget(self.clear_button)

        # Добавление элементов в основной макет
        main_layout.addLayout(code_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(error_label)
        main_layout.addWidget(self.error_output)  # Поле ошибок внизу

        self.setLayout(main_layout)

        # Привязка функций к кнопкам
        self.translate_button.clicked.connect(self.translate_code)
        self.clear_button.clicked.connect(self.clear_fields)

    def translate_code(self):
        # Здесь ваша логика трансляции кода
        # try:
        cpp_code = self.cpp_text.toPlainText()
        if not cpp_code:
            self.error_output.setPlainText("Ошибка: поле C++ пусто. Пожалуйста, введите код для трансляции.")
            return

        with open("program.cpp", 'w') as file:
            file.write(cpp_code)

        # Предположим, вы совершаете трансляцию и получаете java_code
        try:
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
            # parser.print_syntax_tree(program_node)

            # обрабатываем все cin, чтобы добавить к ним тип данных
            preproc_cin(program_node)

            # еще раз печатаем дерево для проверки синов
            parser.print_syntax_tree(program_node)

            # генерируем джава-код
            generator = CodeGenerator()
            generator.generate(program_node)
            java_code = generator.get_code()

        except Exception as e:
            self.error_output.setPlainText(str(e))
        else:
            self.error_output.clear()
            self.java_output.setPlainText(java_code)

    def clear_fields(self):
        self.cpp_text.clear()
        self.java_output.clear()
        self.error_output.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator_app = TranslatorApp()
    translator_app.resize(800, 600)  # Установка начального размера окна
    translator_app.show()
    sys.exit(app.exec_())
