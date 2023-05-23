from collections import deque

# Esta función se encarga de recibir inputs y guardar la gramatica
def guardar_gramática():

    archivo = open('grammars_neusa.txt')
    lista_de_reglas = []
    diccionario_de_reglas = {}

    # Ingresar terminales espaciados
    terminales = archivo.readline().strip().split(' ')
    # Ingresar no terminales espaciados, incluyendo S como gramatica extendida
    no_terminales = archivo.readline().strip().split(' ')

    for no_terminal in no_terminales:
        producciones = archivo.readline().strip().split(' ')

        for producción in producciones:
            if no_terminal in diccionario_de_reglas: diccionario_de_reglas[no_terminal].extend([producción])
            else: diccionario_de_reglas[no_terminal] = [producción]
            lista_de_reglas.append(no_terminal + '->' + producción)

    return {'diccionario_de_reglas': diccionario_de_reglas, 'lista_de_reglas': lista_de_reglas, 'no_terminales': no_terminales, 'terminales': terminales}


def calFirstprod(prod, first):
    iterador = 0
    first_product = set()

    def validar(iterador, prod, first_product, first):
        if prod[iterador].isupper():
            first_product.update(first[prod[iterador]])

            if '0' in first_product:
                iterador += 1
                if iterador > len(prod) - 1:
                    return first_product
                first_product.remove('0')
                remaining_first = validar(iterador, prod, set(first_product), first)
                first_product.update(remaining_first)
            else:
                if iterador >= 1:
                    first_product.add('0')
                    first_product.update(first[prod[iterador]])
            return first_product
        else:
            a = prod[iterador]
            first_product.add(a)
            return first_product

    first_product = validar(iterador, prod, first_product, first)
    return first_product

def first(gramatica):
    first = {}
    first_product = {}
    def recursivo(gramatica, first, non_terminal):
        for produccion in gramatica[non_terminal]:
            if produccion[0] not in gramatica.keys():
                first[non_terminal].add(produccion[0]) # Almacenar el first de la producción
            elif produccion[0] == non_terminal:
                continue
            else:
                recursivo(gramatica, first, produccion[0])
                if '0' in first[produccion[0]]:
                    first[non_terminal].update(first[produccion[0]] )
                else:
                    first[non_terminal].update(first[produccion[0]])
                    break
        return first

    for non_terminal in gramatica.keys():
        first[non_terminal] = set()

    updated = True
    while updated:
        updated = False

        # Recorrer todas las claves y valores del diccionario
        for non_terminal, productions in gramatica.items():
            for production in productions:
                if len(production) > 0:
                    symbol = production[0]
                    if symbol in gramatica:  # El simbolo es un símbolo no terminal?
                        if symbol in gramatica.keys():
                            first = recursivo(gramatica, first, non_terminal)
                        elif '0' not in first[symbol]:
                            first[non_terminal].update(first[symbol])  # Almacenar el first de la producción
                            break
                        else:
                            first[non_terminal].update(first[symbol] - {'0'})
                            updated = True
                    else:
                        # El símbolo es un símbolo terminal
                        first[non_terminal].add(symbol)
                else:
                    first[non_terminal].add('0')  # La producción es vacía
                    updated = True

    return first


def follow(flw, first, symbol, grammar):
    if symbol not in flw:
        flw[symbol] = set()
    for nt in grammar.keys():
        for production in grammar[nt]:
            pos = production.find(symbol)
            if pos != -1:
                if pos == (len(production) - 1):
                    if nt != symbol:
                        flw[symbol] = flw[symbol].union(follow(flw, first, nt, grammar))
                else:
                    first_next = set()
                    for next_symbol in production[pos+1:]:
                        if next_symbol.isupper():
                            fst_next = first[next_symbol]
                            first_next = first_next.union(first[next_symbol] - {'0'})
                            if '0' not in first[next_symbol]:
                                break
                        else:
                            first_next.add(next_symbol)
                            break
                    else:
                        fst_next = set()  # Inicializar fst_next en caso de no haber encontrado un no terminal
                    if '0' in first_next:
                        if production != symbol:
                            flw[symbol] = flw[symbol].union(follow(flw, first, production, grammar))
                            flw[symbol] = flw[symbol].union(first_next) - {'0'}
                    else:
                        flw[symbol] = flw[symbol].union(first_next)
    return flw[symbol]


def closure(I, gramatica):
    J = I
    while True:
        nuevos_items_agregados = False
        for item in J:
            partes = item.split('.')
            if partes[1] != '':
                no_terminal = partes[1][0]
                if no_terminal in gramatica:
                    for produccion in gramatica[no_terminal]:
                        nuevo_item = no_terminal + '->.' + produccion
                        if nuevo_item not in J:
                            J.append(nuevo_item)
                            nuevos_items_agregados = True
        if not nuevos_items_agregados:
            break
    return J

