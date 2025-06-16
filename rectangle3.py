def rectangle(hauteur,largeur):
    for i in range(hauteur):
        if i==0:
            print("O" * largeur)
        else:
            print('*' * largeur)
        

rectangle(6,6)

