import pygame
import random
import os
import sys
import sqlite3
import rulet

WIDTH, HEIGHT = 1280, 960
CLOCK = pygame.time.Clock()

HEROS = {0: 'DrowRanger', 1: 'Oracle', 2: 'Pudge', '': '', 3: 'Mars', 4: 'BountyHunter'}  # Словарь с героями и их индексацией для self.select_char
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
              'это событие навсегда)'],
          3: ['Кто-то решил организовать',
              'в лесу полноценное казино.',
              'Среди всех способов',
              'проиграть свои деньги вам',
              'приглянулась эта рулетка.',
              '',
              'Готовы потратить 100 золота?'],
          4: ['перед вами оказался великий',
              'и могущественный заклинатель',
              'Warlock. Он предлагает сделку.',
              'Он просит 100 монет, иначе он',
              'наложит на вас проклятие',
              '',
              'Заплатить?']}


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


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(Dota.all_sprites)
        if x1 == x2:
            self.add(Dota.vertical_b)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(Dota.horizontal_b)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Dvd(pygame.sprite.Sprite):
    dota = load_image('dota DVD.png', 'images')
    dota = pygame.transform.scale(dota, (100, 100))

    def __init__(self, x, y):
        super().__init__(Dota.all_sprites)
        self.image = Dvd.dota
        self.rect = pygame.Rect(x, y, 100, 100)
        self.vx = 5
        self.vy = 5

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, Dota.horizontal_b):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, Dota.vertical_b):
            self.vx = -self.vx
        CLOCK.tick(60)


