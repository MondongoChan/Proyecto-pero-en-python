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

def calcFirst(gramatica):
    first = {}

    def recursivo(gramatica, first, non_terminal):
        for produccion in gramatica[non_terminal]:
            if produccion[0] not in gramatica.keys():
                first[non_terminal].add(produccion[0])
            elif produccion[0] == non_terminal:
                continue
            else:
                recursivo(gramatica, first, produccion[0])
                if '0' in first[produccion[0]]:
                    first[non_terminal].update(first[produccion[0]])
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
                    if symbol in gramatica: # El símbolo es un símbolo no terminal?
                        if symbol in gramatica.keys():
                            first = recursivo(gramatica, first, symbol)
                        elif '0' not in first[symbol]:
                            first[non_terminal].update(first[symbol])
                            break
                        else:
                            first[non_terminal].update(first[symbol] - {'0'})
                            updated = True
                    else:
                        first[non_terminal].add(symbol) # El símbolo es un símbolo terminal
                else:
                    first[non_terminal].add('0') # La producción es vacía
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

def main():
    gramatica = almacenar_gramatica()
    first = calcFirst(gramatica)
    print(first)
    flw = {}
    start_symbol = list(gramatica.keys())[0]
    flw[start_symbol] = set('$')
    for non_terminal in gramatica:
        flw[non_terminal] = follow(flw, first, non_terminal, gramatica)
    print(flw)
    
main()