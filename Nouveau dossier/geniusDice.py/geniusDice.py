import random, copy

def covertSingle(dice):
    letters = {"A": 5, "B": 4, "C": 3, "D": 2, "E":1, "F": 0}
    numbers = {"6": 0, "5": 6, "4": 12, "3": 18, "2": 24, "1": 30}
    return letters[dice[0]] + numbers[dice[1]]

def convertMultiple(*die):
    binary = 0

    for dice in die:
        binary += 1 << covertSingle(dice)
    
    return bin(binary)

def toBitMaskArray(binary):
    return [1-int(i) for i in binary[2:]]

def toBitMask(binary):
    b = copy.copy(binary)
    b.reverse()
    integrer = 0

    for i in range(len(b)):
        integrer += b[i] * 2**i
        print((i, b[i]))

    return integrer

def rollDice():
    dés = [
        ['A1', 'C1', 'D1', 'D2', 'E2', 'F3'],
        ['A4', 'B5', 'C5', 'C6', 'D6', 'F6'],
        ['D5', 'E4', 'E5', 'E6', 'F4', 'F5'],
        ['A5', 'F2', 'A5', 'F2', 'B6', 'E1'],
        ['A2', 'A3', 'B1', 'B2', 'B3', 'C2'],
        ['B4', 'C3', 'C4', 'D3', 'D4', 'E3'],
        ['A6', 'A6', 'A6', 'F1', 'F1', 'F1']
    ]

    valeurs = []

    for dice in dés:
        valeurs.append(dice[random.randint(0, 5)])

    return valeurs

print(toBitMaskArray("0b1011"))
print(toBitMask([1,0,1,1]))