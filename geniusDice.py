import random

positions = {
    "A": ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5', 'E1', 'E2', 'E3', 'E4', 'E5'],
    "B": ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3', 'D1', 'D2', 'D3', 'E1', 'E2', 'E3', 'F1', 'F2', 'F3'],
    "C": "",
    "E": ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5'],
    "F": ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D4', 'E1', 'E2', 'E3', 'E4', 'F1', 'F2', 'F3', 'F4'],
    "G": ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5', 'E1', 'E2', 'E3', 'E4', 'E5'],
    "H": ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6'],
    "I": ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
}

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
    binary.reverse()
    integrer = 0

    for i in range(len(binary)):
        integrer += binary[i] * 2**i
        print((i, binary[i]))

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