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
            producciones[no_terminal].extend([prod.strip() for prod in producciones_texto])
        else:
            producciones[no_terminal] = [prod.strip() for prod in producciones_texto]

    return producciones

def rules(gramatica):
    reglas = []
    for non_terminal, productions in gramatica.items():
        reglas.append(non_terminal + " -> " + productions[0])
        for i in range(1, len(productions)):
            reglas.append(non_terminal + " -> " + productions[i])
    return reglas

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

def calcFollow(flw, first, symbol, grammar):
    if symbol not in flw:
        flw[symbol] = set()
    for nt in grammar.keys():
        for production in grammar[nt]:
            pos = production.find(symbol)
            if pos != -1:
                if pos == (len(production) - 1):
                    if nt != symbol:
                        flw[symbol] = flw[symbol].union(calcFollow(flw, first, nt, grammar))
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
                            flw[symbol] = flw[symbol].union(calcFollow(flw, first, production, grammar))
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

def gotoandAction(itemSet, symbol, gramatica):
    goToSet = []
    for item in itemSet:
        parts = item.split('.')
        if len(parts[1]) > 0 and parts[1][0] == symbol:
            new_item = parts[0] + symbol + '.' + parts[1][1:]
            goToSet.append(new_item)
    return closure(goToSet, gramatica)

def generar_estados(gramatica):
    estados = []
    inicial = closure(['S->.E'], gramatica)
    estados.append(inicial)
    i = 0
    while i < len(estados):
        estado = estados[i]
        i += 1
        simbolos_punto = set(item.split('.')[1][0] for item in estado if len(item.split('.')[1]) > 0)
        for simbolo in simbolos_punto:
            nuevo_estado = gotoandAction(estado, simbolo, gramatica)
            if nuevo_estado not in estados:
                estados.append(nuevo_estado)
    return estados

def transiciones(gramatica, generar_estados):
    transitions = []

    for i in range(len(generar_estados)):
        for j in range(len(generar_estados)):
            if i != j:
                for item in generar_estados[i]:
                    parts = item.split('.')
                    if len(parts[1]) > 0:
                        symbol = parts[1][0]
                        if symbol == '0':
                            symbol = 'Epsilon'
                        goToSet = gotoandAction(generar_estados[i], symbol, gramatica)
                        if goToSet == generar_estados[j]:
                            transitions.append("Transition: I{}: {} -> {} -> I{}".format(i, item, symbol, j))
                            break

    print("Transitions:")
    for transition in transitions:
        print(transition)

def main():
    gramatica = almacenar_gramatica()
    estados_lr0 = generar_estados(gramatica)
    
    print("Estados LR(0):")
    for i, estado in enumerate(estados_lr0):
        print(i, estado)
    
    print("Reglas:")
    reglas = rules(gramatica)
    for regla in reglas:
        print(regla)
    
    transiciones(gramatica, estados_lr0)
    
main()