class Hero:
    def __init__(self, name, hp, type, att, ult, ult1, ult2, ultmana):
        self.level = int(name[-1])
        self.name = name[:len(name) - 1]
        self.standhp, self.hp = hp, hp
        self.type = type
        self.att = att
        self.ult = ult  # название способности
        self.ult1 = ult1
        self.ult2 = ult2
        self.buff = []
        self.ultmana = ultmana
        self.animation = ''
        self.count = 0

    def typebaff(self, name):  # Возрашает список тегов эффектов
        types = {'armor': ["armor", "-damage"],
                 "healtime": ["dopheal"],
                 "arena": ["arena"],
                 'shield': ['+attake']}
        return types[name]

    def damage(self, dmg, magic=False):  # Нанести урон этому персонажу
        if self.type == "melee" and not magic:
            if random.randint(0, 4) > 2 and dmg > 0:
                dmg -= 1

        for i in self.buff:
            if "-damage" in self.typebaff(i[0]):
                dmg -= i[2]
        if dmg < 0:
            dmg = 0
        print("Damage = ", dmg)
        self.hp -= dmg

    def heal(self, heal):  # Лечение
        for i in self.buff:
            if "dopheal" in self.typebaff(i[0]):
                heal += i[2]

        self.hp += heal
        if self.hp > self.standhp:
            self.hp = self.standhp

    def get_att(self, att=0):  # Возращает нынешний урон обычной атакой
        att += self.att
        for i in self.buff:
            if "+attake" in self.typebaff(i[0]):
                att += i[2]
        if att < 1:
            att = 1
        return att

    def get_image(self, prepiska=""):  # Возращает картинку ( и нужную анимацию)
        if self.count == 0:
            self.animation = ''
        if self.animation == '':
            return "images\\" + self.name + prepiska + ".png"
        elif self.animation == 'a':
            self.count -= 1
            return "images\\" + self.name + "Attake.png"
        elif self.animation == 'u':
            self.count -= 1
            return "images\\" + self.name + "Ult.png"

    def stats(self):
        return [self.name, self.standhp, self.hp, self.get_att(), self.ult, self.buff]

    def checktimesbaff(self, ranges=-1):
        if ranges == -1:
            ranges = 0
        for i in range(ranges, len(self.buff)):
            self.buff[i][1] -= 1
            if self.buff[i][1] <= 0:
                self.buff.pop(i)
                self.checktimesbaff(i)
                break

    def anim(self, type):
        self.animation = type
        self.count = 10


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
        self.point = []
        self.getgold = 0
        self.buttonattacke = False
        self.mana = 1

    def clicked(self, who):
        if self.buttonattacke:
            if self.plrs[self.getplr - 1].name == "BountyHunter":
                self.getgold += 7
            self.enems[who].damage(self.plrs[self.getplr - 1].get_att())
            self.plrs[self.getplr - 1].anim('a')
            self.loop()
            self.point = []
            if self.mana < 4:
                self.mana += 1
        else:
            if self.mana >= self.plrs[self.getplr - 1].ultmana:
                self.mana -= self.plrs[self.getplr - 1].ultmana
                self.plrs[self.getplr - 1].anim('u')
                getattr(self, f'ult_{self.plrs[self.getplr - 1].ult}')(who)
                self.loop()
                self.point = []

    def ult_armor(self, who):
        self.plrs[who].heal(3)
        self.plrs[who].buff.append(['armor', 2, self.plrs[who].ult1])
        self.plrs[who].buff.append(['arena', 2])

    def ult_healtime(self, who):
        self.plrs[who].heal(2)
        self.plrs[who].buff.append(['healtime', 4, self.plrs[self.getplr - 1].ult1, self.plrs[self.getplr - 1].ult2])

    def ult_shotgun(self, who):
        for i in range(3):
            if self.enems[i] != None:
                self.enems[i].damage(self.plrs[who].ult1)

    def ult_crit(self, who):
        self.enems[who].damage(self.plrs[self.getplr - 1].ult1)

    def ult_shield(self, who):
        self.plrs[who].buff.append(['armor', 2, self.plrs[who].ult2])
        self.plrs[who].buff.append(['shield', 2, self.plrs[who].ult1])
        self.plrs[who].buff.append(['arena', 1])

    def ult_fall(self, who):
        self.plrs[who].damage(self.enems[1].ult1)

    def get_map(self):
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
        if (not self.buttonattacke and self.plrs[kash].ult in ['shotgun', 'crit']) or self.buttonattacke:
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
        if self.plrs[kash].ult in ['armor', 'shield'] and not self.buttonattacke:
            self.point.append(3)
            kash1alpha = pygame.image.load("images\\retplayer.png").convert_alpha()
            kash1surf = pygame.transform.scale(kash1alpha, (80, 80))
            kash1rect = kash1surf.get_rect()
            screen.blit(kash1surf,
                        (kash1rect.x + 480 - 200 * kash - 1, kash1rect.y + 620, kash1rect.width, kash1rect.height))

    def update(self):
        if self.phase == "startgame":
            self.loop()
        elif self.phase == "startr":
            if self.whomove == "plr":
                if self.plrs[self.getplr - 1] != None and self.plrs[self.getplr - 1].buff != []:
                    for i in self.plrs[self.getplr - 1].buff:
                        if i[0] in ["Poison"]:
                            self.plrs[self.getplr - 1].damage(i[2], i[3])
                    self.plrs[self.getplr - 1].checktimesbaff()
                self.checkdie()
                self.loop()
                self.buttonattacke = True
                self.phase = "plr"
            else:
                if self.enems[self.getenem - 1] != None and self.enems[self.getenem - 1].buff != []:
                    for j in self.enems[self.getenem - 1].buff:
                        if j[0] in ["Poison"]:
                            self.enems[self.getenem - 1].damage(j[2], j[3])
                    self.enems[self.getenem - 1].checktimesbaff()
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
            if None not in self.plrs and random.randint(1, 10) > 6 and enemy.name == 'Roshan':
                for i in range(3):
                    self.plrs[i].damage(enemy.ult1)
            elif enemy.level in [1, 2, 3, 6, 8]:
                if random.randint(1, 100) >= 86 - 3 * enemy.level:
                    for i in self.plrs:
                        if i != None:
                            for j in i.buff:
                                if "arena" in i.typebaff(j[0]):
                                    i.damage(enemy.get_att() * 2, i.type)
                                    flag = False
                                    break
                        if not flag:
                            break
                    if flag:
                        kash = random.randint(0, 2)
                        while self.plrs[kash] == None:
                            kash = random.randint(0, 2)
                        self.plrs[kash].damage(enemy.get_att() * 2)
                else:
                    for i in self.plrs:
                        if i != None:
                            for j in i.buff:
                                if "arena" in i.typebaff(j[0]):
                                    i.damage(enemy.get_att(), i.type)
                                    flag = False
                                    break
                        if not flag:
                            break
                    if flag:
                        kash = random.randint(0, 2)
                        while self.plrs[kash] == None:
                            kash = random.randint(0, 2)
                        self.plrs[kash].damage(enemy.get_att())


            self.loop()
        elif self.phase == "end":
            for i in self.mapdeffect:
                kash = self.get_mapdeffecttype(i)
                if "PLRSHeal" in kash:
                    for j in self.plrs:
                        if j != None:
                            j.heal(kash[1])
                if "PLRSDamage" in kash:
                    for j in self.plrs:
                        if j != None:
                            j.damage(kash[1], True)
                if "ENEMYESHeal" in kash:
                    for j in self.enems:
                        if j != None:
                            j.heal(kash[1])
                if "ALLDamage" in kash:
                    for j in self.plrs:
                        if j != None:
                            j.damage(kash[1], True)
                    for j in self.enems:
                        if j != None:
                            j.damage(kash[1], True)
            self.phase = "startgame"

    def loop(self):
        self.checkdie()
        if self.phase == 'startgame':
            for i in range(3):
                if self.plrs[i] != None:
                    self.phase = "startr"
                    self.whomove = 'plr'
                    self.getplr = i + 1
                    break
                elif self.enems[i] != None:
                    self.phase = "startr"
                    self.whomove = 'enem'
                    self.getenem = i + 1
                    break
        elif self.phase == 'plr':
            self.buttonattacke = True
            if self.enems[self.getplr - 1] != None:
                self.phase = "startr"
                self.whomove = 'enem'
                self.getenem = self.getplr
                self.enems[self.getenem - 1].checktimesbaff()
            else:
                for i in range(self.getplr, 3):
                    if self.plrs[i] != None:
                        self.phase = "startr"
                        self.whomove = 'plr'
                        self.getplr = i + 1
                        self.plrs[i].checktimesbaff()
                        break
                    elif self.enems[i] != None:
                        self.phase = "startr"
                        self.whomove = 'enem'
                        self.getenem = i + 1
                        self.enems[i].checktimesbaff()
                        break
                else:
                    self.phase = "end"
        elif self.phase == "enem":
            if self.getenem != 3 and self.plrs[self.getenem] != None:
                self.phase = "startr"
                self.whomove = 'plr'
                self.getplr = self.getenem + 1
                self.plrs[self.getplr - 1].checktimesbaff()
            elif self.getenem == 3:
                self.phase = 'end'
            else:
                for i in range(self.getenem, 3):
                    if self.plrs[i] != None:
                        self.phase = "startr"
                        self.whomove = 'plr'
                        self.getplr = i + 1
                        self.plrs[i].checktimesbaff()
                        break
                    elif self.enems[i] != None:
                        self.phase = "startr"
                        self.whomove = 'enem'
                        self.getenem = i + 1
                        self.enems[i].checktimesbaff()
                        break
                else:
                    self.phase = "end"


