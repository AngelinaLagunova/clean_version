class Token:
    def __init__(self, token, lexeme, row, column):
        self.token = token
        self.lexeme = lexeme
        self.row = row
        self.column = column

    def __str__(self):
        return f'Токен: {self.token} Лексема: {self.lexeme}'


class Node:
    def __init__(self, node_type, value=None, parent=None):
        self.node_type = node_type
        self.value = value
        self.parent = parent
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


def find_node(root, value):
    # Проверяем, совпадает ли значение текущего узла с искомым
    if root.value == value:
        return root

    # Рекурсивно ищем в дочерних узлах
    for child in root.children:
        result = find_node(child, value)
        if result is not None:
            return result

    # Если узел не найден, возвращаем None
    return None


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        '''Возвращает текущий токен'''
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, expected_type):
        '''Поглощает токен, то есть сдвигает позицию self.position
        если текущий токен соответствует expected_type'''
        if self.position < len(self.tokens) and self.tokens[self.position].token == expected_type:
            self.position += 1
        else:
            raise Exception(f'Expected token type {expected_type}')

    def checkTokensList(self, tokenlist):
        '''Поглощает последовательность токенов, если она
        соответствует tokenlist'''
        # переменная position вводится для того,
        # чтобы не изменять реальную позицию пока мы
        # не убедимся, что последовательность токенов
        # соответствует tokenlist
        position = self.position
        for i in tokenlist:
            if self.tokens[position].token != i:
                return False
            # если мы не в конце программы,
            # то все ок, смещаемся дальше
            if position < len(self.tokens):
                position += 1
            else:
                return False
        # цикл подошел к концу, теперь можно поменять реальную позицию на нашу
        self.position = position
        return True

    def parse_program(self):
        '''Парсит (добавляет узлы в дерево) прямые потомки Program, то есть
        заголовки, пространство имен, главную функцию, также тут должны быть
        обычные функции (они объявляются на одном уровне с main), классы,
        константы и тд'''
        node = Node('Program')
        node.add_child(self.parse_headers())
        while self.position < len(self.tokens) - 1:
            token = self.current_token()
            if token.token == 'K11':
                node.add_child(self.parse_namespace())
            elif token.token == 'K9':
                node.add_child(self.parse_class_declaration())
            elif token.token in ['K17', 'K18', 'K22', 'ID', 'K20'] and self.tokens[self.position + 1].token != 'K32':
                node.add_child(self.parse_declaration())
            elif token.token == 'K17':
                node.add_child(self.parse_main())
            else:
                raise Exception('Ошибка 2: ожидалось имя класса')
        return node

    def parse_namespace(self):
        '''Парсит пространство имен (пока только std)'''
        node = Node('Namespaces')
        thistokenlist = ['K11', 'K13', 'K26', 'D3']
        if self.checkTokensList(thistokenlist):
            node.add_child(Node('Namespace', 'std'))
            return node
        else:
            raise Exception('Ошибка 18: ожидалось пространство имен')

    def parse_headers(self):
        '''Парсит заголовки (любые)'''
        token = self.current_token()
        node = Node('Headers')
        while token.token == 'P1':
            thistokenlist = ['P1', 'O21', 'ID', 'O19', 'O28']
            if self.checkTokensList(thistokenlist):
                node.add_child(Node('ID', self.tokens[self.position - 3].lexeme))
            else:
                raise Exception('Ошибка 0: ожидалось имя заголовочного файла')
            token = self.current_token()
        return node

    def parse_main(self):
        '''Парсит главную функцию'''
        thistokenlist = ['K17', 'K32', 'D6', 'D7', 'D4']
        if self.checkTokensList(thistokenlist):
            node = Node('MainFunction')
            print(self.tokens[self.position].token)
            node.add_child(self.parse_body())
            token = self.current_token()
            if token.token == 'D5':
                self.consume('D5')
                return node
            else:
                raise Exception('не закрыта фигурная скобка')
        else:
            raise Exception('Ошибка 1: ожидалась главная функция main')

    def parse_body(self):
        '''Парсит тело функции (любой)'''
        node = Node('Body')
        token = self.current_token()
        while token.token != 'D5':
            node.add_child(self.parse_code_block())
            token = self.current_token()

            if token.token == 'D5':
                return node

    def parse_code_block(self):
        '''Парсит инструкции внутри тела функции. Пока
        что только объявление переменных, ввод/вывод, присваивание'''
        node = Node('Instruction')
        token = self.current_token()
        if token.token == 'ID' and self.tokens[self.position+1].token in ['O23', 'O2', 'O3', 'O5', 'O6', 'O8', 'O10', 'O12']:
            node.add_child(self.parse_assignment())
        elif token.token == 'ID' and self.tokens[self.position+1].token == 'D1':
            node.add_child(self.parse_class_declaration_block_method())
        elif token.token == 'ID' and self.tokens[self.position+3].token == 'O23':
            node.add_child(self.parse_class_declaration_block())
        elif token.token == 'ID' and self.tokens[self.position+1].token == 'D6':
            node.add_child(self.parse_function_call())
        elif token.token in ['K17', 'K18', 'K22']:
            node.add_child(self.parse_declaration())
        elif token.token == 'K24':
            node.add_child(self.parse_cout())
        elif token.token == 'ID' and self.tokens[self.position+1].token == 'ID':
            node.add_child(self.ClassDeclarationInsideBlock())
        elif token.token == 'K25':
            node.add_child(self.parse_cin())
        elif token.token == 'K4':
            node.add_child(self.parse_while())
        elif token.token == 'K6':
            node.add_child(self.parse_if())
        elif token.token == 'K12':
            node.add_child(self.parse_return())

        else:
            # print('exeption', token.token, token.row, token.column, self.position)
            raise Exception('Ошибка 17: ожидалась инструкция')
        return node
    
    def ClassDeclarationInsideBlock(self):
        '''парсим объявление одного класса в блоке кода (па парам парам апарам па па па)'''
        token = self.current_token()
        class_node = Node('ClassBlockDeclarationSimple')
        self.consume('ID')
        class_node.add_child(Node('ClassDeclaratedSimpleNameClass', token.lexeme))
        token = self.current_token()
        self.consume('ID')
        class_node.add_child(Node('ClassDeclaratedSimpleName', token.lexeme))
        self.consume('D3')
        return class_node


    def parse_class_declaration_block(self):
        '''парсим объявление метода, сука дайте поспать'''
        token = self.current_token()
        class_node = Node('ClassBlockDeclaration')
        class_node.add_child(Node('ClassDeclarated', token.lexeme))
        self.consume('ID')
        self.consume('O7')
        token = self.current_token()
        class_node.add_child(Node('ClassDeclaratedName', token.lexeme))
        self.consume('ID')
        token = self.current_token()
        self.consume('O23')
        token = self.current_token()
        self.consume('K27')
        token = self.current_token()
        class_node.add_child(Node('ClassDeclaratedSourceName', token.lexeme))
        self.consume('ID')
        token = self.current_token()
        self.consume('D6')
        token = self.current_token()
        if self.tokens[self.position+1].token == 'D7':
            self.consume('D7')
        else:
            class_node.add_child(self.parse_call_arguments())
        self.consume('D3')
        token = self.current_token()
        return(class_node)

    def parse_class_declaration_block_method(self):
        '''парсим объявление класса в блоке, делаю с закрытыми глазами'''
        token = self.current_token()
        class_node = Node('ClassBlockDeclarationMethod')
        class_node.add_child(Node('ClassName', token.lexeme))
        self.consume('ID')
        self.consume('D1')
        token = self.current_token()
        class_node.add_child(Node('ClassMethodDeclarationName', token.lexeme))
        self.consume('ID')
        self.consume('D6')        
        if self.tokens[self.position+1].token == 'D7':
            self.consume('D7')
        else:
            class_node.add_child(self.parse_call_arguments())
        self.consume('D3')
        return(class_node)

    def parse_return(self):
        '''Парсит оператор return'''
        self.consume('K12')
        return_node = Node('Return')
        token = self.current_token()
    
        if token.token not in ['D3', 'D7']:
            expression_node = self.parse_expression()
            return_node.add_child(expression_node)

        token = self.current_token()
        if token.token == 'D3':
            self.consume('D3')
        else:
            raise Exception('Ожидалась точка с запятой после return')

        return return_node

    def parse_class_declaration(self):
        '''Парсит объявление класса'''
        token = self.current_token()
        if token.token == 'K9':
            class_node = Node('ClassDeclaration')
            self.consume('K9')

            token = self.current_token()
            if token.token == 'ID':
                class_node.add_child(Node('ClassName', token.lexeme))
                self.consume('ID')
            else:
                raise Exception(f'Ожидалось имя класса, но найдено {token.lexeme}')

            token = self.current_token()
            if token.token == 'D4':
                self.consume('D4')

                while self.current_token().token != 'D5':
                    access_node = self.parse_class_body()
                    if access_node:
                        class_node.add_child(access_node) 

                token = self.current_token()
                if token.token == 'D5':
                    self.consume('D5')
                else:
                    raise Exception('Пропущена закрывающая фигурная скобка класса')

                token = self.current_token()
                if token.token == 'D3':
                    self.consume('D3')
                    return class_node
                else:
                    raise Exception('Пропущена точка с запятой после объявления класса')
            else:
                raise Exception('Пропущена открывающая фигурная скобка при объявлении класса')
        else:
            raise Exception(f'Ошибка 19: Ожидалось ключевое слово class, но найдено {token.lexeme}')

    def parse_class_body(self):
        '''Парсит содержимое тела класса (переменные, методы, модификаторы доступа)'''
        token = self.current_token()
        access_node = None

        while token.token != 'D5':
            if token.token in ['K29', 'K30', 'K31']:
                access_node = Node('AccessModifier', token.lexeme)
                self.consume(token.token)

                token = self.current_token()
                if token.token == 'O29':
                    self.consume('O29')
                    token = self.current_token()

                while token.token not in ['K29', 'K30', 'K31', 'D5']:
                    if token.token == 'O29':
                        self.consume('O29')
                    elif token.token in ['K17', 'K18', 'K22', 'ID', 'K20']:
                        next_token = self.current_token()
                        if next_token.token == 'ID':
                            self.consume('ID')
                            next_token = self.current_token()
                            if next_token.token == 'D6':
                                function_node = self.parse_function_declaration()
                                access_node.add_child(function_node)
                            else:
                                declaration_node = self.parse_declaration()
                                access_node.add_child(declaration_node)
                        else:
                            declaration_node = self.parse_declaration()
                            access_node.add_child(declaration_node)
                    else:
                        break
                    token = self.current_token()

                return access_node


            elif token.token in ['K17', 'K18', 'K22', 'ID', 'K20']:
                next_token = self.current_token()
                if next_token.token == 'ID':
                    self.consume('ID')
                    next_token = self.current_token()
                    if next_token.token == 'D6':
                        return self.parse_function_declaration()
                    else:
                        return self.parse_declaration()
                else:
                    return self.parse_declaration()

            else:
                raise Exception(f'Ошибка 3: ожидалось тело класса: {token.token}')

    def parse_declaration(self):
        '''Парсит объявление переменных'''
        token = self.current_token()
        var_node = Node('Declaration')
        var_type = token.lexeme
        self.consume(token.token)
        var_node.add_child(Node('Type', var_type))
        var_node.add_child(self.parse_identifier())
        token = self.current_token()
        if token.token == 'O23':
            self.consume('O23')  # '='
            var_node.add_child(self.parse_expression())
        token = self.current_token()
        if token.token == 'D3':
            self.consume('D3')  # ';'
        elif token.token == 'D6': # ( 
            self.consume('D6')
            var_node.add_child(self.parse_function_declaration())
        else:
            raise Exception('пропущена точка с запятой')
        return var_node

    def parse_function_declaration(self):
        '''парсит объявление функции'''
        node = Node('FunctionDeclaration')
        node.add_child(self.parse_arguments())
        token = self.current_token()
        if token.token == 'D4':
            self.consume('D4')
            node.add_child(self.parse_body())
            token = self.current_token()
            if token.token == 'D5':
                self.consume('D5')
                return node
            else:
                raise Exception('не закрыта фигурная скобка')
        else:
            raise Exception('Ошибка 9: ожидалось тело функции')

    def parse_function_call(self):
        '''парсит вызов функции'''
        token = self.current_token()
        node = Node('FunctionCall')
        node.add_child(Node('Identifier', token.lexeme))
        self.consume(token.token)
        token = self.current_token()
        self.consume('D6')
        node.add_child(self.parse_call_arguments())
        token = self.current_token()
        if token.token == 'D3':
            self.consume('D3')
            return node
        else:
            raise Exception('Ожидалась точка с запятой')

    def parse_arguments(self):
        '''парсит аргументы функции при ее объявлении'''
        node = Node('Arguments')
        token = self.current_token()
        while token.token != 'D7':
            token = self.current_token()
            child_node = Node('Argument')
            if token.token in ['K17', 'K18', 'K22', 'ID']:
                child_node.add_child(Node('Type', token.lexeme))
                self.consume(token.token)
                token = self.current_token()
                if token.token == 'ID':
                    child_node.add_child(Node('Arg', token.lexeme))
                    self.consume(token.token)
                    token = self.current_token()
                    if token.token == 'D2':
                        self.consume(token.token)
                        node.add_child(child_node)
                    elif token.token == 'D7':
                        self.consume(token.token)
                        node.add_child(child_node)
                        break
                    else:
                        raise Exception("пропущена запятая или закрывающая скобка")
                else:
                    raise Exception(f"Ошибка 5: ожидалось имя переменной, а получили{token.lexeme}")
            else:
                raise Exception(f"Ошибка 4: ожидался тип данных переменной, а получили{token.lexeme}")
        return node

    def parse_call_arguments(self):
        '''парсит аргументы функции при ее вызове'''
        node = Node('Arguments')
        token = self.current_token()
        while token.token != 'D7':
            token = self.current_token()
            child_node = Node('Argument')
            if token.token in ['N1', 'N2', 'N3', 'ID']:
                child_node.add_child(Node('Value', token.lexeme))
                self.consume(token.token)
                token = self.current_token()
                if token.token == 'D2':
                    self.consume(token.token)
                    node.add_child(child_node)
                elif token.token == 'D7':
                    self.consume(token.token)
                    node.add_child(child_node)
                    break
                else:
                    raise Exception("пропущена запятая или закрывающая скобка")
            else:
                raise Exception(f"Ошибка 6: ожидалось значение, а получили{token.lexeme}")
        return node

    def parse_cout(self):
        '''Парсит вывод'''
        if self.tokens[self.position].token == 'K24':
            self.consume('K24')
            if self.tokens[self.position].token == 'O25':
                self.consume('O25')
                token = self.tokens[self.position]
                if token.token == 'ID' or token.token == 'N1' or token.token == 'N2' or token.token == 'N3':
                    self.consume(token.token)
                    if self.tokens[self.position].token == 'D3':
                        self.consume('D3')
                        node = Node('Cout', token.lexeme)
                        return node
        raise Exception('Ошибка вывода')

    def parse_cin(self):
        '''Парсит ввод'''
        if self.tokens[self.position].token == 'K25':
            self.consume('K25')
            if self.tokens[self.position].token == 'O26':
                self.consume('O26')
                token = self.tokens[self.position]
                if token.token == 'ID':
                    self.consume(token.token)
                    if self.tokens[self.position].token == 'D3':
                        self.consume('D3')
                        node = Node('Cin')
                        node.add_child(Node('Identifirer', token.lexeme))
                        return node
        raise Exception('Ошибка ввода')

    def parse_identifier(self):
        '''Парсит идентификтор (слегка бесполезная функция,
        от нее можно отказаться)'''
        token = self.current_token()
        # print (token.token)
        # print (token.lexeme)
        if token.token == 'ID':
            id_node = Node('Identifier', token.lexeme)
            self.consume('ID')
            return id_node
        else:
            raise Exception(f'Ошибка 10: ожидался идентификатор, а получили {token.token}')

    def parse_assignment(self):
        '''Парсит присваивание, пытаюсь запихнуть сюда
        и присваивание математических/логических выражений.
        пока что присвоить можно только значение или идентификатор'''
        node = Node('Assignment')
        node.add_child(self.parse_identifier())
        token = self.current_token()
        if token.token == 'O2':
            node.add_child(Node('Operator', token.lexeme))
            self.consume('O2')
            if self.tokens[self.position].token == 'D3':
                self.consume('D3')
                return node
        if token.token == 'O5':
            node.add_child(Node('Operator', token.lexeme))
            self.consume('O5')
            if self.tokens[self.position].token == 'D3':
                self.consume('D3')
                return node
        if token.token in ['O23', 'O6', 'O3', 'O8', 'O10', 'O12', 'O24']:
            if token.token == 'O24':
                node.add_child(Node('BooleanOperator', token.lexeme))
            else:
                node.add_child(Node('AssigOperator', token.lexeme))
            self.consume(token.token)
            node.add_child(self.parse_expression())
            while self.tokens[self.position].token != 'D3':
                token = self.current_token()
                if token.token in ['O1', 'O4', 'O7', 'O11', 'O9', 'O24']:
                    node.add_child(Node('Operator', token.lexeme))
                    self.consume(token.token)
                    node.add_child(self.parse_expression())
            if self.tokens[self.position].token == 'D3':
                self.consume('D3')
                return node
            else:
                raise Exception('Ошибка 11: ожидалось выражение')
        else:
            raise Exception('Ошибка 11: ожидалось выражение')            

    def parse_expression(self):
        '''Парсит значение переменной (тоже слегка бесполезная функция)'''
        token = self.current_token()
        if token.token == 'N1':
            value_node = Node('Integer', token.lexeme)
            self.consume('N1')
            return value_node
        elif token.token == 'N2':
            value_node = Node('Float', token.lexeme)
            self.consume('N2')
            return value_node
        elif token.token == 'N3':
            value_node = Node('String', token.lexeme)
            self.consume('N3')
            return value_node
        elif token.token == 'ID':
            value_node = Node('Identificator', token.lexeme)
            self.consume('ID')
            return value_node
        elif token.token == 'K21' or token.token == 'K23':
            value_node = Node('Boolean', token.lexeme)
            self.consume(token.token)
            return value_node
        else:
            raise Exception('Ошибка 6: ожидалось значение')

    def parse_if(self):
        '''Парсит конструкцию if с возможной веткой else'''
        node = Node('If')
        token = self.current_token()

        if token.token == 'K6':  # "if"
            self.consume('K6')
            condition_node = Node('Condition')
            token = self.current_token()

            if token.token == 'D6':  # "("
                self.consume('D6')
                condition_node.add_child(self.parse_expression())
                token = self.current_token()

                while token.token != 'D7':  # ")"
                    if token.token in ['O1', 'O4', 'O7', 'O11', 'O9', 'O24']:
                        condition_node.add_child(Node('Operator', token.lexeme))
                        self.consume(token.token)
                        condition_node.add_child(self.parse_expression())
                    token = self.current_token()

                if token.token == 'D7':  # ")"
                    self.consume('D7')
                    node.add_child(condition_node)

                    if self.current_token().token == 'D4':  # "{"
                        self.consume('D4')
                        body_node = Node('Body')

                        while self.current_token().token != 'D5':  # "}"
                            body_node.add_child(self.parse_code_block())

                        self.consume('D5')  # Закрывающая скобка "}"
                        node.add_child(body_node)

                        # Проверка на наличие ветки else
                        if self.current_token().token == 'K7':  # "else"
                            self.consume('K7')
                            else_node = Node('Else')

                            if self.current_token().token == 'D4':  # "{"
                                self.consume('D4')

                                while self.current_token().token != 'D5':  # "}"
                                    else_node.add_child(self.parse_code_block())

                                self.consume('D5')  # Закрывающая скобка "}"
                                node.add_child(else_node)
                            else:
                                raise Exception('Expected "{" after else')
                        return node
                    else:
                        raise Exception('Expected "{" after if condition')
                else:
                    raise Exception('Expected ")" after if condition')
            else:
                raise Exception('Expected "(" after if')
        else:
            raise Exception('Expected "if" keyword')

    def parse_while(self):
        '''Парсит цикл while'''
        node = Node('While')
        token = self.current_token()

        if token.token == 'K4':
            self.consume('K4')
            condition_node = Node('Condition')
            token = self.current_token()

            if token.token == 'D6':
                self.consume('D6')
                condition_node.add_child(self.parse_expression())
                token = self.current_token()

                while token.token != 'D7':
                    if token.token in ['O1', 'O4', 'O7', 'O11', 'O9', 'O24']:
                        condition_node.add_child(Node('Operator', token.lexeme))
                        self.consume(token.token)
                        condition_node.add_child(self.parse_expression())
                    token = self.current_token()

                if token.token == 'D7':
                    self.consume('D7')
                    node.add_child(condition_node)

                    if self.current_token().token == 'D4':
                        self.consume('D4')
                        body_node = Node('Body')

                        while self.current_token().token != 'D5':
                            body_node.add_child(self.parse_code_block())

                        self.consume('D5')
                        node.add_child(body_node)
                        return node
                    else:
                        raise Exception('Expected "{" after while condition')
                else:
                    raise Exception('Expected ")" after while condition')
            else:
                raise Exception('Expected "(" after while')
        else:
            raise Exception('Expected "while" keyword')

    def print_syntax_tree(self, node, level=0):
        '''Рекурсивно выводит синтаксическое дерево.'''
        if node is None:
            return
        print("\t" * level + f"{node.node_type}: {node.value if node.value is not None else ''}")
        for child in node.children:
            self.print_syntax_tree(child, level + 1)
