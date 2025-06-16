def rectangle(hauteur,largeur):
    for line in range(hauteur):
        l = ''
        for colonne in range(largeur):
              if(line==hauteur//2) or (colonne==largeur//2) or (line == hauteur-1) or (line==0) or (colonne==largeur-1) or (colonne==0) or (line +colonne ==largeur-1) or (line +colonne ==line*2):
                 l = l + '*'
              else:
                l = l + ' '
        print(l)

rectangle(11,11)