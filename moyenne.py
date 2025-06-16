def moyenne (notes):
    return sum(notes)/len(notes)

resultat = moyenne([12,13,15])

print(resultat)

def ecarttype(liste):
    moyenne = sum(liste) / len(liste)
    variance = sum((x - moyenne) ** 2 for x in liste) / len(liste)
    return variance ** 0.5  # racine carrée sans math.sqrt

def ecarttype2(notes):
    m = sum(notes) / len(notes)
    return (sum([(i-m)**2 for i in notes])/len(notes))**0.5

resultat = ecarttype([2, 3, -5, 20])
print("Écart-type :", resultat)
resultat2 = ecarttype2([2, 3, -5, 20])
print("Écart-type :", resultat2)