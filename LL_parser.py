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

print(reglas)

# FIRST
# regla 1: terminal
for i in grammar.keys():
    if grammar[i]['tipo']=="T":
        grammar[i]['first'].append(i)
    else:
        for k in reglas.keys():
            if reglas[k]['Izq'] == i:
                grammar[i]['first']=grammar[reglas[k]['Der'][0]]['first']

print("Gramatica: ", grammar)

# regla 2: incluir first de otro no terminal
for A in grammar.keys():
    if grammar[A]['tipo'] in ('V', 'I'):
        first_set = []
        for key in reglas.keys():
            if reglas[key]['Izq'] == A:
                deriv = reglas[key]['Der']
                if not deriv:
                    if "'" not in first_set:
                        first_set.append("'") 
                    continue
                include_eps = True
                for sym in deriv:
                    for f in grammar[sym]['first']:
                        if f != "'" and f not in first_set:
                            first_set.append(f)
                    if "'" in grammar[sym]['first']:
                        continue
                    include_eps = False
                    break
                if include_eps and "'" not in first_set:
                    first_set.append("'")  
        grammar[A]['first'] = first_set

# regla 2 follows:  first(L) - {''} C follow(A)
for i in reglas.keys():
    for j in range(len(reglas[i]['Der'])-1):
        if grammar[reglas[i]['Der'][j]]["tipo"]=="V":
            grammar[reglas[i]['Der'][j]]["follow"]+=grammar[reglas[i]['Der'][j+1]]['first']
            
# regla 3 follows: follow(B) C follow(A)
for i in reglas.keys():
    if grammar[reglas[i]['Der'][-1]]['tipo']=="V":
        grammar[reglas[i]['Der'][-1]]["follow"]+=grammar[reglas[i]['Izq'][0]]["follow"]

# TABLA
for i in reglas.keys():
    for j in  grammar[reglas[i]['Der'][0]]['first']:
        tabla[reglas[i]['Izq'][0]][j].append(reglas[i])

print("Reglas: ",reglas)

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

##################
print("\n")
print("\n")
print("MATRIZ")

terminales.append("$")
print(f"{'':20}", end="")
for t in terminales:
    print(f"{t:<20}", end="")
print()

print("-" * (12 + 20 * len(terminales)))
for no_terminal, reglas in tabla.items():
    print(f"{no_terminal:20}", end="")
    for t in terminales:
        producciones = reglas[t]
        if producciones:
            produccion_strs = ["{} → {}".format(p["Izq"], " ".join(p["Der"])) for p in producciones]
            print(f"{' / '.join(produccion_strs):<20}", end="")
        else:
            print(f"{'-':<20}", end="")
    print()


###########
code = open("input.txt","r")
sent = code.readlines()

cadena = sent[0]+"$"
pila = start

##################
print("\n")
print("\n")
print("ANALISIS")

while True:
    pila_str = ' '.join(pila)
    entrada_str = ''.join(cadena)
    if (len(cadena)==1) and (len(pila)==0):
        print("CADENA VALIDA")
        break
    if (grammar[pila[-1]]["tipo"] in ["I","V"]) and (len(tabla[pila[-1]][cadena[0]])>=1):
        produccion = tabla[pila[-1]][cadena[0]][0]
        produccion_str = f"{produccion['Izq']} → {' '.join(produccion['Der'])}"
        print(f"{pila_str:<30} {entrada_str:<30} {'Regla: ' + produccion_str}")
        a = pila[-1]
        pila.pop()
        pila+=tabla[a][cadena[0]][0]['Der'][::-1]
    elif (grammar[pila[-1]]["tipo"]=="T") and pila[-1]==cadena[0]:
        print(f"{pila_str:<30} {entrada_str:<30} {'Match: ' + cadena[0]}")
        pila.pop()
        cadena = cadena[1:] 
    else:
        print("Cadena no valida")
        break

print("Gramática:", grammar)