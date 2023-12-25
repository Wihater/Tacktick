import pygame
import random
import os
import sys
import sqlite3

WIDTH, HEIGHT = 1280, 960
HEROS = {(0, 2): 'Drow ranger', (1, 2): 'Oracle', (2, 2): 'Pudge', '': ''}  # Словарь с героями и их индексацией для self.select_char


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
        self.connection = sqlite3.connect('DOTAS.db')  # Создание списка из всех героев и их статов
        self.cursor = self.connection.cursor()  # По типу [[('DrowRanger2', 24, 'range', 11, 'shotgun', 4, None)], [('Oracle3', 26, 'range', 6, 'healtime', 2, 4)], [('Pudge3', 38, 'melee', 9, 'armor', 5, None)]]
        self.hero_list = self.cursor.execute('SELECT * FROM heroes_pick').fetchall()
        self.stat_list = []
        for i in range(len(self.hero_list)):
            self.stat_list.append(self.cursor.execute(f'SELECT * FROM heroes WHERE Name="{self.hero_list[i][0] + str(self.lvls[i])}" ').fetchall())
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
                                for i in range(len(self.select_char)):  # Превращение self.select_char из списка индексов героев в список из 3 героев с уровнями по типу ['Pudge2', 'Drow ranger3', 'Oracle3']
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
                        elif self.room[0] % 2 == 1 or (self.room[1] == 2 and self.room[0] % 2 == 0) or self.room[0] == 0:
                            if 960 < event.pos[0] < 1100 and 800 < event.pos[1] < 850:
                                if self.room[1] == 0:
                                    self.room[1] = 1
                                elif self.room[1] == 2 and self.room[0] % 2 == 0:
                                    self.room[1] -= 1
                                self.room[0] += 1
                            elif 1120 < event.pos[0] < 1260 and 800 < event.pos[1] < 850:
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
                    pass

                elif self.screen == 5:
                    pass

            self.active_screen()
            pygame.display.flip()
        pygame.quit()

    def active_title(self, title):  # Экраны комнат
        if title == 'fight':
            self.screen = 4
        elif title == 'event':
            self.screen = 6
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
            self.event_screen()
        elif self.screen == 7:
            self.elite_screen()

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
                            pygame.draw.circle(screen, 'yellow', (600 - 75 * len(self.map[i]) + 150 * j, 850 - i * 65), 20)
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
        pass

    def boss_screen(self):  # Окно босса
        pass

    def event_screen(self):  # Окно события
        pass

    def elite_screen(self):  #  Окно элитного боя
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
            self.stat_list.append(self.cursor.execute(f'SELECT * FROM heroes WHERE Name="{self.hero_list[i][0] + str(self.lvls[i])}" ').fetchall())
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


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Dota 3')
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    Dota()
