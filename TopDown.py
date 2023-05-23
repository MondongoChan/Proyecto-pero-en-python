def almacenar_gramatica():
    producciones = {}

    print("Ingrese la gramática línea por línea:")
    while True:
        linea = input()
        if linea == "-1":
            break

        partes = linea.split('->')
        no_terminal = partes[0].strip()
        producciones_texto = partes[1].strip().split('|')

        if no_terminal in producciones:
            producciones[no_terminal].extend(
                [prod.strip() for prod in producciones_texto])
        else:
            producciones[no_terminal] = [prod.strip()
                                         for prod in producciones_texto]

    return producciones
def calFirstprod(prod, first):
    iterador = 0
    first_product = set()

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

def calcFirst(gramatica):
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
                    if symbol in gramatica:  # El símbolo es un símbolo no terminal?
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

def create_parsing_table(grammar, flw, first_product):
    terminals = set()
    non_terminals = list(grammar.keys())
    parsing_table = [[''] + ['$']]  # Primera fila con los no terminales y $
    non_terminal_set = set(non_terminals)

    for productions in grammar.values():
        for production in productions:
            for symbol in production:
                if not(symbol.isupper()) and symbol != '0':
                    terminals.add(symbol)
    for terminal in terminals:
        parsing_table[0].insert(-1, terminal)

    for non_terminal in non_terminals:
        row = ['00'] * len(parsing_table[0])
        if non_terminal != '0':
            row[0] = non_terminal
        parsing_table.append(row)
        

    for non_terminal, productions in grammar.items():
        for production in productions:
            first_symbol = production[0]
            if not first_symbol.isupper() and first_symbol != '0':
                # Símbolo terminal en la primera posición de la producción
                terminal_index = parsing_table[0].index(first_symbol)
                for follow_symbol in flw[non_terminal]:
                    parsing_table[non_terminals.index(non_terminal) + 1][terminal_index] = production
            elif first_symbol.isupper():
                # Símbolo no terminal en la primera posición de la producción
                for symbol in first_product[production]:
                    if symbol != '0':
                        terminal_index = parsing_table[0].index(symbol)
                        parsing_table[non_terminals.index(non_terminal) + 1][terminal_index] = production
            else:
                for follow_symbol in flw[non_terminal]:
                    terminal_index = parsing_table[0].index(follow_symbol)
                    parsing_table[non_terminals.index(non_terminal) + 1][terminal_index] = production
                    if '$' in flw[non_terminal]:
                        terminal_index = parsing_table[0].index('$')
                        parsing_table[non_terminals.index(non_terminal) + 1][terminal_index] = '$'       
    return parsing_table
    
# Ejemplo de uso
gramatica = almacenar_gramatica()
firstprod = {}
first = calcFirst(gramatica)
start_symbol = list(gramatica.keys())[0]
flw = {}
flw[start_symbol] = set('$')
for non_terminal in gramatica:
    flw[non_terminal] = follow(flw, first, non_terminal, gramatica)
# Imprimir el conjunto "first" para cada símbolo no terminal
print("First")
for non_terminal, first_set in first.items():
    print(f"First({non_terminal}) = {first_set}")
print("follow")
for non_terminal, follow_set in flw.items():
    print(f"Follow({non_terminal}) = {follow_set}")

for non_terminal in gramatica:
    for prod in gramatica[non_terminal]:
        firstprod[prod] = calFirstprod(prod, first) 
print("first_product")
for prod, frset in firstprod.items():
    print(f"First elements({prod}) = {frset}")
    
matriz = create_parsing_table(gramatica, flw, firstprod)


for fila in matriz:
    for elemento in fila:
        print(elemento, end=' ')
    print()