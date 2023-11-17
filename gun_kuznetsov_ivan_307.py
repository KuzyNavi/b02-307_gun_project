import math
from random import choice

import numpy as np 

import pygame
from random import randint

FPS = 120

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 1200
HEIGHT = 700


class Ball:
    '''снаряд из пушки'''
    def __init__(self, screen: pygame.Surface, x,y):
        """ Конструктор класса ball
        
        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 20
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30
    
    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.x += self.vx
        self.y -= self.vy
        self.vy -=2 # g=2 
        if self.x >= WIDTH - self.r or self.x <= self.r:
            if self.x > WIDTH - self.r:
                self.x = WIDTH - self.r
            if self.x  <= self.r:
                self.x = self.r
        
            self.vy *= 0.5
            self.vx *= - 0.5
        if self.y <= self.r:
            if self.y > HEIGHT - self.r:
                self.y = HEIGHT - self.r
            if self.y  <= self.r:
                self.y = self.r
                
            self.vy *= -0.5
            self.vx *= 0.5
    def draw(self):
        # рисует элемент класса (отрисовывает balls)
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if (obj.x - self.x) ** 2 + (obj.y - self.y) ** 2 < (self.r + obj.r) ** 2:
            return True
        else:
            return False


class Gun:
    def __init__(self, screen, x,side=1):
        """свойства пушек"""
        self.side = side
        self.direction = side
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = RED
        self.x = x
        self.y = 450
        self.vy = 5

    def fire2_start(self, event):
        """пушка активэйтед"""
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet #обращ к переменной снаружи
        bullet += 1
        new_ball = Ball(self.screen, self.x, self.y)
        self.an = self.side*math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = self.side*math.atan((event.pos[1]-450) / (event.pos[0]-20))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def drive(self, direction):
        """хотим двигать"""
        if direction == 'up' and self.y>200:
            self.y-=self.vy
        elif direction == 'down' and self.y<700:
            self.y+=self.vy

    def draw(self):
        '''рисуем пушку'''

        pygame.draw.line(self.screen, self.color, 
                        [self.x, self.y],
            [self.x + self.f2_power * math.cos(self.an), self.y + self.f2_power * math.sin(self.an)],
            10)
        
    def power_up(self):
        """Длина палки (мощность зажатия)"""
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY

class Target:
    def __init__(self, screen: pygame.Surface):
        """инциализ шарики (каждый по отдельности) каждый шарик является экземпляром класса (инкапсуляция)"""
        self.screen = screen
        '''генерация координат, где могут появиться шарики'''
        self.x = randint(200, 980)
        self.y = randint(0, 750)
        m = [5,10,15, 20, 25, 30]
        self.r = m[randint(0,len(m)-1)]
        self.points = 0
        self.live = 1
        self.new_target()
        self.vx = 1/self.r*randint(1,25)
        self.vy = 1/self.r*randint(1,25)

    def new_target(self):
        """ Инициализация новой цели. Убил и он воскрес """
        self.x = randint(200, 980)
        self.y = randint(0, 750)
        m = [10,15,20, 25, 30] #все возможные радиусы
        self.r = m[randint(0,len(m)-1)]
        self.vx = 1/self.r*randint(1,25)
        self.vy = 1/self.r*randint(1,25)
        self.color = choice([RED, BLUE, MAGENTA,GREEN,CYAN])
    
    def move(self):
        """описание движения частицы. 
        Отражение, падение..."""
        self.x += self.vx
        self.y += self.vy

        if self.x >= WIDTH - 100 - self.r or self.x <= self.r+100:
            if self.x > WIDTH -100 - self.r:
                self.x = WIDTH - 100 - self.r
            if self.x  <= self.r:
                self.x = self.r
            self.vx *= -1
            
        if self.y >= HEIGHT - self.r or self.y <= self.r:
            if self.y > HEIGHT - self.r:
                self.y = HEIGHT - self.r
            if self.y  <= self.r:
                self.y = self.r     
            self.vy *= -1

    def draw(self):
        """отрисуем шары в кажодый момент времени"""
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.r)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen,x=40,side=1)
gun2 = Gun(screen,x=1100,side=-1)
trg = [Target(screen) for i in range(0,2000)] #создание элементов
target_1 = Target(screen)
target_2 = Target(screen)
finished = False

while not finished:
    screen.fill(WHITE)
    gun.draw()
    gun2.draw()
    for el in trg: el.draw()
    for b in balls:
        b.draw()
    pygame.display.update()

    keys = pygame.key.get_pressed()
    if not False in keys: print(keys)
    
       if pygame.key.get_pressed()[pygame.K_w]: gun.drive('up') # W
    elif pygame.key.get_pressed()[pygame.K_s]: gun.drive('down') # S

    if pygame.key.get_pressed()[pygame.K_UP]: gun2.drive('up') # arrow up
    elif pygame.key.get_pressed()[pygame.K_DOWN]: gun2.drive('down') # arrow down

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP  and event.button == 1:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)
            gun2.targetting(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            gun2.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP  and event.button == 3:
            gun2.fire2_end(event)

    for el in trg: el.move()
    """проверка на соударения снаряда и шара"""
    c = 0
    for b in balls:
        b.move()
        for el in trg:
            if b.hittest(el) and el.live:
                el.hit()
                el.new_target()
                trg.remove(el)
                c+=1
    [Target(screen) for i in range(0,c)]
    c=0
    gun.power_up()

    #создаём новые шары в концы
    if not trg:
        trg = [Target(screen) for i in range(0,2000)] 


pygame.quit()
