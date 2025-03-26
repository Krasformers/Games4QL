#!/usr/bin/python3

# -*- coding:utf-8 -*-

import sys
import os
from pygame.sprite import Sprite, Group
from pygame.rect import Rect
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
            screen_width:int,
            screen_height:int,
            bullets_group:Group,
            mobs_group:Group,
            *groups
        ):
        super().__init__(*groups)
        self.texture_path = texture_path
        self.image = load(os.path.join(texture_path, "player.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.control_keys = control_keys
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rect.x = (self.screen_width // 2) - (self.rect.width // 2)
        self.rect.y = self.screen_height- self.rect.height
        self.speed = speed
        self.cooldown = cooldown
        self.bullet_speed = bullet_speed
        self.rest_cooldown = 0
        self.bullets_group = bullets_group
        self.mobs_group = mobs_group


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
        if self.rect.x + self.rect.width > self.screen_width:
            self.rect.x = self.screen_width - self.rect.width
    
    def shot(self):
        self.bullets_group.add(
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
            start_point:tuple[int, int],
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
            self.groups()[0].remove(self) # type: ignore
    
    def update(self, *args, **kwargs):
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


class World(Group):
    def __init__(
            self,
            screen_width:int,
            screen_height:int,
            player_speed:int,
            player_cooldown:int,
            bullet_speed:int,
            mobs_grid:list,
            texture_path:str,
            control_keys:dict,
            mob_cost:int,
            *sprites
        ) -> None:
        super().__init__(*sprites)
        self.texture_path = texture_path
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mob_cost = mob_cost
        self.points = 0
        self.bullets = Group()
        self.mobs = Group()
        self.mobs_generate(
            mobs_grid,
            self.mobs,
            self.texture_path,
            self.screen_width
        )
        self.player = Player(
            player_speed,
            player_cooldown,
            bullet_speed,
            self.texture_path,
            control_keys,
            self.screen_width,
            self.screen_height,
            self.bullets,
            self.mobs
        )
        self.add(self.player)
        
    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self.bullets.update()
        self.mobs.update()
        self.check_hit()
        self.game_over()

    def draw(self, surface, bgsurf = None, special_flags = 0) -> list[Rect]:
        super().draw(surface, bgsurf, special_flags)
        self.bullets.draw(surface, bgsurf, special_flags)
        self.mobs.draw(surface, bgsurf, special_flags)
        self.lostsprites = []
        dirty = self.lostsprites
        return dirty

    def mobs_generate(
            self,
            mobs_grid:list,
            sprite_group:Group,
            texture_path:str,
            screen_width:int,
        ) -> None:
        y_step = 64
        x_step = 64
        x_speed = 2
        teps_to_next_turn = 64
        for v_level in range(len(mobs_grid)):
            count_mobs = mobs_grid[v_level]
            occupy_width = (count_mobs + 1) * x_step + x_speed * teps_to_next_turn
            while occupy_width > screen_width:
                count_mobs -= 1
                occupy_width = (count_mobs + 1) * x_step + x_speed * teps_to_next_turn
            first_cood = (screen_width- occupy_width) // 2 + (x_speed * teps_to_next_turn) // 2
            for x_pos in range(count_mobs):
                sprite_group.add(
                    Mob(
                        texture_path=texture_path,
                        x_delay=0,
                        y_delay=64,
                        x_speed=2,
                        y_speed=8,
                        steps_to_next_turn=64,
                        direction=bool(v_level%2),
                        x_position=(x_pos * x_step) + first_cood,
                        y_position=y_step*(v_level+1)
                    )
                )

    def check_hit(self) -> None:
        for bullet in self.bullets.sprites():
            for mob in self.mobs.sprites():
                if bullet.rect.colliderect(mob.rect):
                    self.points += self.mob_cost
                    print(self.points)
                    self.mobs.remove(mob)
                    self.bullets.remove(bullet)
    
    def check_end_game(self) -> int:
        if len(self.mobs.sprites()) == 0:
            return 1
        for mob in self.mobs.sprites():
            if mob.rect.bottom >= self.player.rect.top:
                return -1
        return 0

    def game_over(self) -> None:
        end_game = self.check_end_game()
        if end_game == 0:
            return None
        if end_game == 1:
            print('Win!')
            sys.exit()
        if end_game == -1:
            print('Lose!')
            sys.exit()
