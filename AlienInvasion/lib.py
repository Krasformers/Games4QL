#!/usr/bin/python3

# -*- coding:utf-8 -*-

import os
from pygame.sprite import Sprite, Group
from pygame.image import load
from pygame.key import get_pressed
from pygame import KEYDOWN


class Player(Sprite):
    def __init__(
            self,
            speed:int,
            cooldown:int,
            bullet_speed:int,
            texture_path:str,
            control_keys:dict,
            display_params:dict,
            *groups
        ):
        super().__init__(*groups)
        self.texture_path = texture_path
        self.image = load(os.path.join(texture_path, "player.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.control_keys = control_keys
        self.display_params = display_params
        self.rect.x = (self.display_params['width'] // 2) - (self.rect.width // 2)
        self.rect.y = self.display_params['height'] - self.rect.height
        self.speed = speed
        self.cooldown = cooldown
        self.bullet_speed = bullet_speed
        self.rest_cooldown = 0


    def update(self, *args, **kwargs):
        self.rest_cooldown -= 1
        if self.rest_cooldown < 0:
            self.rest_cooldown = 0
        pressed_keys = get_pressed()
        if pressed_keys[self.control_keys["left"]]:
            self.move_left()
        if pressed_keys[self.control_keys["right"]]:
            self.move_right()
        if pressed_keys[self.control_keys["shot"]] and (self.rest_cooldown == 0):
            self.shot()

    def move_left(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.rect.x = 0
    
    def move_right(self):
        self.rect.x += self.speed
        if self.rect.x + self.rect.width > self.display_params['width']:
            self.rect.x = self.display_params['width'] - self.rect.width
    
    def shot(self):
        self.groups()[0].add(
            Bullet(
                self.texture_path,
                self.bullet_speed,
                (self.rect.centerx, self.rect.top)
            )
        )
        self.rest_cooldown = self.cooldown


class Bullet(Sprite):
    def __init__(
            self,
            texture_path:str,
            speed:int,
            start_point:tuple[int],
            *groups
        ):
        super().__init__(*groups)
        self.image = load(os.path.join(texture_path, "bullet.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = speed
        self.rect.bottom = start_point[1]
        self.rect.centerx = start_point[0]
    
    def move(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.groups()[0].remove(self)
    
    def check_hit(self):
        for entity in self.groups()[0].sprites():
            if isinstance(entity, Mob):
                if self.rect.colliderect(entity.rect):
                    self.groups()[0].remove([entity, self])
                    return
    
    def update(self, *args, **kwargs):
        self.check_hit()
        self.move()


class Mob(Sprite):
    def __init__(
            self,
            texture_path:str,
            x_delay:int,
            y_delay:int,
            x_speed:int,
            y_speed:int,
            steps_to_next_turn:int,
            direction:bool,
            x_position:int,
            y_position:int,
            *groups
        ):
        super().__init__(*groups)
        self.image = load(os.path.join(texture_path, "mob.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x_position
        self.rect.centery = y_position
        self.x_delay = x_delay
        self.y_delay = y_delay
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.steps_to_next_turn = steps_to_next_turn
        self.direction = direction
        self.rest_x_delay = 0
        self.rest_y_delay = 0
        self.counter_steps_to_next_turn = steps_to_next_turn // 2

    def move(self):
        if self.rest_x_delay >= self.x_delay:
            self.rest_x_delay = 0
            if self.counter_steps_to_next_turn >= self.steps_to_next_turn:
                self.direction = not self.direction
                self.counter_steps_to_next_turn = 0
            if self.direction:
                self.rect.centerx += self.x_speed
            else:
                self.rect.centerx -= self.x_speed
            self.counter_steps_to_next_turn += 1
        if self.rest_y_delay >= self.y_delay:
            self.rest_y_delay = 0
            self.rect.centery += self.y_speed
        self.rest_x_delay += 1
        self.rest_y_delay += 1
        

    def update(self, *args, **kwargs):
        self.move()


def mobs_generate(
        mobs_grid:list,
        sprite_group:Group,
        texture_path:str,
        display_params:dict
    ):
    y_step = 64
    x_step = 64
    x_speed = 2
    teps_to_next_turn = 64
    for v_level in range(len(mobs_grid)):
        count_mobs = mobs_grid[v_level]
        occupy_width = (count_mobs + 1) * x_step + x_speed * teps_to_next_turn
        while occupy_width > display_params['width']:
            count_mobs -= 1
            occupy_width = (count_mobs + 1) * x_step + x_speed * teps_to_next_turn
        first_cood = (display_params['width'] - occupy_width) // 2 + (x_speed * teps_to_next_turn) // 2
        for x_pos in range(count_mobs):
            sprite_group.add(
                Mob(
                    texture_path=texture_path,
                    x_delay=0,
                    y_delay=64,
                    x_speed=2,
                    y_speed=8,
                    steps_to_next_turn=64,
                    direction=v_level%2,
                    x_position=(x_pos * x_step) + first_cood,
                    y_position=y_step*(v_level+1)
                )
            )