class Dota:
    all_sprites = pygame.sprite.Group()
    horizontal_b = pygame.sprite.Group()
    vertical_b = pygame.sprite.Group()
    restart_img = load_image('restart.png', 'images')
    restart_img = pygame.transform.scale(restart_img, (49, 49))

    def __init__(self):
        Border(5, 5, WIDTH - 5, 5)
        Border(5, 5, 5, HEIGHT - 5)
        Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
        Border(0, 500, 1280, 500)
        Dvd(640, 150)
        self.start()
        self.running = True
        self.connection = sqlite3.connect('DOTAS.db')
        self.cursor = self.connection.cursor()
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
                                    self.select_char[i] = HEROS[self.select_char[i]] + str(
                                        self.lvls[int(self.select_char[i])])

                        elif 460 < event.pos[0] < 610 and 600 < event.pos[1] < 675:  # Улучшение
                            if int(self.gold) >= 100:
                                self.lvl_up(self.select_char[self.select - 1])

                        else:  # Составление отряда
                            for i in range(len(self.hero_list)):
                                if 220 + i * 80 - i // 3 * 240 < event.pos[0] < 220 + i * 80 - i // 3 * 240 + 70 \
                                        and 180 + i // 3 * 80 < event.pos[1] < 180 + i // 3 * 80 + 70:
                                    if i not in self.select_char:
                                        self.select_char[self.select - 1] = i

                elif self.screen == 3:
                    if event.type == pygame.MOUSEBUTTONUP:
                        if 50 < event.pos[0] < 100 and 50 < event.pos[1] < 100:
                            self.start()
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
                                self.room[0] += 1
                                self.movement()
                        else:
                            if 960 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
                                self.room[0] += 1
                                self.room[1] -= 1
                                self.movement()

                elif self.screen == 4:
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and \
                            self.board.plrs != [None, None, None] and self.board.enems != [None, None, None]:
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
                            1] < 930 and self.board.enems != [None, None, None]:
                            self.board.buttonattacke = False

                        if 800 < event.pos[0] < 970 and 780 < event.pos[
                            1] < 930 and self.board.enems != [None, None, None]:
                            self.board.buttonattacke = True

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and \
                            self.board.enems == [None, None, None]:
                        if self.map[self.room[0] - 1][self.room[1] - 1] == "elite":
                            self.gold_add(self.board.getgold * 3)
                            self.fin_gold += self.board.getgold * 3
                        else:
                            self.gold_add(self.board.getgold)
                            self.fin_gold += self.board.getgold
                        self.screen = 3

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and \
                            self.board.plrs == [None, None, None]:
                        self.select_char = ['', '', '']
                        self.start()
                        self.screen = 2

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
                        elif 1050 < event.pos[0] < 1230 and 800 < event.pos[1] < 850:
                            self.event_res(5)
                            self.screen = 3

            self.active_screen()
            pygame.display.flip()
        pygame.quit()

    def movement(self):
        if self.map[self.room[0] - 1][self.room[1] - 1] == 'event':
            self.active_title(self.map[self.room[0] - 1][self.room[1] - 1])
        elif self.map[self.room[0] - 1][self.room[1] - 1] == 'fight':
            kash = [random.choices(['GhostCreap', 'Wood', 'Creep'])[0] for i in range(3)]
            for i in range(3):
                kash[i] += str((self.room[0] + self.room[1]) // 4 + 1)
            self.board = Fight(self.select_char, kash)
            self.screen = 4
        elif self.map[self.room[0] - 1][self.room[1] - 1] == 'elite':
            kash = [random.choices(['GhostCreap', 'Wood', 'Creep'])[0] for i in range(3)]
            for i in range(3):
                kash[i] += '6'
            self.board = Fight(self.select_char, kash)
            self.screen = 4


    def active_title(self, title):  # Экраны комнат
        if title == 'fight':
            self.screen = 4
        elif title == 'event':
            self.screen = 7
        elif title == 'elite':
            self.screen = 4

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
        elif self.screen == 'f':
            self.fin_screen()
        elif self.screen == 'e':
            self.event_screen()

    def main_screen(self):  # Меню
        # fon = pygame.transform.scale(load_image('dota.jpg', 'data'), (WIDTH, HEIGHT))
        # screen.blit(fon, (0, 0))
        Dota.all_sprites.draw(screen)
        for i in Dota.all_sprites:
            i.update()
        pygame.draw.rect(screen, (235, 122, 52), (0, 500, 1280, 400))
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
                for ij in self.select_char:
                    if ij != '':
                        if i == ij:
                            pygame.draw.rect(screen, 'red', (220 + i * 80 - i // 3 * 240, 180 + i // 3 * 80, 70, 70), 5)

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
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1]][0][3]), 'red', (670, 250))
            self.print_text(40, 'Навык:', 'blue', (480, 290))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1]][0][4]), 'blue', (670, 290))
            self.print_text(40, 'HP:', 'green', (480, 330))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1]][0][1]), 'green', (670, 330))
            self.print_text(40, 'Уровень:', (0, 49, 163), (480, 370))
            self.print_text(40, str(self.lvls[self.select_char[self.select - 1]]), (0, 49, 163), (670, 370))
            self.print_text(40, 'Тип атаки:', 'yellow', (480, 410))
            self.print_text(40, str(self.stat_list[self.select_char[self.select - 1]][0][2]), 'yellow', (670, 410))

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
        pygame.draw.rect(screen, 'green', (50, 50, 50, 50))
        screen.blit(Dota.restart_img, (51, 51))
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
            pygame.draw.rect(screen, (255, 255, 255), (0, 0, 800, 850))
            backG_Image = pygame.image.load(self.board.get_map())
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, backG_rect)
            backG_Image = pygame.image.load('images\\backGMana.png')
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, (backG_rect.x + 15, backG_rect.y + 170, backG_rect.width,
                                      backG_rect.height))
            for i in range(4):
                if self.board.mana - 1 - 1 * i >= 0:
                    mana_Image = pygame.image.load('images\\ManaPoint.png')
                    mana_surt = pygame.transform.scale(mana_Image, (52, 52))
                    mana_rect = mana_Image.get_rect()
                    screen.blit(mana_surt, (mana_rect.x + 40 + i * 58, mana_rect.y + 240, mana_rect.width,
                                            mana_rect.height))
                else:
                    mana_Image = pygame.image.load('images\\ManaBreak.png')
                    mana_surt = pygame.transform.scale(mana_Image, (52, 52))
                    mana_rect = mana_Image.get_rect()
                    screen.blit(mana_surt, (mana_rect.x + 40 + i * 58, mana_rect.y + 240, mana_rect.width,
                                            mana_rect.height))
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
            backG_Image = pygame.image.load(self.board.get_map())
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, backG_rect)
            backG_Image = pygame.image.load('images\\ScreenWin.png').convert_alpha()
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, backG_rect)
            if self.map[self.room[0] - 1][self.room[1] - 1] == "elite":
                self.print_text(75, str(self.board.getgold * 3), 'yellow', (410, 420))
            else:
                self.print_text(75, str(self.board.getgold), 'yellow', (410, 420))

        else:
            backG_Image = pygame.image.load(self.board.get_map())
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, backG_rect)
            backG_Image = pygame.image.load('images\\ScreenLose.png').convert_alpha()
            backG_rect = backG_Image.get_rect()
            screen.blit(backG_Image, backG_rect)
            self.print_text(75, str(self.fin_gold), 'yellow', (410, 420))

    def boss_screen(self):
        self.fight_screen()

    def event_pick(self):
        self.connection = sqlite3.connect('DOTAS.db')
        self.cursor = self.connection.cursor()
        self.event_list = self.cursor.execute('SELECT * FROM events').fetchall()
        self.connection.close()
        self.event = ['st']
        while self.event[-1] in self.event_flag:
            self.event = random.choice(self.event_list)
        self.screen = 'e'

    def event_screen(self):
        pygame.draw.rect(screen, (135, 135, 161), (800, 0, 500, 1000))
        pygame.draw.rect(screen, self.event[8], (850, 800, 180, 50))
        pygame.draw.rect(screen, self.event[9], (1050, 800, 180, 50))
        self.print_text(70, self.event[1], 'red', (900, 100))
        self.print_text(30, self.event[2], self.event[8], (830, 750))
        self.print_text(30, self.event[3], self.event[9], (1060, 750))
        self.print_event(40, EVENTS[self.event[0]], self.event[8], (840, 200))

    def event_res(self, res):
        if self.event[-1] != 'x':
            self.event_flag.append(self.event[-1])
        if self.event[res] == 'buff_add':
            if self.event[res + 2][0] == '-':
                self.debuffs.append(self.event[res + 2][1:])
            else:
                self.buffs.append(self.event[res + 2])
        elif self.event[res] == 'gold_add':
            self.gold_add(int(self.event[res + 2]))
            self.fin_gold += int(self.event[res + 2])
        elif self.event[res] == 'file_edit':
            self.connection = sqlite3.connect('DOTAS.db')
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                f'UPDATE events SET effect1 = {str(int(self.event[6]) + int(self.event[7]))} WHERE id = {self.event[0]}')
            self.cursor.execute(
                f'UPDATE events SET var1text = "Получить золото ({str(int(self.event[6]) + int(self.event[7]))})" WHERE id = {self.event[0]}')
            self.connection.commit()
            self.connection.close()
        elif self.event[res] == 'rulet' and int(self.gold) >= 100:
            self.result = rulet.rulet()
            self.gold_add(-100 + self.result)
            self.fin_gold += -100 + self.result

    def event_pick(self):
        self.connection = sqlite3.connect('DOTAS.db')
        self.cursor = self.connection.cursor()
        self.event_list = self.cursor.execute('SELECT * FROM events').fetchall()
        self.connection.close()
        self.event = ['st']
        while self.event[-1] in self.event_flag:
            self.event = random.choice(self.event_list)
        self.screen = 'e'

    def event_screen(self):
        pygame.draw.rect(screen, (135, 135, 161), (800, 0, 500, 1000))
        pygame.draw.rect(screen, self.event[8], (850, 800, 180, 50))
        pygame.draw.rect(screen, self.event[9], (1050, 800, 180, 50))
        self.print_text(70, self.event[1], 'red', (900, 100))
        self.print_text(30, self.event[2], self.event[8], (830, 750))
        self.print_text(30, self.event[3], self.event[9], (1060, 750))
        self.print_event(40, EVENTS[self.event[0]], self.event[8], (840, 200))

    def event_res(self, res):
        if self.event[-1] != 'x':
            self.event_flag.append(self.event[-1])
        if self.event[res] == 'buff_add':
            if self.event[res + 2][0] == '-':
                self.debuffs.append(self.event[res + 2][1:])
            else:
                self.buffs.append(self.event[res + 2])
        elif self.event[res] == 'gold_add':
            self.gold_add(int(self.event[res + 2]))
            self.fin_gold += int(self.event[res + 2])
        elif self.event[res] == 'file_edit':
            self.connection = sqlite3.connect('DOTAS.db')
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                f'UPDATE events SET effect1 = {str(int(self.event[6]) + int(self.event[7]))} WHERE id = {self.event[0]}')
            self.cursor.execute(
                f'UPDATE events SET var1text = "Получить золото ({str(int(self.event[6]) + int(self.event[7]))})" WHERE id = {self.event[0]}')
            self.connection.commit()
            self.connection.close()
        elif self.event[res] == 'rulet' and int(self.gold) >= 100:
            self.result = rulet.rulet()
            self.gold_add(-100 + self.result)
            self.fin_gold += -100 + self.result

    def fin_screen(self):
        self.print_text(50, f'Вы заработали {self.fin_gold} золота!', 'yellow', (100, 200))

    def gold_add(self, goldadd):  # Изменение денег
        gold_file = open(f'gold//gold{self.save}.txt', mode='w', encoding='utf-8')
        gold_file.write(str(int(self.gold) + goldadd))
        gold_file.close()
        self.gold = str(int(self.gold) + goldadd)

    def lvl_up(self, char):  # Изменение уровня
        self.lvl_file = open(f'lvl//lvl{self.save}.txt', mode='w', encoding='utf-8')
        if self.lvls[char] + 1 != 6:
            self.lvls[char] += 1
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
            self.lvl = '11111'
            self.gold = '10'
        self.lvls = []
        for i in range(len(self.lvl)):
            self.lvls.append(int(self.lvl[i]))

    def start(self):  # Старт программы и любые возвращения в меню
        self.buffs = []  # Список бафов
        self.debuffs = []
        self.event_flag = ['st']
        self.room = [0, 0]
        self.save = 1  # Сохранение (1 окно)
        self.files()
        self.fin_gold = 0  # Подсчет золота
        self.select = 1  # Выбранный слот отряда (2 окно)
        self.screen = 1  # Номер экрана (для active_screen())
        self.select_char = ['', '', '']  # Отряд
        self.map = []
        self.map_titles = ['fight', 'fight']
        self.map.append(self.map_titles)
        self.map_rooms = [3, 2, 3, 2, 3, 2, 3, 2, 3]
        for i in range(9):  # Генератор карты
            self.map_titles = []
            for j in range(self.map_rooms[i]):
                self.map_titles.append(
                    random.choice(('fight', 'fight', 'fight', 'fight', 'fight', 'fight', 'event', 'event', 'elite')))
            self.map.append(self.map_titles)

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
