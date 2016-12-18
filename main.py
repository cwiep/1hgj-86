#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import pygame
import math
import random

SHOOTRANGE = 200
HEALRADIUS = 150
INVTIME = 2000
MAX_HP = 50
SHOOTTIME = 500
HEALTIME = 100

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption('The Medic by chriiis88 for 1-Hour-Gamejam #86')
pygame.key.set_repeat(20)

def dist(a, b):
    return math.sqrt((a.x - b.x)*(a.x - b.x)+(a.y - b.y)*(a.y - b.y))

class Soldier:
    def __init__(self):
        self.x = random.randint(50, 750)
        self.y = random.randint(100, 500)
        self.rect = pygame.Rect(self.x, self.y, 20, 20)
        self.color = (0, 0, 255)
        self.hp = MAX_HP
        self.target = None
        self.shoottimer = 200
        self.invtime = 0 # time that the soldier is invincible after respawn

    def _get_color(self):
        c = float(self.hp)/MAX_HP * 255
        return (0, 0, c)

    def render(self):
        pygame.draw.rect(SCREEN, self._get_color(), self.rect)
        if self.target is not None and self.target.hp > 0:
            pygame.draw.line(SCREEN, self.color, self.rect.topleft, self.target.rect.topleft)
        if self.invtime > 0:
            r = (self.rect.x - 2, self.rect.y - 2, self.rect.width + 2, self.rect.height + 2)
            pygame.draw.rect(SCREEN, (255, 255, 255), r, 1) 

    def update(self, enemies, dt):
        self.shoottimer -= dt
        # enemy still valid?
        if self.target is not None and self.target.hp > 0:
            if dist(self.rect, self.target.rect) < SHOOTRANGE:
                if self.shoottimer <= 0:
                    self.shoottimer = 500
                    self.target.damage(10)
            else:
                self.target = None
        else:
            # find next enemy
            e = None
            d = 800 # any big value
            for ee in enemies:
                if dist(self.rect, ee.rect) < SHOOTRANGE:
                    self.target = ee

        self.invtime -= dt

    def damage(self, d):
        if self.invtime <= 0:
            self.hp -= d

    def heal(self, h):
        self.hp = min(self.hp + h, MAX_HP)

    def respawn(self):
        self.hp = MAX_HP
        self.invtime = INVTIME
        
class Player(Soldier):
    def __init__(self):
        Soldier.__init__(self)
        self.rect = pygame.Rect(400, 400, 20, 20)
        self.color = (255, 255, 255)
        self.healtarget = None

    def _get_color(self):
        return self.color

    def render(self):
        Soldier.render(self)
        if self.healtarget is not None and self.healtarget.hp > 0:
            if dist(self.healtarget.rect, self.rect) < HEALRADIUS:
                pygame.draw.line(SCREEN, (128, 128, 0), self.rect.topleft, self.healtarget.rect.topleft)

    def update(self, dt):
        self.shoottimer -= dt
        if self.healtarget is not None and self.healtarget.hp > 0:
            if self.shoottimer <= 0:
                self.shoottimer = HEALTIME
                self.healtarget.heal(20)
        
class Enemy(Soldier):
    def __init__(self):
        Soldier.__init__(self)
        self.x = random.randint(200, 600)
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, 20, 20)
        self.color = (255, 0, 0)
    
    def _get_color(self):
        c = float(self.hp)/MAX_HP * 255
        return (c, 0, 0)

    def update(self, soldiers, dt):
        Soldier.update(self, soldiers, dt)
        self.rect.y += 1

def create_soldier(x, y):
    s = Soldier()
    s.rect.x = x
    s.rect.y = y
    return s

def main():
    random.seed()
    
    player = Player()
    soldiers = []
    deadsoldiers = []
    soldiers.append(create_soldier(100, 400))
    soldiers.append(create_soldier(250, 300))
    soldiers.append(create_soldier(400, 300))
    soldiers.append(create_soldier(550, 300))
    soldiers.append(create_soldier(700, 400))
    enemies = []
    enemytimermax = 2000
    enemytimer = enemytimermax
    basehp = 10
    timealive = 0

    clock = pygame.time.Clock()
    dt = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    return -1
                if keys[pygame.K_a]:
                    player.rect.x -= 5
                if keys[pygame.K_d]:
                    player.rect.x += 5
                if keys[pygame.K_w]:
                    player.rect.y -= 5
                if keys[pygame.K_s]:
                    player.rect.y += 5
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                button = event.button
                if button == 1:
                    # left 
                    s = None
                    for ss in soldiers:
                        if ss.rect.collidepoint(pos) and dist(player.rect, ss.rect) < HEALRADIUS:
                            player.healtarget = ss
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                player.healtarget = None

                    
        SCREEN.fill((0, 0, 0))
        player.update(dt)
        player.render()

        #save dead soldiers
        for s in soldiers:
            if s.hp <= 0:
                deadsoldiers.append(s)

        #clear dead soldiers
        soldiers = [s for s in soldiers if s.hp > 0]
        for soldier in soldiers:
            soldier.update(enemies, dt)
            soldier.render()

        for e in enemies:
            if e.rect.y >= 600:
                e.hp = 0
                basehp -= 1
                if len(deadsoldiers) > 0:
                    s = deadsoldiers.pop()
                    s.respawn()
                    soldiers.append(s)

        enemies = [e for e in enemies if e.hp > 0]

        # spawn new enemies
        enemytimer -= dt
        if enemytimer <= 0 and len(enemies) < 10:
            enemytimermax -= 50
            enemytimer = max(1000, enemytimermax)
            enemies.append(Enemy())

        for enemy in enemies:
            enemy.update(soldiers, dt)
            enemy.render()

        if basehp <= 0:
            return timealive
        else:
            for b in range(basehp):
                pygame.draw.circle(SCREEN, (0, 128, 0), (100 + b * 20, 580), 10)


        pygame.display.update()
        dt = clock.tick(60)
        timealive += dt

    return -1

def show_intro():
    clock = pygame.time.Clock()
    running = True
    myFont = pygame.font.SysFont("None", 35)
    fontcolor = (255, 255, 255)
    SCREEN.fill((0, 0, 0))
    SCREEN.blit(myFont.render("The Medic", 0, (200, 0, 0)), (250, 20))
    SCREEN.blit(myFont.render("As a medic, you need to stay out of sight.", 0, fontcolor), (100, 100))
    SCREEN.blit(myFont.render("You save lives.", 0, fontcolor), (100, 130))
    SCREEN.blit(myFont.render("You work behind the scenes of war.", 0, fontcolor), (100, 160))
    SCREEN.blit(myFont.render("WASD to move, left mouse to heal", 0, fontcolor), (100, 300))
    SCREEN.blit(myFont.render("Press any key to start. Good luck.", 0, fontcolor), (100, 330))
    pygame.display.update()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return

def show_outtro(timealive):
    clock = pygame.time.Clock()
    myFont = pygame.font.SysFont("None", 35)
    fontcolor = (255, 255, 255)
    SCREEN.fill((0, 0, 0))
    SCREEN.blit(myFont.render("The Medic", 0, (200, 0, 0)), (250, 20))
    SCREEN.blit(myFont.render("You survived {} seconds".format(float(timealive)/1000), 0, fontcolor), (100, 300))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.QUIT:
                return


if __name__ == '__main__':
    pygame.init()
    pygame.event.clear()
    show_intro()
    pygame.event.clear()
    timealive = main()
    pygame.event.clear()
    if timealive > 0:
        show_outtro(timealive)

