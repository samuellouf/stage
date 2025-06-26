class Pile:
    def __init__(self):
        self.__stack__ = []

    def empiler(self, i):
        self.__stack__.append(i)

    def depiler(self):
        if self.taille() == 0: return
        return self.__stack__.pop()

    def taille(self):
        return len(self.__stack__)