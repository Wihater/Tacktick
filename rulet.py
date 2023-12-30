import random
import pygame

pygame.init()
size = (1280, 960)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    surf.blit(rotated_image, new_rect)


def roter(angle, img):
    screen.fill((0, 0, 0))
    blitRotateCenter(screen, img, (340, 180), angle)
    pygame.draw.polygon(screen, 'red', ((910, 480), (970, 460), (970, 500)))
    pygame.display.flip()
    clock.tick(60)


def rulet():
    my_image = pygame.image.load("images/ruletka.png").convert_alpha()
    scaled_image = pygame.transform.scale(my_image, (600, 600))
    angle = random.randint(-15, 344)
    old_angle = angle
    rulet = False
    running = True
    end = False
    end_1 = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                if end_1 == True:
                    return int(500 * res)
                if end == False:
                    rulet = True
                else:
                    end_1 = True

        if not end_1:
            blitRotateCenter(screen, scaled_image, (340, 180), angle)
            pygame.draw.polygon(screen, 'red', ((910, 480), (970, 460), (970, 500)))
            pygame.display.flip()
            screen.fill((0, 0, 0))
        else:
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont('sistem', 50)
            if -500 + 500 * res < 0:
                text = font.render(f'Вы потеряли {-(int(-500 + 500 * res))} золота!', True, 'red')
            elif -500 + 500 * res == 0:
                text = font.render('Вы ничего не получили', True, 'white')
            else:
                text = font.render('Вы получили 500 золота!', True, 'yellow')
            screen.blit(text, (400, 400))
            pygame.display.flip()

        if rulet:
            if angle - old_angle <= 40:
                angle += 2
                roter(angle, scaled_image)
            elif angle - old_angle <= 160:
                angle += 3
                roter(angle, scaled_image)
            elif angle - old_angle <= 320:
                angle += 4
                roter(angle, scaled_image)
            elif angle - old_angle <= 560:
                angle += 6
                roter(angle, scaled_image)
            elif angle - old_angle <= 1010:
                angle += 7.5
                roter(angle, scaled_image)
            elif angle - old_angle <= 2810:
                angle += 9
                roter(angle, scaled_image)
            elif angle - old_angle <= 3260:
                angle += 7.5
                roter(angle, scaled_image)
            elif angle - old_angle <= 3500:
                angle += 6
                roter(angle, scaled_image)
            elif angle - old_angle <= 3660:
                angle += 4
                roter(angle, scaled_image)
            elif angle - old_angle <= 3780:
                angle += 3
                roter(angle, scaled_image)
            elif angle - old_angle <= 3860:
                angle += 2
                roter(angle, scaled_image)
            elif angle - old_angle <= 3950:
                angle += 1.5
                roter(angle, scaled_image)
            elif angle - old_angle <= 4010:
                angle += 1
                roter(angle, scaled_image)
            elif angle - old_angle <= 4055:
                angle += 0.75
                roter(angle, scaled_image)
            elif angle - old_angle <= 4105:
                angle += 0.5
                roter(angle, scaled_image)
            elif angle - old_angle <= 4135:
                angle += 0.3
                roter(angle, scaled_image)
            else:
                if -15 <= old_angle <= 35 or 139 <= old_angle <= 189:
                    res = 0.5
                elif 36 <= old_angle <= 138:
                    res = 0
                elif 190 <= old_angle <= 240 or 293 <= old_angle <= 344:
                    res = 1
                elif 241 <= old_angle <= 292:
                    res = 2
                end = True
                rulet = False
