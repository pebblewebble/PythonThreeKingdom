import pygame
import numpy as np
import random
from enum import Enum

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
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Three Kingdom")
        self.clock = pygame.time.Clock()

        self.grid = {}
        # self.update_grid()
        self.reset()

    def reset(self):
        self.player_direction = 0
        self.reward = 0
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
        # foodToAdd = int(((self.w * self.h) / 5) / 1000)
        foodToAdd=200
        self.foodCounter = 1
        for x in range(foodToAdd):
            self.foodCounter += 1
            # print("Added 1 food | Total Food on Screen = " + str(self.foodCounter))
            self.food.append(
                Point(
                    random.randint(0, self.w - 1),
                    random.randint(0, self.h - 1),
                    10,
                    WHITE,
                )
            )
        self.collision_count = 0
        self.frame_iteration = 0

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
                # movement_speed = 5
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
            for grid_point in (
                self.reds + self.greens + self.blues + self.food + self.player
            ):
                # We check for color logic here but there is another check below just in case i guess
                if (
                    new_point.colliderect(grid_point)
                    and grid_point != point
                    and grid_point.color != new_point.color
                ):
                    # print(grid_point.color, new_point.color)
                    # print("COLLIDED")
                    # self.collision_count = self.collision_count + 1
                    # print(self.collision_count)
                    if grid_point in self.food:
                        collided_food.append(grid_point)
                    elif grid_point in self.reds:
                        collided_reds.append(grid_point)
                    elif grid_point in self.greens:
                        collided_greens.append(grid_point)
                    elif grid_point in self.blues:
                        collided_blues.append(grid_point)
                    elif grid_point in self.player:
                        print(f"A {color} has eaten the player.")
                        collided_player.append(grid_point)
            if collided_player:
                for player in collided_player:
                    size += 5
                    self.player.remove(player)
                    self.spawn_point(color)
            if collided_food:
                # Keep the food that is not in the array that we just created
                for food in collided_food:
                    self.reward = self.reward + 5 if player else self.reward
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
                        self.reward = self.reward + 10 if player else self.reward
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
                        self.reward = self.reward + 10 if player else self.reward
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
                        self.reward = self.reward + 10 if player else self.reward
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

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        directions=[0,1,2,3]
        direction=directions[np.argmax(action)]
        self.player_direction = direction 
        self.move_points()

        # print(self.frame_iteration, 500*(self.reward+1))

        # If player is dead
        # if len(self.player)==0 or self.frame_iteration>1000*(self.reward+1):
        if len(self.player)==0:
            self.reward += -50
            return self.reward, True, self.reward

        self.update_ui()

        allDead=False

        if len(self.food)==0 and len(self.greens)==0 and len(self.blues)==0 and len(self.reds)==0:
            allDead=True

        if self.reward < 1000 and not allDead: 
            return self.reward, False, self.reward
        else:
            return self.reward, True, self.reward

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


# if __name__ == "__main__":
#     game = SnakeGame()
#     # Game Loop
#     while True:
#         game.play_step()
