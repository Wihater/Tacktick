import sys
import os
import pygame
import sqlite3
import random


class Hero:
    def __init__(self, name, hp, type, att, ult, ult1, ult2):
        self.image = f"images\\{name}"
        self.name = name
        self.standhp, self.hp = hp, hp
        self.type = type
        self.att = att
        self.ult = ult
        self.ult1 = ult1
        self.ult2 = ult2
        self.buff = []
    def get_image(self, prepiska=""):
        return self.image + prepiska + ".png"
    def typebaff(self, name):  # Возрашает список тегов эффектов
        types = {'armor': ["armor", "-damage"],
                 "healtime": ["dopheal"]}
        return types[name]

    def damage(self, dmg):  # Нанести урон этому персонажу
        if self.type == "melee":
            if random.randint(0, 4) > 2 and dmg > 0:
                dmg -= 1

        for i in self.buff:
            if "-damage" in self.typebaff(i[0]):
                dmg -= i[1]
        if dmg < 0:
            dmg = 0

        self.hp -= dmg

    def heal(self, heal):  # Лечение
        for i in self.buff:
            if "dopheal" in self.typebaff(i[0]):
                heal += i[1]

        self.hp += heal
        if self.hp > self.standhp:
            self.hp = self.standhp

    def get_att(self, att=0):  # Возращает нынешний урон обычной отакой
        att += self.att
        for i in self.buff:
            if "attake" in self.typebaff(i[0]):
                att += i[1]
        if att < 1:
            att = 0
        return att

    def get_super(self, mega=0):  # пока что не трогаем
        if mega:
            return 0
        else:
            supertype = {'armor': 1,
                         "healtime": 1,
                         "shotgun": 1}
            return supertype[self.ult]

    def stats(self):
        return [self.name, self.standhp, self.hp, self.get_att(), self.ult]


class Fight():
    def __init__(self, plrs, enems, map="Plain", mapdeffect=[]):
        connection = sqlite3.connect('DOTAS.db')
        cursor = connection.cursor()
        self.map = map
        self.mapdeffect = mapdeffect
        self.player1 = Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[0],)).fetchone())
        self.player2 = Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[1],)).fetchone())
        self.player3 = Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[2],)).fetchone())

        self.enemy1 = Hero(*cursor.execute('SELECT * FROM enemy WHERE Name=?', (enems[0],)).fetchone())
        self.enemy2 = Hero(*cursor.execute('SELECT * FROM enemy WHERE Name=?', (enems[1],)).fetchone())
        self.enemy3 = Hero(*cursor.execute('SELECT * FROM enemy WHERE Name=?', (enems[2],)).fetchone())
        connection.close()
        # "start" "plr#" "enem#", "Vplr" "Venem" "Vall", "end"
        self.phase = ["start", None]

    def get_map(self):
        # if chtoto == chemuto:
        #     return cthoto Если какой то навык, который может сменить фон, то нам сюда
        # else:
        return f"images\\{self.map}"

    def get_mapdeffecttype(self, name):  # Возрашает значения и тип дэффекта от карты
        types = {'PoisonForest': ["ALLDamage", 1],
                 "RadiantShild": ["PLRSHeal", 2],
                 "DireDefect": ["PLRSDamage", 2],
                 "DireShild": ["ENEMYESHeal", 1]}
        return types[name]

    def get_figurs(self):
        return [self.player1.name, self.player2.name, self.player3.name,
                self.enemy1.name, self.enemy2.name, self.enemy3.name]

    def get_players(self):
        return [self.player1.stats(), self.player2.stats(), self.player3.stats()]

    def get_enemyes(self):
        return [self.enemy1.stats(), self.enemy2.stats(), self.enemy3.stats()]

    def get_image(self):  # Список ссылок на картинки [Frendly1, 2, 3, Enemy1, 2, 3]
        return [self.player1.image, self.player2.image, self.player3.image,
                self.enemy1.image, self.enemy2.image, self.enemy3.image]


if __name__ == "__main__":
    players = ["Pudge1", "DrowRanger1", "Oracle1"]
    enemyes = ["Creap", "Creap", "Creap"]

    board = Fight(players, enemyes)
    print(board.get_players())
    print(board.get_image())
    gamecheck = True

