def rectangle(hauteur,largeur):
    for i in range(hauteur):
        print(i*"*" +"o" + (largeur-i-1)*"*")
        
rectangle(6,6)