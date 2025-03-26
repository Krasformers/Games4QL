#!/usr/bin/python3

# -*- coding:utf-8 -*-

import os
import pygame
import sys
from lib import World
from pygame import K_LEFT, K_RIGHT, K_SPACE
 
FPS = 60
W = 640  # ширина экрана
H = 480  # высота экрана
TEXTURE_PATH = os.path.join(
    os.getcwd(),
    "textures"
)
MOBS_GRID = [5, 5, 5, 5]
CONTROL_KEYS = {"left": K_LEFT, "right": K_RIGHT, "shot":K_SPACE}

screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
all_sprites = World(
    screen_width = W,
    screen_height = H,
    player_speed = 5,
    player_cooldown = 30,
    bullet_speed = 5,
    mobs_grid = MOBS_GRID,
    texture_path = TEXTURE_PATH,
    control_keys = CONTROL_KEYS,
    mob_cost = 100
)

 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    all_sprites.update()
    screen.fill((0,0,0))
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
