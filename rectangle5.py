def rectangle(hauteur,largeur):
    for line in range(hauteur):
        l = ''
        for colonne in range(largeur):
            if (line == hauteur-1) or (line==0) or (colonne==largeur-1) or (colonne==0):
                l = l + '*'
            else:
                l = l + ' '
        print(l)
        
rectangle(15,10)