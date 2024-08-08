import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


SIZE = 10
SPEED = 20


class Point(pygame.Rect):
    def __init__(self, x, y, size):
        super().__init__(x,y,size,size)
    def my_own_update(self,x,y,size):
        self.x=x
        self.y=y
        if size is not None:
            self.width=self.height=size


class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Three Kingdom")
        self.clock = pygame.time.Clock()

        self.reds = [
            Point(random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10)
        ]
        self.blues = [
            Point(random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10)
        ]
        self.greens = [
            Point(random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10)
        ]
        self.food = [
            Point(random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10)
        ]
        for x in range(50):
            self.food.append(
                Point(random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10)
            )

    def move_points(self):
        def move_point(point):
            x, y, size = point.x, point.y, point.width
            direction = random.randint(0, 3)
            match direction:
                case 0:
                    x -= 1
                case 1:
                    x += 1
                case 2:
                    y += 1
                case 3:
                    y -= 1
            x = x % self.w
            y = y % self.h
            new_point = Point(x, y, size)
            #Creates an array to store the food that has to be removed later on
            collided_food = [food for food in self.food if new_point.colliderect(food)]
            if collided_food:
                size += 5
                #Keep the food that is not in the array that we just created
                self.food = [f for f in self.food if f not in collided_food]
    
            point.my_own_update(x, y, size)
            return point

        self.reds = [move_point(p) for p in self.reds]
        self.blues = [move_point(p) for p in self.blues]
        self.greens = [move_point(p) for p in self.greens]

    def play_step(self):
        self.move_points()
        self.update_ui()

    def update_ui(self):
        self.display.fill((0, 0, 0))
        for point in self.reds:
            pygame.draw.rect(self.display, RED, point)
        for point in self.blues:
            pygame.draw.rect(self.display, BLUE, point)
        for point in self.greens:
            pygame.draw.rect(self.display, GREEN, point)
        for point in self.food:
            pygame.draw.rect(self.display, WHITE, point)
        pygame.display.update()


if __name__ == "__main__":
    game = SnakeGame()
    # Game Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        game.play_step()
