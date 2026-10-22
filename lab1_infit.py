import math



# Лексер
def tokenize(text):
    tokens_list = []   
    position = 0       

    while position < len(text):
        char = text[position]    

        if char == " ":
            position += 1

        elif char.isdigit() or char == ".":
            start = position
            while position < len(text) and (text[position].isdigit() or text[position] == "."):
                position += 1
            number_text = text[start:position]
            if number_text.count(".") > 1 or number_text == ".":
                raise ValueError("Некорректное число: " + number_text)
            tokens_list.append(("NUM", float(number_text)))

        elif char.isalpha():
            start = position
            while position < len(text) and text[position].isalpha():
                position += 1
            word = text[start:position]
            if word == "log":
                tokens_list.append(("FUNC", "log"))
            else:
                raise ValueError("Неизвестная функция: " + word)

        elif char in "+-*/":
            tokens_list.append(("OP", char))
            position += 1

        elif char == "(":
            tokens_list.append(("LPAR", "("))
            position += 1

        elif char == ")":
            tokens_list.append(("RPAR", ")"))
            position += 1

        elif char == "!":
            if position + 1 < len(text) and text[position + 1] == "=":
                tokens_list.append(("OP", "!="))
                position += 2
            else:
                raise ValueError("После '!' ожидался символ '='")

        else:
            raise ValueError("Неизвестный символ: " + char)

    return tokens_list



# Парсер
tokens = [] 
pos = 0       


def current():
    if pos < len(tokens):
        return tokens[pos]
    return ("END", None)


def skip_right_bracket():
    global pos
    if current() != ("RPAR", ")"):
        raise ValueError("Ожидалась закрывающая скобка ')'")
    pos += 1


def parse_comparison():
    global pos
    left = parse_sum_diff()
    if current() == ("OP", "!="):
        pos += 1
        right = parse_sum_diff()
        if left != right:
            return 1
        return 0
    return left


def parse_sum_diff():
    global pos
    result = parse_mul_div()
    while current() in (("OP", "+"), ("OP", "-")):
        operator = current()[1]
        pos += 1
        right = parse_mul_div()
        if operator == "+":
            result = result + right
        else:
            result = result - right
    return result


def parse_mul_div():
    global pos
    result = parse_unary()
    while current() in (("OP", "*"), ("OP", "/")):
        operator = current()[1]
        pos += 1
        right = parse_unary()
        if operator == "*":
            result = result * right
        else:
            if right == 0:
                raise ValueError("Деление на ноль")
            result = result / right
    return result


def parse_unary():
    global pos
    if current() == ("OP", "-"):
        pos += 1
        return -parse_unary()
    if current() == ("OP", "+"):
        pos += 1
        return parse_unary()
    return parse_value()


def parse_value():
    global pos
    kind, value = current()

    if kind == "NUM":
        pos += 1
        return value

    if kind == "LPAR":
        pos += 1
        result = parse_comparison()
        skip_right_bracket()
        return result

    if kind == "FUNC":
        pos += 1
        if current() != ("LPAR", "("):
            raise ValueError("После log ожидалась скобка '('")
        pos += 1
        argument = parse_comparison()
        skip_right_bracket()
        if argument <= 0:
            raise ValueError("log определён только для x > 0")
        return math.log(argument)

    raise ValueError("Ожидалось число, скобка или log")


# Вычисление строки целиком
def calculate(text):
    global tokens, pos
    tokens = tokenize(text)   
    pos = 0                   
    result = parse_comparison()
    if pos != len(tokens):
        raise ValueError("Лишние символы в конце выражения")
    return result



# Основной цикл программы
while True:
    line = input("Введите выражение: ") 
    if line.strip() == "":
        break
    try:
        print("Результат:", calculate(line))
    except ValueError as error:
        print("Ошибка:", error)


