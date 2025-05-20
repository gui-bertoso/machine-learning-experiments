import threading
import time
import pygame
import random
import math
import os


pygame.init()

left_wall = 150
right_wall = 900
up_wall = 0
down_wall = 600

window = pygame.display.set_mode((right_wall, down_wall))

class Entity:
    def __init__(self, target_x, target_y, best_weights):
        self.target_x = target_x
        self.target_y = target_y
        self.weights = []
        self.weights_quantity = 64
        self.color = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
        self.position_x = 180
        self.position_y = 50
        self.velocity_x = 0
        self.velocity_y = 0

        if best_weights != []:
            self.weights = best_weights
            self.modify_weight()
        else:
            self.generate_weights()

    def process(self):
        i0 = left_wall - self.position_x
        i1 = right_wall - self.position_x
        i2 = up_wall - self.position_y
        i3 = down_wall - self.position_y
        i4 = self.target_x - self.position_x
        i5 = self.target_y - self.position_y
        i6 = self.velocity_x
        i7 = self.velocity_y

        rc0 = (i0 * self.weights[0] +
               i1 * self.weights[1] +
               i2 * self.weights[2] +
               i3 * self.weights[3] +
               i4 * self.weights[4] +
               i5 * self.weights[5] +
               i6 * self.weights[6] +
               i7 * self.weights[7]
        )
        rc1 = (i0 * self.weights[8] +
               i1 * self.weights[9] +
               i2 * self.weights[10] +
               i3 * self.weights[11] +
               i4 * self.weights[12] +
               i5 * self.weights[13] +
               i6 * self.weights[14] +
               i7 * self.weights[15]
        )
        rc2 = (i0 * self.weights[16] +
               i1 * self.weights[17] +
               i2 * self.weights[18] +
               i3 * self.weights[19] +
               i4 * self.weights[20] +
               i5 * self.weights[21] +
               i6 * self.weights[22] +
               i7 * self.weights[23]
        )
        rc3 = (i0 * self.weights[24] +
               i1 * self.weights[25] +
               i2 * self.weights[26] +
               i3 * self.weights[27] +
               i4 * self.weights[28] +
               i5 * self.weights[29] +
               i6 * self.weights[30] +
               i7 * self.weights[31]
        )
        rc4 = (i0 * self.weights[32] +
               i1 * self.weights[33] +
               i2 * self.weights[34] +
               i3 * self.weights[35] +
               i4 * self.weights[36] +
               i5 * self.weights[37] +
               i6 * self.weights[38] +
               i7 * self.weights[39]
        )

        r0 = (rc0 * self.weights[40] +
              rc1 * self.weights[41] +
              rc2 * self.weights[42] +
              rc3 * self.weights[43] +
              rc4 * self.weights[44]
        )
        r1 = (rc0 * self.weights[45] +
              rc1 * self.weights[46] +
              rc2 * self.weights[47] +
              rc3 * self.weights[48] +
              rc4 * self.weights[49]
        )
        r2 = (rc0 * self.weights[50] +
              rc1 * self.weights[51] +
              rc2 * self.weights[52] +
              rc3 * self.weights[53] +
              rc4 * self.weights[54]
        )
        r3 = (rc0 * self.weights[55] +
              rc1 * self.weights[56] +
              rc2 * self.weights[57] +
              rc3 * self.weights[58] +
              rc4 * self.weights[59]
        )

        if (r0 * self.weights[60]) > 0:
            self.velocity_x += 0.001
        if (r1 * self.weights[61]) > 0:
            self.velocity_x -= 0.001
        if (r2 * self.weights[62]) > 0:
            self.velocity_y += 0.001
        if (r3 * self.weights[63]) > 0:
            self.velocity_y -= 0.001

    def physics_process(self):
        self.position_x += self.velocity_x
        self.position_y += self.velocity_y

    def render(self):
        pygame.draw.circle(window, self.color, (self.position_x, self.position_y), 20)

    def generate_weights(self):
        for weight in range(self.weights_quantity):
            self.weights.append(random.randint(-1000, 1000))
    def modify_weight(self):
        for weight in self.weights:
            weight += random.randint(-100, 100)
    def minimum_modify_weight(self):
        for weight in self.weights:
            weight += random.randint(-10, 10)


class Simulation:
    def __init__(self):
        os.system("cls")
        print("Initializing")
        time.sleep(0.2)
        self.entitys_quantity = 3000
        self.entitys = []
        self.process_thread = None
        self.physics_process_thread = None
        self.generation = 0
        self.running = True
        self.target_x = 800
        self.target_y = 500
        self.lifetime = 5.0
        self.best_weights = []
        self.best_distance = 1000
        os.system("cls")
        print("Initializing.")
        time.sleep(0.2)

        self.generate_entitys()
        os.system("cls")
        print("Initializing..")
        time.sleep(0.2)
        self.start_threads()

    def generate_entitys(self):
        self.generation += 1
        for entity in range(self.entitys_quantity):
            self.entitys.append(Entity(self.target_x, self.target_y, self.best_weights))

    def start_threads(self):
        self.process_thread = threading.Thread(target=self.process_function)
        self.physics_process_thread = threading.Thread(target=self.physics_process_function)
        self.process_thread.start()
        self.physics_process_thread.start()
        self.render_function()

    def physics_process_function(self):
        while self.running:
            for entity in self.entitys:
                entity.physics_process()

    def render_function(self):
        while self.running:
            positions = []
            window.fill((0, 0, 0))
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
            for entity in self.entitys:
                if not (entity.position_x, entity.position_y) in positions:
                    positions.append((entity.position_x, entity.position_y))
                    entity.render()
            self.draw_hud()
            pygame.display.flip()
        pygame.quit()
        self.physics_process_thread.join()
        self.process_thread.join()

    def process_function(self):
        while self.running:
            for entity in self.entitys:
                entity.process()
                if right_wall < entity.position_x > left_wall or down_wall < entity.position_y > up_wall:
                    try:
                        self.entitys.remove(entity)
                    except ValueError:
                        pass
                else:
                    distance = math.sqrt((self.target_x+20 - entity.position_x) ** 2 + (self.target_y+20 - entity.position_y) ** 2)
                    if distance < self.best_distance:
                        self.best_weights = entity.weights
                        self.best_distance = distance
                        if distance < 40:
                            self.target_x = random.randint(left_wall, right_wall)
                            self.target_y = random.randint(up_wall, down_wall)
                            self.entitys = []
                            self.lifetime = 5.0
                            self.generate_entitys()
            self.lifetime -= 0.001
            if len(self.entitys) < 1 or self.lifetime <= 0:
                self.entitys = []
                self.lifetime = 5.0
                self.generate_entitys()

    def draw_hud(self):
        pygame.draw.circle(window, (255, 0, 0), (self.target_x, self.target_y), 20)
        pygame.draw.rect(window, (80, 80, 80), (0, 0, 150, down_wall))
        font = pygame.font.SysFont("Arial", 14)
        text = font.render("GENERATION: " + str(self.generation), True, (255, 255, 255))
        window.blit(text, (10, 10))

if __name__ == "__main__":
    Simulation()
