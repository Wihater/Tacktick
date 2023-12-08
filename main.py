import sys
import os
import pygame
import sqlite3
import random

class Hero:
    def __init__(self, name, hp, type, att, ult, ult1, ult2):
        self.image = f"images\\{name}"
        self.standhp, self.hp = hp, hp
        self.type = type
        self.standatt, self.att = att, att
        self.ult = ult
        self.ult1 = ult1
        self.ult2 = ult2
        self.buff = []

    def typebaff(self, name):
        types = {'armor':["armor", "-damage"]}
        return types[name]

    def demage(self, dmg):
        if self.type == "melee":
            if random.randint(0, 4) > 2 and dmg > 0:
                dmg -= 1

        for i in self.buff:
            if "-damage" in self.typebaff(i[0]):
                dmg -= i[1]
        if dmg < 0:
            dmg = 0

        self.hp -= dmg

    def heal(self, heal):
        for i in self.buff:
            if "dopheal" in self.typebaff(i[0]):
                heal += i[1]

        self.hp += heal
        if self.hp > self.standhp:
            self.hp = self.standhp


class Fight():
    def __init__(self, plrs, enem):
        connection = sqlite3.connect('DOTAS.db')
        cursor = connection.cursor()
        player1 = Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[0],)).fetchone())
        player2 = Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[1],)).fetchone())
        player3 = Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[2],)).fetchone())

        enemy1 = Hero(*cursor.execute('SELECT * FROM enemys WHERE Name=?', (enem[0],)).fetchone())
        enemy2 = Hero(*cursor.execute('SELECT * FROM enemys WHERE Name=?', (enem[1],)).fetchone())
        enemy3 = Hero(*cursor.execute('SELECT * FROM enemys WHERE Name=?', (enem[2],)).fetchone())
        connection.close()