def goto(I, X, gramatica):
    J = []
    for item in I:
        partes = item.split('.')
        if partes[1] != '':
            simbolo = partes[1][0]
            if simbolo == X:
                nuevo_item = partes[0] + simbolo + '.' + partes[1][1:]
                J.append(nuevo_item)
    return closure(J, gramatica)

def generar_estados(gramatica, diccionario_follow):

    
    tabla = {'action': [gramatica['terminales']], 'goto': [gramatica['no_terminales']]}
    estados = []
    inicial = closure(['S->.E$'], gramatica['diccionario_de_reglas'])
    item_aceptación = 'S->.E$'
    estados.append(inicial)
    i = 0
    while i < len(estados):

        estado = estados[i]

        tabla['action'].append([' ']*len(tabla['action'][0]))
        tabla['goto'].append([' ']*len(tabla['goto'][0]))
        
        i += 1
        simbolos_punto = set(item.split('.')[1][0] for item in estado if len(item.split('.')[1]) > 0)
        
        for simbolo in simbolos_punto:
            nuevo_estado = goto(estado, simbolo, gramatica['diccionario_de_reglas'])
            if nuevo_estado not in estados:
                estados.append(nuevo_estado)

            if nuevo_estado not in estados:
                estados.append(nuevo_estado)

            if simbolo in gramatica['no_terminales']:
                # En la fila que representa el estado en la tabla goto, se guarda el número del estado transición
                tabla['goto'][i][tabla['goto'][0].index(simbolo)] = str(estados.index(nuevo_estado)+1)
            else:
                # Si el simbolo es $ y la derivación es S -> E.$, leer ese simbolo significa aceptar
                if simbolo == '$' and item_aceptación in nuevo_estado: tabla['action'][i][tabla['action'][0].index(simbolo)] = 'Acc'
                
                # Ahora vamos con el shift o reduce, analizando cada uno de los items que conforman el estado
                for item in estado:
                    # Reduce
                    if item[-1] == '.':
                        regla_reduce = gramatica['lista_de_reglas'].index(item.replace('.', ''))
                        for símbolo_del_follow in diccionario_follow[item[0]]:
                            tabla['action'][i][tabla['action'][0].index(símbolo_del_follow)] = 'R' + str(regla_reduce+1)
                    # Shift
                    else: tabla['action'][i][tabla['action'][0].index(simbolo)] = 'S' + str(estados.index(nuevo_estado)+1)

    return tabla

def predictiveParsing(input_string: str, table: dict, start_simbol: str, terminals: list, nonterminals: list) -> bool:
    stack = deque()
    stack.append(start_simbol)
    pointer = 0
    while len(stack) > 0:
        top = stack[-1]
        try:
            a = input_string[pointer]
        except:
            a = 'ε'
        if top == a:
            stack.pop()
            pointer += 1
        elif top in terminals:
            return False
        elif top in nonterminals:
            production = table[top][a]
            if production == 'Error':
                return False
            else:
                stack.pop()
                stack.extend(reversed(production))
                if stack[-1] == 'ε':
                    stack.pop()
    return True


def verify(table):
    for key, inner_dict in table.items():
        for inner_key, value in inner_dict.items():
            if value == 'No es LL1':
                return False
    return True

def main():

    gramatica = guardar_gramática() # Es el conjunto de P_lista, P_diccionario N y E
    first_símbolos = first(gramatica['diccionario_de_reglas'])
    diccionario_follow = {}
    diccionario_follow['S'] = set('$')
    for no_terminal in gramatica['no_terminales']: diccionario_follow[no_terminal] = follow(diccionario_follow, first_símbolos, no_terminal, gramatica['diccionario_de_reglas'])
    tabla = generar_estados(gramatica, diccionario_follow)

    print(tabla['action'])
    
    for i in range(len(tabla['action'])):
        for j in range(len(tabla['action'][0])):
            print(tabla['action'][i][j].ljust(5), end=' | ')
        print()
    print('\ngoto') 
    for i in range(len(tabla['goto'])):
        for j in range(len(tabla['goto'][0])):
            print(tabla['goto'][i][j].ljust(5), end=' | ')
        print()
    return ''
    print("Estados LR(0):")
    for i, estado in enumerate(autómata):
        print(f"Estado {i}:")
        for item in estado:
            print(item)
        print()
    tabla_de_parsing = crear_tabla_de_parsing(autómata)


main()