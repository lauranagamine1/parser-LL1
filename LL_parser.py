import re
import json

archivo = open("grammar.txt","r")
sent = archivo.readlines()
variables = []
terminales = []

t1 = sent[0].split()
start = [t1[0]]

# SCANNER
for production in sent:
    tokens = production.split() # tokens separa todo
    for tok in tokens:
        if tok.isalpha() and tok.isupper() and tok != "'":
            if tok not in variables and tok not in start:
                variables.append(tok)
        else:
            # cualquier otro token (minuscula, digito, "'" epsilon)
            if tok == "->":
                pass
            elif tok == "|":
                pass
            elif tok not in terminales:
                terminales.append(tok)

#gramatica
grammar = {}

tabla = {}
print("Cadena inicial: ",start)
print("Variables: ",variables)
print("Terminales: ", terminales, "\n")

for i in start + variables:
    tabla[i]={}
    for j in terminales:
        tabla[i][j]=[]
    tabla[i]["$"]=[]

for i in start:
    grammar[i]={"tipo":"I","first":[],"follow":["$"]}

for j in terminales:
    grammar[j]={"tipo":"T","first":[]}

for j in variables:
    grammar[j]={"tipo":"V","first":[],"follow":[]}

# DICCIONARIO DE REGLAS
archivo = open("grammar.txt","r")
sent = archivo.readlines()
print(sent)
reglas ={}
i=1

expanded = []
for line in sent:
    line = line.strip()
    if '->' not in line:
        continue
    lhs, rhs = line.split('->', 1)
    # separada por |, indica que es un nuevo no terminal
    for alt in rhs.split('|'):
        expanded.append(f"{lhs}->{alt.strip()}")
sent = expanded

for i in range(len(sent)):
    reglas['regla'+str(i+1)] = {}

j = 0

for i in reglas.keys():
    reglas[i]['Izq'] = sent[j][0]
    j+=1

for i in range(len(sent)):
    sent[i]= sent[i][2:]
j=0

for i in reglas.keys():
    reglas[i]['Der'] = []
    for k in sent[j]:
        if k in grammar.keys():
            reglas[i]['Der'].append(k)
    j+=1

print("Reglas: ", reglas)

# FIRST
# regla 1: terminal
for i in grammar.keys():
    if grammar[i]['tipo']=="T":
        grammar[i]['first'].append(i)
    else:
        for k in reglas.keys():
            if reglas[k]['Izq'] == i:
                grammar[i]['first']=grammar[reglas[k]['Der'][0]]['first']


# regla 2: incluir first de otro no terminal
order = variables + [start[0]] 
for A in order:
    if grammar[A]['tipo'] in ('V', 'I'):
        first_set = []
        for key in reglas.keys():
            if reglas[key]['Izq'] == A:
                deriv = reglas[key]['Der']
                # producción vacía
                if not deriv:
                    if "'" not in first_set:
                        first_set.append("'")
                    continue
                include_eps = True
                for sym in deriv:
                    # agregar firsts menos e
                    for f in grammar[sym]['first']:
                        if f != "'" and f not in first_set:
                            first_set.append(f)
                    # si sym no deriva e, detiene todo
                    if "'" in grammar[sym]['first']:
                        continue
                    include_eps = False
                    break
                # si todos derivan e, incluir e
                if include_eps and "'" not in first_set:
                    first_set.append("'")
        grammar[A]['first'] = first_set

# regla 2 follows:  first(L) - {''} C follow(A)
for k in reglas.keys():
    deriv = reglas[k]['Der']
    for idx in range(len(deriv)-1):
        B = deriv[idx]
        beta = deriv[idx+1]
        if grammar[B]['tipo'] in ("V", "I"):
            for f in grammar[beta]['first']:
                if f != "'" and f not in grammar[B]['follow']:
                    grammar[B]['follow'].append(f)

# regla 3 follows: follow(B) C follow(A)
for _ in range(len(reglas)): # repetimos lo suficiente para asegurar que todos los follow interactuan
    for key in reglas:
        deriv = reglas[key]['Der']
        A = reglas[key]['Izq']
        for idx, B in enumerate(deriv):
            if grammar[B]['tipo'] not in ("V", "I"):
                continue
            beta = deriv[idx+1:]
            beta_derives_epsilon = all("'" in grammar[s]['first'] for s in beta) if beta else True
            if beta_derives_epsilon:
                # propagar follow(A) aa follow(B)
                for f in grammar[A]['follow']:
                    if f not in grammar[B]['follow']:
                        grammar[B]['follow'].append(f)


