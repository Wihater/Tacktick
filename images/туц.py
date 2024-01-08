import pygame as pg
import sys
import os

W = 1280
H = 720

sc = pg.display.set_mode((W, H))
sc.fill((100, 150, 200))


def load_image(name, colorkey=None):
    fullname = name
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


dog_surf = load_image("OracleUlt.png")
dog_rect = dog_surf.get_rect(bottomright=(W, H))
sc.blit(dog_surf, dog_rect)

pg.display.update()

while 1:
    for i in pg.event.get():
        if i.type == pg.QUIT:
            sys.exit()

    pg.time.delay(20)
