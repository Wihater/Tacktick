import pygame
import random


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
        pass

    def boss_screen(self):
        pass

    def fight_screen(self):
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
