import pygame
import random
import sqlite3


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
        self.frame = 60
        self.clock = pygame.time.Clock()
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

                        elif 460 < event.pos[0] < 610 and 600 < event.pos[1] < 675:  # Улучшение
                            if int(self.gold) >= 100:
                                self.lvl_up(self.select_char[self.select - 1])

                        else:  # Составление отряда
                            for i in range(5):
                                for j in range(3):
                                    if 220 + j * 80 < event.pos[0] < 220 + j * 80 + 70 \
                                            and 180 + i * 80 < event.pos[1] < 180 + i * 80 + 70:
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
                            elif 1120 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.screen = 4
                                self.board = Fight(["Pudge1", "DrowRanger1", "Oracle1"],
                                                   ['GhostCreap1', 'Creep1', 'Creep1'], "Background")
                                if self.room[1] == 0:
                                    self.room[1] = 2
                                elif self.room[0] % 2 == 1:
                                    self.room[1] += 1
                                self.room[0] += 1
                        elif self.room[1] == 1:
                            if 960 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.room[0] += 1
                        else:
                            if 960 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.room[0] += 1
                                self.room[1] -= 1
                        if self.room[0] != 10:
                            pass  # Смена экрана на бои/события/элиток. Если убрать комент то все будет плоха)))
                            # self.active_title(self.map[self.room[0] - 1][self.room[1] - 1])

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

                elif self.screen == 5:
                    pass

            self.active_screen()
            pygame.display.flip()
        pygame.quit()

    def active_title(self, title):  # Экраны комнат
        if title == 'fight':
            self.screen = 6
        elif title == 'event':
            self.screen = 7
        elif title == 'elite':
            self.screen = 7

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
            self.event_screen()
        elif self.screen == 8:
            self.elite_screen()

    def main_screen(self):  # Меню
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

        font = pygame.font.SysFont('sistem', 100)  # Текст на кнопках
        text = font.render('Играть', True, (82, 65, 191))
        screen.blit(text, (530, 570))
        font = pygame.font.SysFont('sistem', 50)
        text = font.render('Сохранение 1', True, (82, 65, 191))
        screen.blit(text, (223, 710))
        text = font.render('Сохранение 2', True, (82, 65, 191))
        screen.blit(text, (523, 710))
        text = font.render('Сохранение 3', True, (82, 65, 191))
        screen.blit(text, (823, 710))

    def pick_screen(self):  # Экран составления отряда
        pygame.draw.rect(screen, (135, 135, 161), (200, 100, 880, 700))
        pygame.draw.rect(screen, (86, 104, 209), (460, 180, 330, 390))
        pygame.draw.rect(screen, (52, 229, 235), (480, 400, 290, 150))
        pygame.draw.rect(screen, (86, 104, 209), (220, 600, 230, 180))
        for i in range(5):  # Отрисовка сетки персонажей
            for j in range(3):
                pygame.draw.rect(screen, (86, 104, 209), (220 + j * 80, 180 + i * 80, 70, 70))

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
                                pygame.draw.rect(screen, 'red', (220 + j * 80, 180 + i * 80, 70, 70), 5)

        font = pygame.font.SysFont('sistem', 50)
        text = font.render(str(self.select_char[0]), True, (82, 65, 191))  # Отображение индексов персонажей
        screen.blit(text, (870, 200))
        text = font.render(str(self.select_char[1]), True, (82, 65, 191))
        screen.blit(text, (870, 300))
        text = font.render(str(self.select_char[2]), True, (82, 65, 191))
        screen.blit(text, (870, 400))

        text = font.render('Персонажи', True, (82, 65, 191))  # Надписи сверху
        screen.blit(text, (240, 130))
        text = font.render('Описание', True, (82, 65, 191))
        screen.blit(text, (540, 130))
        text = font.render('Отряд', True, (82, 65, 191))
        screen.blit(text, (870, 130))

        text = font.render('Золото', True, 'yellow')  # Деньги???
        screen.blit(text, (270, 620))
        font = pygame.font.SysFont('sistem', 30)
        text = font.render(str(self.gold), True, 'yellow')
        screen.blit(text, (250, 670))

        if self.select_char[self.select - 1] != '':  # Текст описания + прокачка
            font = pygame.font.SysFont('sistem', 50)
            text = font.render(f'Персонаж {self.select_char[self.select - 1]}', True, (82, 65, 191))
            screen.blit(text, (500, 200))
            font = pygame.font.SysFont('sistem', 40)
            text = font.render('Атака:', True, 'red')
            screen.blit(text, (480, 250))
            text = font.render('Защита:', True, 'blue')
            screen.blit(text, (480, 290))
            text = font.render('HP:', True, 'green')
            screen.blit(text, (480, 330))
            text = font.render('Уровень:', True, (0, 49, 163))
            screen.blit(text, (480, 370))
            text = font.render(
                str(self.lvls[self.select_char[self.select - 1][1]][self.select_char[self.select - 1][0]]), True,
                (0, 49, 163))
            screen.blit(text, (750, 370))
            text = font.render('история/роль:', True, 'red')
            screen.blit(text, (480, 410))

            font = pygame.font.SysFont('sistem', 40)
            text = font.render('Улучшение:', True, 'yellow')
            screen.blit(text, (250, 700))
            font = pygame.font.SysFont('sistem', 30)
            text = font.render(f'{str(self.gold)} / 100', True, 'yellow')
            screen.blit(text, (250, 740))
            if int(self.gold) >= 100:
                font = pygame.font.SysFont('sistem', 40)
                pygame.draw.rect(screen, 'green', (460, 600, 150, 75))
                text = font.render('Улучшить', True, (82, 65, 191))
                screen.blit(text, (470, 625))
            else:
                font = pygame.font.SysFont('sistem', 40)
                pygame.draw.rect(screen, 'red', (460, 600, 150, 75))
                text = font.render('Улучшить', True, (82, 65, 191))
                screen.blit(text, (470, 625))

        if '' not in self.select_char:  # Кнопка играть
            pygame.draw.rect(screen, (186, 78, 52), (700, 650, 360, 100))
            font = pygame.font.SysFont('sistem', 60)
            text = font.render('Играть', True, (82, 65, 191))
            screen.blit(text, (800, 680))

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
        font = pygame.font.SysFont('sistem', 35)
        text = font.render('- элитный враг', True, 'red')
        screen.blit(text, (980, 37))
        text = font.render('- случайное событие', True, 'green')
        screen.blit(text, (980, 87))
        text = font.render('- обычный враг', True, 'grey')
        screen.blit(text, (980, 137))

        font = pygame.font.SysFont('sistem', 40)  # Кнопки для перемещения яуауаяууф
        if self.room[0] == 10:
            pygame.draw.rect(screen, 'blue', (960, 800, 300, 50))
            text = font.render('БОСС', True, 'red')
            screen.blit(text, (1060, 815))
        elif self.room[0] % 2 == 1 or (self.room[1] == 2 and self.room[0] % 2 == 0) or self.room[0] == 0:
            font = pygame.font.SysFont('sistem', 35)
            pygame.draw.rect(screen, 'blue', (960, 800, 140, 50))
            pygame.draw.rect(screen, 'blue', (1120, 800, 140, 50))
            text = font.render('< Налево', True, 'green')
            screen.blit(text, (980, 815))
            text = font.render('Направо >', True, 'green')
            screen.blit(text, (1130, 815))
        elif self.room[1] == 1:
            pygame.draw.rect(screen, 'blue', (960, 800, 300, 50))
            text = font.render('Направо >', True, 'green')
            screen.blit(text, (1040, 815))
        else:
            pygame.draw.rect(screen, 'blue', (960, 800, 300, 50))
            text = font.render('< Налево', True, 'green')
            screen.blit(text, (1040, 815))

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
            self.gold_add(self.board.getgold)
            self.screen = 3

    def boss_screen(self):
        pass

    def event_screen(self):
        pass

    def elite_screen(self):
        pass

    def gold_add(self, goldadd):  # Изменение денег
        gold_file = open(f'gold//gold{self.save}.txt', mode='w', encoding='utf-8')
        gold_file.write(str(int(self.gold) + goldadd))
        gold_file.close()
        self.gold = str(int(self.gold) + goldadd)

    def lvl_up(self, char):  # Изменение уровня
        self.lvl_file = open(f'lvl//lvl{self.save}.txt', mode='w', encoding='utf-8')
        if self.lvls[char[1]][char[0]] + 1 != 4:
            self.lvls[char[1]][char[0]] += 1
            self.gold_add(-100)
        for i in self.lvls:
            for j in i:
                self.lvl_file.write(str(j))
        self.lvl_file.close()

    def files(self):  # Файлы
        try:  # txt (деньги и уровень)
            self.gold = open(f'gold//gold{self.save}.txt', mode='r', encoding='utf-8').read()
            self.lvl = open(f'lvl//lvl{self.save}.txt', mode='r', encoding='utf-8').read()
        except Exception:
            print('Файлы не найдены')
            self.lvl = '111111111111111'
            self.gold = '10'
        self.lvls = []
        for i in range(3):
            self.lvls.append([])
            for j in range(5):
                self.lvls[i].append(int(self.lvl[i * 5 + j]))


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Dota 3')
    size = width, height = 1280, 960
    screen = pygame.display.set_mode(size)
    Dota()
