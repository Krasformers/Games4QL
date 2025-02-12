#!/usr/bin/python3

# -*- coding:utf-8 -*-

import os
import pygame
import sys
from lib import Player, mobs_generate
from pygame import K_LEFT, K_RIGHT, K_SPACE
 
FPS = 60
W = 640  # ширина экрана
H = 480  # высота экрана
TEXTURE_PATH = os.path.join(
    os.getcwd(),
    "textures"
)
MOBS_GRID = [5, 5, 5, 5]

screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

player = Player(
    speed=5,
    cooldown=FPS//2,
    bullet_speed=5,
    texture_path=TEXTURE_PATH,
    control_keys={"left": K_LEFT, "right": K_RIGHT, "shot":K_SPACE},
    display_params={"width": W, "height": H}
)
all_sprites.add(player)
mobs_generate(MOBS_GRID, all_sprites, TEXTURE_PATH, {"width": W, "height": H})
 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    all_sprites.update()
    screen.fill((0,0,0))
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
