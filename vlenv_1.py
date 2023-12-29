import pygame
import random
import os
import sys
import sqlite3

WIDTH, HEIGHT = 1280, 960
HEROS = {(0, 2): 'DrowRanger', (1, 2): 'Oracle', (2, 2): 'Pudge',
         '': ''}  # Словарь с героями и их индексацией для self.select_char
EVENTS = {1: ['Вы попадаете на свой фонтан.',
              'Здесь вы можете восполнить',
              'свои ресурсы',
              '(описание работы эффекта)',
              '(я хз как он работать будет)'],
          2: ['Проходя по лесу вы замечаете',
              'стак крипов, вы можете',
              f'получить много золота или',
              'сделать еще один стак',
              '(это увеличит золото за',
              'это событие навсегда)']}


def load_image(name, pack, colorkey=None):
    fullname = os.path.join(pack, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Hero:
    def __init__(self, name, hp, type, att, ult, ult1, ult2):
        self.level = int(name[-1])
        self.name = name[:len(name) - 1]
        self.standhp, self.hp = hp, hp
        self.type = type
        self.att = att
        self.ult = ult
        self.ult1 = ult1
        self.ult2 = ult2
        self.buff = []

    def typebaff(self, name):  # Возрашает список тегов эффектов
        types = {'armor': ["armor", "-damage"],
                 "healtime": ["dopheal"]}
        return types[name]

    def damage(self, dmg, magic=False):  # Нанести урон этому персонажу
        if self.type == "melee" and not magic:
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

    def get_att(self, att=0):  # Возращает нынешний урон обычной атакой
        att += self.att
        for i in self.buff:
            if "attake" in self.typebaff(i[0]):
                att += i[1]
        if att < 1:
            att = 1
        return att

    def get_super(self, mega=0):  # пока что не трогаем
        if mega:
            return 0
        else:
            supertype = {'armor': 1,
                         "healtime": 1,
                         "shotgun": 1}
            return supertype[self.ult]

    def get_image(self, prepiska=""):  # Возращает картинку ( и нужную анимацию)
        return "images\\" + self.name + prepiska + ".png"

    def stats(self):
        return [self.name, self.standhp, self.hp, self.get_att(), self.ult, self.buff]

    def checktimesbaff(self):
        for i in self.buff:
            if i[1] <= 0:
                self.buff.remove(i)


class Fight():
    def __init__(self, plrs, enems, map="Background", mapdeffect=[]):
        connection = sqlite3.connect('DOTAS.db')
        cursor = connection.cursor()
        self.map = map
        self.mapdeffect = mapdeffect
        self.plrs = []
        for u in range(0, 3):
            if plrs[u] != None:
                self.plrs.append(Hero(*cursor.execute('SELECT * FROM heroes WHERE Name=?', (plrs[u],)).fetchone()))
            else:
                self.plrs.append(None)

        self.enems = []
        for u in range(0, 3):
            if enems[u] != None:
                self.enems.append(Hero(*cursor.execute('SELECT * FROM enemy WHERE Name=?', (enems[u],)).fetchone()))
            else:
                self.enems.append(None)
        connection.close()
        self.phase = "startgame"  # "startgame" = "startr" "endr" "plr" "enem", "Vplr" "Venem" "Vall", "endloop"
        self.whomove = 0  # 1-plr1 2-enem1 3-plr2 ...
        self.getplr = 0
        self.getenem = 0
        self.heroplay = 1
        self.point = []
        self.wait = 0
        self.getgold = 0
        self.whywait = None
        self.buttonattacke = False
        self.mana = 0
        self.end = False

    def clicked(self, who):
        if self.buttonattacke:
            if self.plrs[self.getplr - 1].name == "BountyHunter":
                self.getgold += 11
            self.enems[who].damage(self.plrs[self.getplr - 1].get_att())

            self.checkdie()
            self.loop()
        else:
            getattr(self, f'ult_{self.plrs[self.getplr - 1].ult}')(who)
            self.checkdie()
            self.loop()
        self.point = []

    def ult_armor(self, who):
        self.plrs[who].heal(3)
        self.plrs[who].buff.append(['armor', self.plrs[self.getplr - 1].ult1, 3])

    def ult_healtime(self, who):
        self.plrs[who].heal(2)
        self.plrs[who].buff.append(['healtime', self.plrs[self.getplr - 1].ult1, self.plrs[self.getplr - 1].ult2])

    def ult_shotgun(self, who):
        for i in range(3):
            self.enems[i].damage(self.plrs[self.getplr - 1].ult1)

    def get_map(self):
        # if chtoto == chemuto:
        #     return cthoto Если какой то навык, который может сменить фон, то нам сюда
        # else:
        return f"images\\{self.map}.png"

    def get_mapdeffecttype(self, name):  # Возрашает значения и тип дэффекта от карты
        types = {'PoisonForest': ["ALLDamage", 1],
                 "RadiantShild": ["PLRSHeal", 2],
                 "DireDefect": ["PLRSDamage", 2],
                 "DireShild": ["ENEMYESHeal", 1]}
        return types[name]

    def get_figurs(self):
        return [i.name for i in self.plrs if i != None], [i.name for i in self.enems if i != None]

    def get_players(self):  # Список аттрибутов союзников
        a = []
        for i in self.plrs:
            if i != None:
                a.append(i.stats())
        return a

    def get_enemyes(self):  # Список аттрибутов врагов
        a = []
        for i in self.enems:
            if i != None:
                a.append(i.stats())
        return a

    def get_images(self):  # Список ссылок на картинки [Frendly1, 2, 3] [Enemy1, 2, 3] - уже не нужно
        return [i.image for i in self.plrs if i != None], [i.image for i in self.enems if i != None]

    def checkdie(self):
        for i in range(3):
            if self.plrs[i] != None and self.plrs[i].hp <= 0:
                self.plrs[i] = None
            if self.enems[i] != None and self.enems[i].hp <= 0:
                self.enems[i] = None
                self.getgold += random.randint(28, 36)

    def draw(self):
        kash = self.getplr - 1
        self.point = []
        if (not self.buttonattacke and self.plrs[kash].ult in ['shotgun']) or self.buttonattacke:
            self.point.append(1)
            for i in range(3):
                if self.enems[i] != None:
                    kash1alpha = pygame.image.load("images\\retenemy.png").convert_alpha()
                    kash1surf = pygame.transform.scale(kash1alpha, (80, 80))
                    kash1rect = kash1surf.get_rect()
                    screen.blit(kash1surf,
                                (kash1rect.x + 670 + 200 * i, kash1rect.y + 620, kash1rect.width,
                                 kash1rect.height))
        if self.plrs[kash].ult in ['healtime'] and not self.buttonattacke:
            self.point.append(2)
            for i in range(3):
                if self.plrs[i] != None:
                    kash1alpha = pygame.image.load("images\\retplayer.png").convert_alpha()
                    kash1surf = pygame.transform.scale(kash1alpha, (80, 80))
                    kash1rect = kash1surf.get_rect()
                    screen.blit(kash1surf,
                                (kash1rect.x + 480 - 200 * i, kash1rect.y + 620, kash1rect.width, kash1rect.height))
        if self.plrs[kash].ult in ['armor'] and not self.buttonattacke:
            self.point.append(3)
            kash1alpha = pygame.image.load("images\\retplayer.png").convert_alpha()
            kash1surf = pygame.transform.scale(kash1alpha, (80, 80))
            kash1rect = kash1surf.get_rect()
            screen.blit(kash1surf,
                        (kash1rect.x + 480 - 200 * kash - 1, kash1rect.y + 620, kash1rect.width, kash1rect.height))

    def update(self):
        if self.phase == "startgame":
            for i in range(3):
                if self.plrs[i] != None:
                    self.phase = "startr"
                    self.whomove = 1 + i * 2
                    break
                elif self.enems[i] != None:
                    self.phase = "startr"
                    self.whomove = 2 + i * 2
                    break
            else:
                self.phase = "endloop"

        elif self.phase == "startr":
            if self.whomove % 2 == 1:
                self.getplr = 1 + self.whomove // 2
                for i in self.plrs[self.getplr - 1].buff:
                    if i[0] in ["Poison"]:
                        self.plrs[self.getplr - 1].damage(i[2], i[3])
                self.plrs[self.getplr - 1].checktimesbaff()
                self.checkdie()
                self.loop()
                self.buttonattacke = True
                self.phase = "plr"
            else:
                self.getenem = 1 + self.whomove // 2
                for i in self.enems[self.getenem].buff:
                    if i[0] in ["Poison"]:
                        self.enems[self.getenem].damage(i[2], i[3])
                self.enems[self.getenem].checktimesbaff()
                self.checkdie()
                self.loop()
                self.phase = "enem"
        elif self.phase == "plr":
            kash1alpha = pygame.image.load("images\\who.png").convert_alpha()
            kash1surf = pygame.transform.scale(kash1alpha, (40, 40))
            kash1rect = kash1surf.get_rect()
            screen.blit(kash1surf,
                        (kash1rect.x + 670 - 200 * self.getplr, kash1rect.y + 470, kash1rect.width, kash1rect.height))
            self.draw()
        elif self.phase == "enem":
            enemy = self.enems[self.getenem - 1]
            flag = True
            if enemy.level == 1:
                if random.randint(1, 100) >= 83:
                    for i in self.plrs:
                        for j in i.buff:
                            if j[0] in ["Arena"]:
                                i.damage(enemy.get_att() * 2, i.type)
                                flag = True
                                break
                        if flag:
                            break
                    if flag:
                        kash = random.randint(0, 2)
                        self.plrs[kash].damage(enemy.get_att() * 2)
                else:
                    for i in self.plrs:
                        for j in i.buff:
                            if j[0] in ["Arena"]:
                                i.damage(enemy.get_att(), i.type)
                                flag = False
                                break
                        if flag:
                            break
                    if flag:
                        kash = random.randint(0, 2)
                        self.plrs[kash].damage(enemy.get_att())
            self.loop()
        elif self.phase == "end":
            for i in self.mapdeffect:
                kash = self.get_mapdeffecttype(i)
                if "PLRSHeal" in kash:
                    for j in self.plrs:
                        j.heal(kash[1])
                if "PLRSDamage" in kash:
                    for j in self.plrs:
                        j.damage(kash[1], True)
                if "ENEMYESHeal" in kash:
                    for j in self.enems:
                        j.heal(kash[1])
                if "ALLDamage" in kash:
                    for j in self.plrs:
                        j.damage(kash[1], True)
                    for j in self.enems:
                        j.damage(kash[1], True)
            self.phase = "startgame"

    def loop(self):
        if self.phase == 'plr':
            if self.enems[self.getplr - 1] != None:
                self.phase = 'enem'
                self.getenem = self.getplr
            else:
                for i in range(self.getplr, 3):
                    if self.plrs[i] != None:
                        self.phase = "startr"
                        self.whomove = 1 + i * 2
                        break
                    elif self.enems[i] != None:
                        self.phase = "startr"
                        self.whomove = 2 + i * 2
                        break
                else:
                    self.phase = "end"
        elif self.phase == "enem":
            if self.getenem != 3 and self.plrs[self.getenem - 1] != None:
                self.phase = 'plr'
                self.getplr = self.getenem + 1
            elif self.getenem == 3:
                self.phase = 'end'
            else:
                for i in range(self.getplr - 1, 3):
                    if self.plrs[i] != None:
                        self.phase = "plr"
                        self.whomove = 1 + i * 2
                        break
                    elif self.enems[i] != None:
                        self.phase = "enem"
                        self.whomove = 2 + i * 2
                        break
                else:
                    self.phase = "end"


class Dota:
    def __init__(self):
        self.bufs = []  # Список бафов (хз че ты с ним делать будешь))))
        self.map = []
        self.map_prev = 2
        self.map_title = 2
        self.map_titles = ['fight', 'fight']
        self.map.append(self.map_titles)
        for i in range(9):  # Что-то типо гениратора карты
            while self.map_title == self.map_prev:
                self.map_title = random.randint(2, 3)
            self.map_prev = self.map_title
            self.map_titles = []
            for j in range(self.map_title):
                self.map_titles.append(
                    random.choice(('fight', 'fight', 'fight', 'fight', 'fight', 'fight', 'event', 'event', 'elite')))
            self.map.append(self.map_titles)
        self.room = [0, 0]
        self.save = 1  # Сохранение (1 окно)
        self.files()
        self.select = 1  # Выбранный слот отряда (2 окно)
        self.screen = 1  # Номер экрана (для active_screen())
        self.running = True
        self.select_char = ['', '', '']  # Отряд
        self.connection = sqlite3.connect('DOTAS.db')  # Создание списка из всех героев и их статов
        self.cursor = self.connection.cursor()  # По типу [[('DrowRanger2', 24, 'range', 11, 'shotgun', 4, None)], [('Oracle3', 26, 'range', 6, 'healtime', 2, 4)], [('Pudge3', 38, 'melee', 9, 'armor', 5, None)]]
        self.hero_list = self.cursor.execute('SELECT * FROM heroes_pick').fetchall()
        self.stat_list = []
        for i in range(len(self.hero_list)):
            self.stat_list.append(self.cursor.execute(
                f'SELECT * FROM heroes WHERE Name="{self.hero_list[i][0] + str(self.lvls[i])}" ').fetchall())
        self.connection.close()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.screen == 1:  # Отдельные функции для разных экранов
                    if event.type == pygame.MOUSEBUTTONUP:
                        if 980 > event.pos[0] > 300 and 550 < event.pos[1] < 650:  # Кнопка играть
                            self.screen = 2

                        elif 220 < event.pos[0] < 460 and 700 < event.pos[1] < 750:  # Смена сохранений
                            self.save = 1
                        elif 520 < event.pos[0] < 760 and 700 < event.pos[1] < 750:
                            self.save = 2
                        elif 820 < event.pos[0] < 1060 and 700 < event.pos[1] < 750:
                            self.save = 3
                        self.files()
                        self.connection = sqlite3.connect('DOTAS.db')
                        self.cursor = self.connection.cursor()
                        self.hero_list = self.cursor.execute('SELECT * FROM heroes_pick').fetchall()
                        self.stat_list = []
                        for i in range(len(self.hero_list)):
                            self.stat_list.append(self.cursor.execute(
                                f'SELECT * FROM heroes WHERE Name="{self.hero_list[i][0] + str(self.lvls[i])}" ').fetchall())
                        self.connection.close()

                elif self.screen == 2:
                    if event.type == pygame.MOUSEBUTTONUP:
                        if 800 < event.pos[0] < 1050 and 180 < event.pos[1] < 260:  # Выбор слота отряда
                            self.select = 1
                        elif 800 < event.pos[0] < 1050 and 280 < event.pos[1] < 360:
                            self.select = 2
                        elif 800 < event.pos[0] < 1050 and 380 < event.pos[1] < 460:
                            self.select = 3

                        elif 700 < event.pos[0] < 1060 and 650 < event.pos[1] < 750:  # Кнопка играть
                            if '' not in self.select_char:
                                self.screen = 3
                                for i in range(
                                        len(self.select_char)):  # Превращение self.select_char из списка индексов героев в список из 3 героев с уровнями по типу ['Pudge2', 'Drow ranger3', 'Oracle3']
                                    self.select_char[i] = HEROS[self.select_char[i]] + str(self.lvls[i])

                        elif 460 < event.pos[0] < 610 and 600 < event.pos[1] < 675:  # Улучшение
                            if int(self.gold) >= 100:
                                self.lvl_up(self.select_char[self.select - 1])

                        else:  # Составление отряда
                            for i in range(len(self.hero_list)):
                                if 220 + i * 80 - i // 3 * 240 < event.pos[0] < 220 + i * 80 - i // 3 * 240 + 70 \
                                        and 180 + i // 3 * 80 < event.pos[1] < 180 + i // 3 * 80 + 70:
                                    if (i, j) not in self.select_char:
                                        self.select_char[self.select - 1] = (i, j)

                elif self.screen == 3:
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.room[0] == 10:  # Кнопки передвижения на карте (прикольна)
                            if 960 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.screen = 5
                        elif self.room[0] % 2 == 1 or (self.room[1] == 2 and self.room[0] % 2 == 0) or self.room[
                            0] == 0:
                            if 960 < event.pos[0] < 1100 and 800 < event.pos[1] < 850:
                                if self.room[1] == 0:
                                    self.room[1] = 1
                                elif self.room[1] == 2 and self.room[0] % 2 == 0:
                                    self.room[1] -= 1
                                self.room[0] += 1
                                self.movement()
                            elif 1120 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                if self.room[1] == 0:
                                    self.room[1] = 2
                                elif self.room[0] % 2 == 1:
                                    self.room[1] += 1
                                self.room[0] += 1
                                self.movement()
                        elif self.room[1] == 1:
                            if 960 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.movement()
                                self.room[0] += 1
                        else:
                            if 960 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.room[0] += 1
                                self.room[1] -= 1
                                self.movement()
                        if self.room[0] != 10:
                            # Смена экрана на бои/события/элиток.
                            self.active_title(self.map[self.room[0] - 1][self.room[1] - 1])

                elif self.screen == 4:
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if 1 in self.board.point:
                            for i in range(3):
                                if 600 + 200 * i < event.pos[0] < 780 + 200 * i and 500 < event.pos[
                                    1] < 780 and self.board.enems[i] != None:
                                    self.board.clicked(i)
                                    break
                        if 2 in self.board.point:
                            for i in range(3):
                                if 400 - 200 * i < event.pos[0] < 580 - 200 * i and 500 < event.pos[
                                    1] < 780 and self.board.plrs[i] != None:
                                    self.board.clicked(i)
                                    break
                        if 3 in self.board.point:
                            for i in range(3):
                                if 400 - 200 * i < event.pos[0] < 580 - 200 * i and 500 < event.pos[
                                    1] < 780 and self.board.plrs[i] != None and i == self.board.getplr - 1:
                                    self.board.clicked(i)
                                    break

                        if 1000 < event.pos[0] < 1170 and 780 < event.pos[
                            1] < 930 and self.board.enems[i] != None:
                            self.board.buttonattacke = False

                        if 800 < event.pos[0] < 970 and 780 < event.pos[
                            1] < 930 and self.board.enems[i] != None:
                            self.board.buttonattacke = True
                    if event.type == pygame.KEYUP:
                        if event.key == 32:
                            self.board.buttonattacke = True
                        elif event.key == 101:
                            self.board.buttonattacke = False

                elif self.screen == 5:
                    pass

                elif self.screen == 'e':  # Кнопки на событиях
                    if event.type == pygame.MOUSEBUTTONUP:
                        if 850 < event.pos[0] < 1030 and 800 < event.pos[1] < 850:
                            self.event_res(4)
                            self.screen = 3
                        elif 1050 < event.pos[0] < 1230 and  800 < event.pos[1] < 850:
                            self.event_res(5)
                            self.screen = 3

            self.active_screen()
            pygame.display.flip()
        pygame.quit()

    def movement(self):
        if self.map[self.room[0] - 1][self.room[1] - 1] == 'fight':
            kash = random.choices(['GhostCreap1', 'Wood1', 'Creep1', 'Creep1'], k=3)
            self.board = Fight(self.select_char, kash)
            self.screen = 4

    def active_title(self, title):  # Экраны комнат
        if title == 'fight':
            self.screen = 4
        elif title == 'event':
            self.screen = 7
        elif title == 'elite':
            self.screen = 8

    def active_screen(self):  # Функция для выбора отрисовываемого окна
        screen.fill((0, 0, 0))
        if self.screen == 1:
            self.main_screen()
        elif self.screen == 2:
            self.pick_screen()
        elif self.screen == 3:
            self.map_screen()
        elif self.screen == 4:
            self.fight_screen()
        elif self.screen == 5:
            self.boss_screen()
        elif self.screen == 6:
            self.fight_screen()
        elif self.screen == 7:
            self.event_pick()
        elif self.screen == 8:
            self.elite_screen()
        elif self.screen[0] == 'e':
            self.event_screen()

    def main_screen(self):  # Меню
        fon = pygame.transform.scale(load_image('dota.jpg', 'data'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        pygame.draw.rect(screen, (235, 122, 52), (140, 500, 1000, 400))
        pygame.draw.rect(screen, (135, 135, 161), (300, 550, 680, 100))
        pygame.draw.rect(screen, (65, 147, 191), (300, 550, 680, 100), 5)
        pygame.draw.rect(screen, (135, 135, 161), (220, 700, 240, 50))
        pygame.draw.rect(screen, (135, 135, 161), (520, 700, 240, 50))
        pygame.draw.rect(screen, (135, 135, 161), (820, 700, 240, 50))

        if self.save == 1:  # Обводка выбранного сохранения
            pygame.draw.rect(screen, (86, 209, 145), (220, 700, 240, 50), 5)
        elif self.save == 2:
            pygame.draw.rect(screen, (86, 209, 145), (520, 700, 240, 50), 5)
        else:
            pygame.draw.rect(screen, (86, 209, 145), (820, 700, 240, 50), 5)

        self.print_text(100, 'Играть', (82, 65, 191), (530, 570))  # Текст на кнопках
        self.print_text(50, 'Сохранение 1', (82, 65, 191), (223, 710))
        self.print_text(50, 'Сохранение 2', (82, 65, 191), (523, 710))
        self.print_text(50, 'Сохранение 3', (82, 65, 191), (823, 710))

    def pick_screen(self):  # Экран составления отряда
        pygame.draw.rect(screen, (135, 135, 161), (200, 100, 880, 700))
        pygame.draw.rect(screen, (86, 104, 209), (460, 180, 330, 390))
        pygame.draw.rect(screen, (86, 104, 209), (220, 600, 230, 180))

        for i in range(len(self.hero_list)):  # Отрисовка сетки персонажей
            pygame.draw.rect(screen, (86, 104, 209), (220 + i * 80 - i // 3 * 240, 180 + i // 3 * 80, 70, 70))

        for i in range(len(self.hero_list)):
            self.img = load_image(self.hero_list[i][0] + '.png', 'pick_images')
            self.img = pygame.transform.scale(self.img, (70, 70))
            screen.blit(self.img, (220 + i * 80 - i // 3 * 240, 180 + i // 3 * 80, 70, 70))

        for i in range(3):  # Отрисовка слотов отряда
            pygame.draw.rect(screen, (86, 104, 209), (800, 180 + 100 * i, 250, 80))

        if self.select == 1:  # Обводка выделенного слота в отряде
            pygame.draw.rect(screen, (86, 209, 145), (800, 180, 250, 80), 5)
        elif self.select == 2:
            pygame.draw.rect(screen, (86, 209, 145), (800, 280, 250, 80), 5)
        else:
            pygame.draw.rect(screen, (86, 209, 145), (800, 380, 250, 80), 5)

        if self.select_char != ['', '', '']:  # Обводка выбаных персонажей
            for i in range(5):
                for j in range(3):
                    for ij in self.select_char:
                        if ij != '':
                            if i == ij[0] and j == ij[1]:
                                pygame.draw.rect(screen, 'red',
                                                 (220 + i * 80 - i // 3 * 240, 180 + i // 3 * 80, 70, 70), 5)

        self.print_text(50, str(HEROS[self.select_char[0]]), 'red', (830, 200))  # Отображение названий персонажей
        self.print_text(50, str(HEROS[self.select_char[1]]), 'red', (830, 300))
        self.print_text(50, str(HEROS[self.select_char[2]]), 'red', (830, 400))

        self.print_text(50, 'Персонажи', (82, 65, 191), (240, 130))  # Надписи сверху
        self.print_text(50, 'Описание', (82, 65, 191), (540, 130))
        self.print_text(50, 'Отряд', (82, 65, 191), (870, 130))

        self.print_text(50, 'Золото', 'yellow', (270, 620))  # Деньги???
        self.print_text(30, str(self.gold), 'yellow', (250, 670))

        if self.select_char[self.select - 1] != '':  # Текст описания + прокачка
            self.print_text(50, f'{HEROS[self.select_char[self.select - 1]]}', (82, 65, 191), (500, 200))
            self.print_text(40, 'Атака:', 'red', (480, 250))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1][0]][0][3]), 'red', (670, 250))
            self.print_text(40, 'Навык:', 'blue', (480, 290))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1][0]][0][4]), 'blue', (670, 290))
            self.print_text(40, 'HP:', 'green', (480, 330))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1][0]][0][1]), 'green', (670, 330))
            self.print_text(40, 'Уровень:', (0, 49, 163), (480, 370))
            self.print_text(40, str(self.lvls[self.select_char[self.select - 1][0]]), (0, 49, 163), (670, 370))
            self.print_text(40, 'Тип атаки:', 'yellow', (480, 410))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1][0]][0][2]), 'yellow', (670, 410))

            self.print_text(40, 'Улучшение:', 'yellow', (250, 700))
            self.print_text(30, f'{str(self.gold)} / 100', 'yellow', (250, 740))
            if int(self.gold) >= 100:
                pygame.draw.rect(screen, 'green', (460, 600, 150, 75))
            else:
                pygame.draw.rect(screen, 'red', (460, 600, 150, 75))
            self.print_text(40, 'Улучшить', (82, 65, 191), (470, 625))

        if '' not in self.select_char:  # Кнопка играть
            pygame.draw.rect(screen, (186, 78, 52), (700, 650, 360, 100))
            self.print_text(60, 'Играть', (82, 65, 191), (800, 680))

    def map_screen(self):  # Окно карты
        pygame.draw.rect(screen, (158, 154, 122), (100, 50, 800, 850))
        pygame.draw.rect(screen, (86, 104, 209), (930, 0, 360, 1000))
        for i in range(9):  # Линии между комнатами (ужас)
            for j in range(2):
                if i % 2 == 0:
                    pygame.draw.line(screen, 'black', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65),
                                     (600 - 75 * len(self.map[i]) + 150 * j - 75, 850 - i * 65 - 65), 5)
                    pygame.draw.line(screen, 'black', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65),
                                     (600 - 75 * len(self.map[i]) + 150 * j + 75, 850 - i * 65 - 65), 5)
                else:
                    pygame.draw.line(screen, 'black', (600 - 75 * len(self.map[i]) + 150 * j + 150, 850 - i * 65),
                                     (600 - 75 * len(self.map[i]) + 150 * j + 75, 850 - i * 65 - 65), 5)
                    pygame.draw.line(screen, 'black', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65),
                                     (600 - 75 * len(self.map[i]) + 150 * j + 75, 850 - i * 65 - 65), 5)
        for i in range(3):
            if i != 1:
                pygame.draw.line(screen, 'black', (600 - 225 + 150 * i, 265), (525, 150), 5)
            else:
                pygame.draw.line(screen, 'black', (600 - 225 + 150 * i, 265), (525, 150), 4)
        pygame.draw.line(screen, 'black', (450, 850), (525, 885), 5)
        pygame.draw.line(screen, 'black', (600, 850), (525, 885), 5)

        if self.room == [0, 0]:  # Положение игрока на карте
            pygame.draw.circle(screen, 'yellow', (525, 885), 20)
        else:
            for i in range(10):
                for j in range(len(self.map[i])):
                    if i == self.room[0] - 1:
                        if j == self.room[1] - 1:
                            pygame.draw.circle(screen, 'yellow', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65),
                                               20)
        pygame.draw.circle(screen, 'black', (525, 885), 15)

        pygame.draw.circle(screen, 'red', (525, 150), 50)
        for i in range(10):
            for j in range(len(self.map[i])):  # Прорисовка карты
                if self.map[i][j] == 'fight':
                    pygame.draw.circle(screen, 'grey', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65), 15)
                elif self.map[i][j] == 'event':
                    pygame.draw.circle(screen, 'green', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65), 15)
                elif self.map[i][j] == 'elite':
                    pygame.draw.circle(screen, 'red', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65), 15)

        pygame.draw.circle(screen, 'red', (950, 50), 15)  # Подсказки справа
        pygame.draw.circle(screen, 'green', (950, 100), 15)
        pygame.draw.circle(screen, 'grey', (950, 150), 15)
        self.print_text(35, '- элитный враг', 'red', (980, 37))
        self.print_text(35, '- случайное событие', 'green', (980, 87))
        self.print_text(35, '- обычный враг', 'grey', (980, 137))

        # Кнопки для перемещения яуауаяууф
        if self.room[0] == 10:
            pygame.draw.rect(screen, 'blue', (960, 800, 300, 50))
            self.print_text(40, 'БОСС', 'red', (1060, 815))
        elif self.room[0] % 2 == 1 or (self.room[1] == 2 and self.room[0] % 2 == 0) or self.room[0] == 0:
            pygame.draw.rect(screen, 'blue', (960, 800, 140, 50))
            pygame.draw.rect(screen, 'blue', (1120, 800, 140, 50))
            self.print_text(35, '< Налево', 'green', (980, 815))
            self.print_text(35, 'Направо >', 'green', (1130, 815))
        elif self.room[1] == 1:
            pygame.draw.rect(screen, 'blue', (960, 800, 300, 50))
            self.print_text(35, 'Направо >', 'green', (1040, 815))
        else:
            pygame.draw.rect(screen, 'blue', (960, 800, 300, 50))
            self.print_text(35, '< Налево', 'green', (1040, 815))

    def fight_screen(self):  # Окно боя
        if self.board.plrs != [None, None, None] and self.board.enems != [None, None, None]:
            print(self.board.get_players())
            pygame.draw.rect(screen, (255, 255, 255), (0, 0, 800, 850))
            backG_Image = pygame.image.load(self.board.get_map())
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, backG_rect)
            if self.board.phase == 'plr':
                if self.board.buttonattacke:
                    buttonAtt = pygame.image.load("images\\AttackeButton1.png").convert_alpha()
                    buttonAttsurf = pygame.transform.scale(buttonAtt, (164, 120))
                    buttonAttrect = buttonAttsurf.get_rect()
                    screen.blit(buttonAttsurf, (buttonAttrect.x + 800, buttonAttrect.y + 780, buttonAttrect.width,
                                                buttonAttrect.height))
                    buttonAtt = pygame.image.load("images\\UltButton0.png").convert_alpha()
                    buttonAttsurf = pygame.transform.scale(buttonAtt, (164, 120))
                    buttonAttrect = buttonAttsurf.get_rect()
                    screen.blit(buttonAttsurf, (buttonAttrect.x + 1000, buttonAttrect.y + 780, buttonAttrect.width,
                                                buttonAttrect.height))
                else:
                    buttonAtt = pygame.image.load("images\\AttackeButton0.png").convert_alpha()
                    buttonAttsurf = pygame.transform.scale(buttonAtt, (164, 120))
                    buttonAttrect = buttonAttsurf.get_rect()
                    screen.blit(buttonAttsurf, (buttonAttrect.x + 800, buttonAttrect.y + 780, buttonAttrect.width,
                                                buttonAttrect.height))
                    buttonAtt = pygame.image.load("images\\UltButton1.png").convert_alpha()
                    buttonAttsurf = pygame.transform.scale(buttonAtt, (164, 120))
                    buttonAttrect = buttonAttsurf.get_rect()
                    screen.blit(buttonAttsurf, (buttonAttrect.x + 1000, buttonAttrect.y + 780, buttonAttrect.width,
                                                buttonAttrect.height))

            self.board.checkdie()
            for i in range(3):
                if self.board.plrs[i] != None:
                    kash1alpha = pygame.image.load(self.board.plrs[i].get_image()).convert_alpha()
                    kash1surf = pygame.transform.scale(kash1alpha, (180, 260))
                    kash1rect = kash1surf.get_rect()
                    screen.blit(kash1surf,
                                (kash1rect.x + 400 - 200 * i, kash1rect.y + 500, kash1rect.width, kash1rect.height))
                    pygame.draw.rect(screen, (128, 128, 128), [430 - 200 * i, 470, 120, 20])
                    pygame.draw.rect(screen, (127, 235, 77), [432 - 200 * i, 473,
                                                              116 * self.board.plrs[i].hp / self.board.plrs[i].standhp,
                                                              15])
            for i in range(3):
                if self.board.enems[i] != None:
                    kash1alpha = pygame.image.load(self.board.enems[i].get_image()).convert_alpha()
                    kash1surf = pygame.transform.scale(kash1alpha, (180, 260))
                    kash1rect = kash1surf.get_rect()
                    screen.blit(kash1surf, (kash1rect.x + 600 + 200 * i, kash1rect.y + 500, kash1rect.width - 50,
                                            kash1rect.height - 50))
                    pygame.draw.rect(screen, (128, 128, 128), [600 + 200 * i, 470, 120, 20])
                    pygame.draw.rect(screen, (255, 97, 97), [602 + 200 * i, 473,
                                                             116 * self.board.enems[i].hp / self.board.enems[i].standhp,
                                                             15])
            self.board.update()
        elif self.board.enems == [None, None, None]:
            print('END')
            #if self.map[self.room[0] - 1][self.room[1] - 1] == 'fight':
            self.gold_add(self.board.getgold)
            self.screen = 3

    def boss_screen(self):
        pass

    def event_pick(self):
        self.connection = sqlite3.connect('DOTAS.db')
        self.cursor = self.connection.cursor()
        self.event_list = self.cursor.execute('SELECT * FROM events').fetchall()
        self.connection.close()
        self.event = random.choice(self.event_list)
        self.screen = 'e'

    def event_screen(self):
        pygame.draw.rect(screen, (135, 135, 161), (800, 0, 500, 1000))
        pygame.draw.rect(screen, self.event[8], (850, 800, 180, 50))
        pygame.draw.rect(screen, self.event[9], (1050, 800, 180, 50))
        self.print_text(70, self.event[1], 'red', (900, 100))
        self.print_text(30, self.event[2], self.event[8], (830, 750))
        self.print_text(30, self.event[3], self.event[9], (1050, 750))
        self.print_event(40, EVENTS[self.event[0]], self.event[8], (850, 200))

    def event_res(self, res):
        if self.event[res] == 'buff_add':
            self.bufs.append(self.event[res + 2])
        elif self.event[res] == 'gold_add':
            self.gold_add(int(self.event[res + 2]))
        elif self.event[res] == 'file_edit':
            self.connection = sqlite3.connect('DOTAS.db')
            self.cursor = self.connection.cursor()
            self.cursor.execute(f'UPDATE events SET effect1 = {str(int(self.event[6]) + int(self.event[7]))} WHERE id = {self.event[0]}')
            self.cursor.execute(f'UPDATE events SET var1text = "Получить золото ({str(int(self.event[6]) + int(self.event[7]))})" WHERE id = {self.event[0]}')
            self.connection.commit()
            self.connection.close()

    def elite_screen(self):
        pass

    def gold_add(self, goldadd):  # Изменение денег
        gold_file = open(f'gold//gold{self.save}.txt', mode='w', encoding='utf-8')
        gold_file.write(str(int(self.gold) + goldadd))
        gold_file.close()
        self.gold = str(int(self.gold) + goldadd)

    def lvl_up(self, char):  # Изменение уровня
        self.lvl_file = open(f'lvl//lvl{self.save}.txt', mode='w', encoding='utf-8')
        if self.lvls[char[0]] + 1 != 4:
            self.lvls[char[0]] += 1
            self.gold_add(-100)
        for i in self.lvls:
            self.lvl_file.write(str(i))
        self.lvl_file.close()
        self.connection = sqlite3.connect('DOTAS.db')
        self.cursor = self.connection.cursor()
        self.hero_list = self.cursor.execute('SELECT * FROM heroes_pick').fetchall()
        self.stat_list = []
        for i in range(len(self.hero_list)):
            self.stat_list.append(self.cursor.execute(
                f'SELECT * FROM heroes WHERE Name="{self.hero_list[i][0] + str(self.lvls[i])}" ').fetchall())
        self.connection.close()

    def files(self):  # Файлы
        try:  # txt (деньги и уровень)
            self.gold = open(f'gold//gold{self.save}.txt', mode='r', encoding='utf-8').read()
            self.lvl = open(f'lvl//lvl{self.save}.txt', mode='r', encoding='utf-8').read()
        except Exception:
            print('Файлы не найдены')
            self.lvl = '111'
            self.gold = '10'
        self.lvls = []
        for i in range(3):
            self.lvls.append(int(self.lvl[i]))

    def print_text(self, size, toprint, col, rect):
        font = pygame.font.SysFont('sistem', size)
        text = font.render(toprint, True, col)
        screen.blit(text, rect)

    def print_event(self, size, toprint, col, rect):
        font = pygame.font.SysFont('sistem', size)
        self.rect = rect
        for i in toprint:
            text = font.render(i, True, col)
            screen.blit(text, self.rect)
            self.rect = (rect[0], self.rect[1] + size)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Dota 3')
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    Dota()
