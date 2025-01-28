class CodeGenerator:
    def __init__(self):
        self.code = []

    def generate(self, node):
        if node.node_type == 'Program':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'Headers':
            pass
        elif node.node_type == 'Namespaces':
            pass
        elif node.node_type == 'MainFunction':
            self.code.append("public class Main {")
            self.code.append("public static void main(String[] args) {")
            for child in node.children:
                self.generate(child)
            self.code.append("}")
            self.code.append("}")
        elif node.node_type == 'While':
            for child in node.children:
                if child.node_type == 'Condition':
                    self.code.append(f'while ({" ".join([sub_child.value for sub_child in child.children])})' + '{')
                if child.node_type == 'Body':
                    for sub_child in child.children:
                        self.generate(sub_child)
                    self.code.append('}')
        elif node.node_type == 'If':
            for child in node.children:
                if child.node_type == 'Condition':
                    self.code.append(f'if ({" ".join([sub_child.value for sub_child in child.children])})' + '{')
                if child.node_type == 'Body':
                    for sub_child in child.children:
                        self.generate(sub_child)
                    self.code.append('}')
                if child.node_type == 'Else':
                    self.code.append('else {')
                    for sub_child in child.children:
                        self.generate(sub_child)
                    self.code.append('}')
        elif node.node_type == 'Body':
            for child in node.children:
                self.generate(child)
            if 'Scanner scanner = new Scanner(System.in);' in self.code:
                self.code.append('scanner.close();')
        elif node.node_type == 'Instruction':
            for child in node.children:
                self.generate(child)
        elif node.node_type == 'Declaration':
            var_type = node.children[0].value
            identifier = node.children[1].value
            if len(node.children) > 2:
                next = node.children[2]
                if next.node_type == 'FunctionDeclaration':
                    self.generate_function_declaration(var_type, identifier, next, '')
                else:
                    self.code.append(f'{var_type} {identifier} = {next.value};')
            else:
                self.code.append(f'{var_type} {identifier};')
        elif node.node_type == 'FunctionCall':
            id = node.children[0].value
            agruments_node = node.children[1]
            arguments = ''
            for arg in agruments_node.children:
                arguments += ' ' + arg.children[0].value + ','
            self.code.append(f'{id}({arguments[:-1]} );')

        elif node.node_type == 'ClassDeclaration':
            self.generate_class_declaration(node)
        elif node.node_type == 'Assignment':
            identifier = node.children[0].value
            assign_operator = node.children[1].value
            self.code.append(f'{identifier} {assign_operator} {" ".join([child.value for child in node.children[2:]])};')
        elif node.node_type == 'Cout':
            self.code.append(f'System.out.println({node.value});')
        elif node.node_type == 'ClassBlockDeclaration':
            ClassDeclarated = node.children[0].value
            ClassDeclaratedName = node.children[1].value
            ClassDeclaratedSourceName = node.children[2].value
            arguments_node = node.children[3]
            arguments = ''
            for arg in arguments_node.children:
                arguments += arg.children[0].value + ','
            self.code.append(f'{ClassDeclarated} {ClassDeclaratedName} = new {ClassDeclaratedSourceName}({arguments[:-1]});')
        elif node.node_type == 'ClassBlockDeclarationMethod':
            ClassDeclarated = node.children[0].value
            ClassDeclaratedName = node.children[1].value
            arguments_node = node.children[2]
            arguments = ''
            for arg in arguments_node.children:
                arguments += arg.children[0].value + ','
            self.code.append(f'{ClassDeclarated}.{ClassDeclaratedName}({arguments[:-1]});')
        elif node.node_type == 'ClassBlockDeclarationSimple':
            NameClass = node.children[0].value
            Name = node.children[1].value
            self.code.append(f'{NameClass} {Name} = new {NameClass}();')
        elif node.node_type == 'Cin':
            value = node.children[1].value
            if 'import java.util.Scanner;' not in self.code:
                self.code.insert(0, 'import java.util.Scanner;')
            if 'Scanner scanner = new Scanner(System.in);' not in self.code:
                self.code.append('Scanner scanner = new Scanner(System.in);')
            if value == 'string':
                type = 'Line'
            elif value == 'int':
                type = 'Int'
            elif value == 'bool':
                type = 'Boolean'
            elif value == 'float':
                type = 'Double'
            else:
                raise Exception(f'ошибка типа данных считываемой переменной{node.children[0].value}')
            self.code.append(f'{node.children[0].value} = scanner.next{type}();')
        elif node.node_type == 'Return':
            self.generate_return(node)
        else:
            raise Exception(f'Unknown node type: {node.node_type}')

    def generate_function_declaration(self, var_type, identifier, node, access_modifier):
        '''Генерирует код для метода'''
        arguments_node = node.children[0]
        arguments = ''
        for arg in arguments_node.children:
            arguments += ' ' + arg.children[0].value + ' ' + arg.children[1].value + ','
        if access_modifier != '':
            self.code.append(f'{access_modifier} {var_type} {identifier}({arguments[:-1]} )' + ' {')
        else:
            self.code.append(f'{var_type} {identifier}({arguments[:-1]} )' + ' {')
        self.generate(node.children[1])
        self.code.append('}')

    def generate_class_declaration(self, node):
        '''Генерирует код для объявления класса'''
        class_name = node.children[0].value
        access_modifier = 'public' + ' '
        self.code.append(f'{access_modifier}class {class_name} {{')

        for child in node.children[1:]:
            if child.node_type == 'AccessModifier':
                self.generate_access_modifier(child)

        self.code.append('}')

    def generate_access_modifier(self, node):
        '''Генерирует код для переменных с модификатором доступа'''
        access_modifier = node.value

        for child in node.children[0:]:
            if child.node_type == 'Declaration':
                self.generate_variable_declaration(child, access_modifier)

    def generate_variable_declaration(self, node, access_modifier):
        '''Генерирует поля для класса с учетом модификатора доступа'''
        var_type = node.children[0].value
        identifier = node.children[1].value
        if len(node.children) > 2:
            value = node.children[2].value
            next = node.children[2]
            if next.node_type == 'FunctionDeclaration':
                self.generate_function_declaration(var_type, identifier, next, access_modifier)
            else:
                self.code.append(f'{var_type} {identifier} = {next.value};')
        else:
            access_modifier = access_modifier + ' '
            self.code.append(f'    {access_modifier}{var_type} {identifier};')

    def generate_return(self, node):
        '''Генерирует код для оператора return'''
        if node.children:
            self.code.append(f'return {node.children[0].value};')
        else:
            self.code.append('return;')

    def get_code(self):
        return "\n".join(self.code)