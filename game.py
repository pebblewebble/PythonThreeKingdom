import pygame
import random
from enum import Enum
import numpy as np
# from collections import namedtuple

# TO DO LIST
# 2. Reinforcement Learning later on
# 3. I think it sometimes doesn't eat other rect, especially when two rects colliding are moving is because
# I am redrwaing them every frame, so according to reddit, it is better to just use the move() method for rects.

pygame.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BLACK = (0, 0, 0)


SIZE = 10
SPEED = 20
CELL_SIZE = 50


class Point(pygame.Rect):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, size)
        self.color = color

    def my_own_update(self, x, y, size):
        self.x = x
        self.y = y
        if size is not None:
            self.width = self.height = size


class SnakeGame:
    def __init__(self, w=1080, h=700):
        self.iteration=0
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Three Kingdom")
        self.clock = pygame.time.Clock()
        self.player_direction = 0

        self.reds = [
            Point(random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10, RED)
        ]
        self.blues = [
            Point(
                random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10, BLUE
            )
        ]
        self.greens = [
            Point(
                random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10, GREEN
            )
        ]
        self.food = [
            Point(
                random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10, WHITE
            )
        ]
        self.player = [
            Point(
                random.randint(0, self.w - 1), random.randint(0, self.h - 1), 10, YELLOW
            )
        ]
        foodToAdd = int(((self.w * self.h) / 5) / 1000)
        # foodToAdd=1000
        self.foodCounter = 1
        for x in range(foodToAdd):
            self.foodCounter += 1
            print("Added 1 food | Total Food on Screen = " + str(self.foodCounter))
            self.food.append(
                Point(
                    random.randint(0, self.w - 1),
                    random.randint(0, self.h - 1),
                    10,
                    WHITE,
                )
            )
        self.test = 0
        self.grid = {}
        self.update_grid()

    def update_grid(self):
        self.grid.clear()
        for point_list in [self.reds, self.blues, self.greens, self.food, self.player]:
            for point in point_list:
                cell = (point.x // CELL_SIZE, point.y // CELL_SIZE)
                if cell not in self.grid:
                    self.grid[cell] = []
                self.grid[cell].append(point)

    def move_points(self):
        def move_point(point, player):
            x, y, size, color = point.x, point.y, point.width, point.color
            direction = random.randint(0, 3)
            movement_speed = 1
            if player and self.player_direction == -1:
                return point
            if player:
                direction = self.player_direction
                movement_speed = 1
                self.player_direction = -1
            match direction:
                case 0:
                    x -= movement_speed
                case 1:
                    x += movement_speed
                case 2:
                    y += movement_speed
                case 3:
                    y -= movement_speed
            x = x % self.w
            y = y % self.h
            new_point = Point(x, y, size, color)

            current_cell = (point.x // CELL_SIZE, point.y // CELL_SIZE)
            if current_cell not in self.grid:
                self.grid[current_cell] = []

            # Creates an array to store the food that has to be removed later on
            collided_food = []
            collided_reds = []
            collided_blues = []
            collided_greens = []
            collided_player = []

            # for grid_point in self.grid[current_cell]:
            for grid_point in self.reds + self.greens + self.blues + self.food + self.player:
                # We check for color logic here but there is another check below just in case i guess
                if (
                    new_point.colliderect(grid_point)
                    and grid_point != point
                    and grid_point.color != new_point.color
                ):
                    # print(grid_point.color, new_point.color)
                    # print("COLLIDED")
                    # self.test = self.test + 1
                    # print(self.test)
                    if grid_point in self.food:
                        collided_food.append(grid_point)
                    elif grid_point in self.reds:
                        collided_reds.append(grid_point)
                    elif grid_point in self.greens:
                        collided_greens.append(grid_point)
                    elif grid_point in self.blues:
                        collided_blues.append(grid_point)
                    elif grid_point in self.player:
                        collided_player.append(grid_point)
            if collided_player:
                for player in collided_player:
                    size+=5
                    self.player.remove(player)
                    self.spawn_point(color)
            if collided_food:
                # Keep the food that is not in the array that we just created
                for food in collided_food:
                    size += 5
                    self.food.remove(food)
                    # print(
                    #     "A food has been eaten! | Total Food on Screen = "
                    #     + str(len(self.food))
                    #     + " | Eater Color = "
                    #     + str(color)
                    # )
                    self.spawn_point(color)
            if collided_reds:
                for j in collided_reds:
                    if j.color != color:
                        size += 5
                        # print(
                        #     "A red has been eaten! | Total Reds on Screen = "
                        #     + str(len(self.reds))
                        #     + " | Eater Color = "
                        #     + str(color)
                        # )
                        self.reds.remove(j)
                        self.spawn_point(color)
            if collided_blues:
                for j in collided_blues:
                    if j.color != color:
                        size += 5
                        # print(
                        #     "A blue has been eaten!| Total Blues on Screen = "
                        #     + str(len(self.blues))
                        #     + " | Eater Color = "
                        #     + str(color)
                        # )
                        self.blues.remove(j)
                        self.spawn_point(color)
            if collided_greens:
                for j in collided_greens:
                    if j.color != color:
                        size += 5
                        # print(
                        #     "A green has been eaten!| Total Greens on Screen = "
                        #     + str(len(self.greens))
                        #     + " | Eater Color = "
                        #     + str(color)
                        # )
                        self.greens.remove(j)
                        self.spawn_point(color)

            point.my_own_update(x, y, size)
            return point

        self.reds = [move_point(p, False) for p in self.reds]
        self.blues = [move_point(p, False) for p in self.blues]
        self.greens = [move_point(p, False) for p in self.greens]
        self.player = [move_point(p, True) for p in self.player]
        # self.update_grid()

    def spawn_point(self, color):
        if color == RED:
            self.reds.append(
                Point(
                    random.randint(0, self.w - 1),
                    random.randint(0, self.h - 1),
                    10,
                    color,
                )
            )
        if color == GREEN:
            self.greens.append(
                Point(
                    random.randint(0, self.w - 1),
                    random.randint(0, self.h - 1),
                    10,
                    color,
                )
            )
        if color == BLUE:
            self.blues.append(
                Point(
                    random.randint(0, self.w - 1),
                    random.randint(0, self.h - 1),
                    10,
                    color,
                )
            )

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # elif event.type==pygame.KEYDOWN:
            #     if event.key==pygame.K_LEFT:
            #         self.player_direction=0
            #     elif event.key==pygame.K_RIGHT:
            #         self.player_direction=1
            #     elif event.key==pygame.K_DOWN:
            #         self.player_direction=2
            #     elif event.key==pygame.K_UP:
            #         self.player_direction=3
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_direction = 0
        elif keys[pygame.K_RIGHT]:
            self.player_direction = 1
        elif keys[pygame.K_DOWN]:
            self.player_direction = 2
        elif keys[pygame.K_UP]:
            self.player_direction = 3

        self.move_points()

        if self.iteration%500==0:
            print(self.get_state())

        self.clock.tick(240) 

        self.iteration=self.iteration+1
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
        for point in self.player:
            pygame.draw.rect(self.display, YELLOW, point)
        pygame.display.update()

    def get_state(self):
        point = self.player[0]

        nearest_food = self.find_nearest(point, game.food)
        nearest_enemy = self.find_nearest(point, game.reds + game.blues + game.greens)

        state = [
            # Normalized position of the player's point
            point.x / game.w,
            point.y / game.h,
            # Normalized direction to nearest food
            (nearest_food.x - point.x) / game.w if nearest_food else 0,
            (nearest_food.y - point.y) / game.h if nearest_food else 0,
            # Normalized direction to nearest enemy (regardless of color)
            (nearest_enemy.x - point.x) / game.w if nearest_enemy else 0,
            (nearest_enemy.y - point.y) / game.h if nearest_enemy else 0,
            # Danger in four directions (binary values)
            self.is_direction_dangerous(game, point, "left"),
            self.is_direction_dangerous(game, point, "right"),
            self.is_direction_dangerous(game, point, "up"),
            self.is_direction_dangerous(game, point, "down"),
        ]

        return np.array(state, dtype=float)

    def find_nearest(self, point, objects):
        if not objects:
            return None
        nearest = min(objects, key=lambda obj: self.distance(point, obj))
        return nearest

    def distance(self, point1, point2):
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

    def is_direction_dangerous(self, game, point, direction):
        x, y = point.x, point.y
        size = point.width/2
        if direction == "left":
            x -= size
        elif direction == "right":
            x += size
        elif direction == "up":
            y -= size
        elif direction == "down":
            y += size

        # Check if the new position would collide with any enemy
        for enemy in game.reds + game.blues + game.greens:
            if pygame.Rect(x, y, point.width, point.height).colliderect(enemy):
                return 1

        # Check if the new position is out of bounds
        # if x < 0 or x >= game.w or y < 0 or y >= game.h:
            # return 1

        return 0

if __name__ == "__main__":
    game = SnakeGame()
    # Game Loop
    while True:
        game.play_step()