#################
print("TABLA")
print("\n")
print(f"{'Símbolo':<10} {'Tipo':<8} {'FIRST':<20} {'FOLLOW':<20}")
print("-" * 60)

for simbolo, datos in grammar.items():
    tipo = datos['tipo']
    first = ", ".join(datos.get('first', []))
    follow = ", ".join(datos.get('follow', [])) if 'follow' in datos else "-"
    print(f"{simbolo:<10} {tipo:<8} {first:<20} {follow:<20}")

print()
##################

# TABLA
for key, rule in reglas.items():
    A = rule['Izq']
    deriv = rule['Der']
    if not deriv: 
        continue
    rhs_str = ' '.join(deriv) if deriv else "''"
    first0 = grammar[deriv[0]]['first']
    for f in first0:
        if f != "'":
            tabla[A][f].append(key)
        else:
            for fol in grammar[A]['follow']:
                tabla[A][fol].append(key)
    

print(f"{'':20}" + ''.join(f"{t:<20}" for t in terminales+['$']))
print("-"*(20*(len(terminales)+1)))
for nt, row in tabla.items():
    #print(nt) 
    #print(row)
    print(f"{nt:20}", end="")
    for t in terminales + ['$']:
        prods = row[t]
        if prods:
            # traducimos cada clave a su producción completa
            prod_strs = [
                f"{reglas[p]['Izq']} -> {' '.join(reglas[p]['Der'])}"
                for p in prods
            ]
            if(len(prod_strs) > 1):
                raise Exception("Grammar is not LL(1)")
            print(f"{' / '.join(prod_strs):<20}", end="")
        elif t == '$':
            print(f"Extraer", end = "")
        elif t in grammar[nt]['follow']:
            print(f"{'Extraer':<20}", end = "")
        else:
            print(f"{'Explorar':<20}", end="")
    print()

valid = True

# ANÁLISIS LL(1)
print("\nANÁLISIS")
with open("input.txt") as f:
    inp = f.readline().strip() + '$'
pila = ['$'] + start.copy()
entrada = inp
while True:
    if not entrada and not pila:
        if valid:
            print("CADENA VALIDA")
        else:
            print("CADENA INVALIDA")
        break
    lookahead = entrada[0]
    if lookahead.isspace():
        entrada = entrada[1:]
        continue
    top = pila[-1]
    if top == '$':
        if lookahead == '$':
            print(f"{' '.join(pila):<30}{entrada:<30}Match: {lookahead}")
            pila.pop()
            entrada = entrada[1:]
        else: 
            print(f"{' '.join(pila):<30}{entrada:<30}Pila is empty")
            print("CADENA INVALIDA")
            break
    elif grammar[top]['tipo'] in ['I','V'] and lookahead in tabla[top] and tabla[top][lookahead]:
        pr = tabla[top][lookahead][0]
        # construimos la cadena de producción completa
        full = f"{reglas[pr]['Izq']} -> {' '.join(reglas[pr]['Der'])}"
        print(f"{' '.join(pila):<30}{entrada:<30}Regla: {full}")

        pila.pop()
        rhs = reglas[pr]['Der']
        if rhs == ["'"]:
            continue
        pila.extend(rhs[::-1])
    elif grammar[top]['tipo']=='T' and top==lookahead:
        print(f"{' '.join(pila):<30}{entrada:<30}Match: {lookahead}")
        pila.pop()
        entrada = entrada[1:]
    elif lookahead == '$':
        #print(f"Extraer", end = "")
        print(f"{' '.join(pila):<30}{entrada:<30}Extraer")
        valid = False
        pila.pop()
    elif lookahead in grammar[top]['follow']:
        #print(f"{'Extraer':<20}", end = "")
        print(f"{' '.join(pila):<30}{entrada:<30}Extraer")
        valid = False
        pila.pop()
    else:
        #print(f"{'Explorar':<20}", end="")
        print(f"{' '.join(pila):<30}{entrada:<30}Explorar")
        valid = False
        entrada = entrada[1:]
