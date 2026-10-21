import os

from enums import Window
from nodes.graph_node import GraphNode
from nodes.loading_bar import LoadingBar
from nodes.simulated_entity import SimulatedEntity
from nodes.target import Target

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import logging
logging.basicConfig(level=logging.FATAL)

import multiprocessing
import random
import pygame
import threading
import platform
import psutil
#import wmi
import subprocess
import re
import enum
import datetime
import sys

TOP_LIMIT = 0
BOTTOM_LIMIT = 720
LEFT_LIMIT = 0
RIGHT_LIMIT = 1280
PROCESS_FPS_LIMIT = 1000
RENDER_FPS_LIMIT = 60

DELTA_TIME = 0

NODES_RAM_USAGE = 0
NODES_COUNT = 0


class App:
    def __init__(self):
        print("[CORE] starting app...")

        print("     [!] settings up variables")
        self.cpu_count = 0
        self.cpu_name = ""

        self.gpu_name = ""
        self.gpu_count = 0
        self.gpu_id = 0
        self.gpu_renderer = ""
        self.gpu_video_memory = 0

        self.memory_amount = 0

        self.os_name = ""
        self.os_arch = ""

        print("     [!] initializing pygame")

        pygame.init()
        pygame.font.init()

        print("     [!] initializing window")

        self.current_screen = Window.Loading

        self.window_height = 720
        self.window_width = 1280
        self.loading_window_height = 300
        self.loading_window_width = 560

        self.window = pygame.display.set_mode((self.loading_window_width, self.loading_window_height))
        pygame.display.set_caption("ml experiments v2")

        self.loading_bar = LoadingBar(window=self.window)
        self.loading_bar.size.x = self.loading_window_width
        self.loading_bar.value = 0
        self.loading_bar.size.y = 10
        self.loading_bar.position.y = self.loading_window_height - 30
        self.loading_bar.position.x = 0
        self.loading_bar.base_color = (20, 20, 20)
        self.loading_bar.fill_color = (0, 255, 0)

        print("     [!] setting up fonts")

        self.loading_title_font = pygame.font.SysFont("Arial", 35)
        self.loading_main_font = pygame.font.SysFont("Arial", 35)
        self.title_font = pygame.font.SysFont("Arial", 20)
        self.main_font = pygame.font.SysFont("Arial", 14)

        print("     [!] creating hud items")

        self.lifetime_graph = GraphNode(window=self.window)
        self.lifetime_graph.position.x = 10
        self.lifetime_graph.position.y = 250
        self.lifetime_graph.size.x = 180
        self.lifetime_graph.size.y = 180
        self.lifetime_graph.max_points = 180
        self.lifetime_graph.line_color = (255, 0, 0)

        self.pontuations_graph = GraphNode(window=self.window)
        self.pontuations_graph.position.x = 10
        self.pontuations_graph.position.y = 470
        self.pontuations_graph.size.x = 180
        self.pontuations_graph.size.y = 180
        self.pontuations_graph.max_points = 180
        self.pontuations_graph.line_color = (255, 255, 0)

        print("     [!] creating target")

        self.target = Target(window=self.window)
        self.target.position.x = 600
        self.target.position.y = 200

        print("     [!] settings first gen variables")

        self.doom_timer = 1000.0
        self.pontuations = {}
        self.current_generation = 0
        self.entities = []
        self.entities_per_generation = 100
        self.entities_alive = 0
        self.current_generation = -1
        self.initial_generation_position = pygame.math.Vector2(300, 40)
        self.best_of_all_entities_pontuation = 0
        self.best_tree_all_entities_weights = [[], [], []]

        #self.get_initial_data()

        print("     [!] creating simulated entities")

        self.spawn_generation()

        print("     [!] creating event triggers")

        self.close_event = threading.Event()

        print("     [!] creating clocks")

        self.render_clock = pygame.time.Clock()
        self.process_clock = pygame.time.Clock()

        self.generation_lifetime = 0.0

        print("     [!] starting render thread")

        self.close_event = threading.Event()

        self.render_thread = threading.Thread(target=self.render_core)
        self.render_thread.start()

        print("     [!] starting process thread")

        #print("     [!] generations loop initiated")
        self.process_core()

        print("     [!] quiting operations")
        if self.render_thread.is_alive():
            self.render_thread.join()
        pygame.quit()
        exit()

    def render_core(self):
        while not self.close_event.is_set():
            self.render_clock.tick(RENDER_FPS_LIMIT)
            self.window.fill((0, 0, 0))

            match self.current_screen:
                case Window.Loading:
                    self.draw_loading_window()

                case Window.Main:
                    for e in self.entities[:]:
                        e.draw()

                    self.target.draw()
                    self.draw_hud()
            pygame.display.flip()

    def draw_loading_window(self):
        global DELTA_TIME

        text = self.loading_main_font.render("Hi, working in some thinks for start", True, (255, 255, 255))
        self.window.blit(text, (10, 10))

        self.loading_bar.value += 0.1*DELTA_TIME
        self.loading_bar.draw()

    def process_core(self):
        global DELTA_TIME

        while not self.close_event.is_set():
            dt = self.process_clock.tick(PROCESS_FPS_LIMIT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_event.set()

            match self.current_screen:
                case Window.Loading:
                    pass
                case Window.Main:
                    self.doom_timer -= dt

                    for e in self.entities[:]:
                        e.update()

                        self.verify_entity(e)

                    self.target.update()
                    self.entityes_alive = len(self.entities)

                    self.generation_lifetime += dt

                    if self.doom_timer <= 0.0 or self.entities_alive <= 0:
                        for e in self.entities[:]:
                            e.controller.pontuation *= 0.8
                            self.registry_entity_pontuation(e)

                        self.lifetime_graph.add_value(self.generation_lifetime)
                        self.get_best_of_all_entities()
                        self.pontuations_graph.add_value(self.best_of_all_entities_pontuation)
                        self.spawn_generation()
            DELTA_TIME = dt

    def verify_entity(self, entity:SimulatedEntity):
        if entity.position.x < LEFT_LIMIT or entity.position.x > RIGHT_LIMIT or entity.position.y < TOP_LIMIT or entity.position.y > BOTTOM_LIMIT:
            self.registry_entity_pontuation(entity)
            self.entities.remove(entity)

    def registry_entity_pontuation(self, entity:SimulatedEntity):
        self.pontuations[self.current_generation].append([entity.controller.pontuation, entity.controller.weights])

    def get_best_of_all_entities(self):
        all_entities = self.pontuations.get(self.current_generation)
        if not all_entities:
            all_entities = self.pontuations.get(self.current_generation-1)
            if not all_entities:
                all_entities = self.pontuations.get(self.current_generation-2)

        all_entities.sort(key=lambda x: x[0], reverse=True)
        best_pontuation = all_entities[0]
        self.best_of_all_entities_pontuation = best_pontuation[0]
        self.best_tree_all_entities_weights[0] = all_entities[0][1].copy()
        self.best_tree_all_entities_weights[1] = all_entities[1][1].copy()
        self.best_tree_all_entities_weights[2] = all_entities[2][1].copy()

    def draw_hud(self):
        pygame.draw.rect(self.window, (50, 50, 50), pygame.Rect(0, 0, 200, 720))

        text = self.title_font.render("Debug panel", True, (255, 255, 255))
        self.window.blit(text, (20, 20))
        text = self.main_font.render(f"Render FPS: {int(self.render_clock.get_fps())}", True, (255, 255, 255))
        self.window.blit(text, (20, 50))
        text = self.main_font.render(f"Process FPS: {int(self.process_clock.get_fps())}", True, (255, 255, 255))
        self.window.blit(text, (20, 70))
        text = self.main_font.render(f"delta: {DELTA_TIME}ms", True, (255, 255, 255))
        self.window.blit(text, (20, 90))
        text = self.main_font.render(f"Frametime: {self.process_clock.get_time()}ms", True, (255, 255, 255))
        self.window.blit(text, (20, 110))
        text = self.main_font.render(f"Entityes: {self.entities_per_generation}/{self.entities_alive}", True, (255, 255, 255))
        self.window.blit(text, (20, 130))
        text = self.main_font.render(f"Timeout: {self.doom_timer}", True, (255, 255, 255))
        self.window.blit(text, (20, 150))
        text = self.main_font.render(f"Generation: {self.current_generation}", True, (255, 255, 255))
        self.window.blit(text, (20, 170))
        text = self.main_font.render(f"Best Pontuation: {int(self.best_of_all_entities_pontuation)}", True, (255, 255, 255))
        self.window.blit(text, (20, 190))

        text = self.main_font.render("lifetime graph", True, (255, 255, 255))
        self.window.blit(text, (20, 230))
        self.lifetime_graph.draw()
        text = self.main_font.render("pontuation graph", True, (255, 255, 255))
        self.window.blit(text, (20, 450))
        self.pontuations_graph.draw()

        text = self.main_font.render(f"Memory Usage: {self.get_used_memory()} GB", True, (255, 255, 255))
        self.window.blit(text, (20, 600))

    def spawn_generation(self):
        self.entities.clear()
        self.current_generation += 1
        self.doom_timer = 1000.0
        self.generation_lifetime = 0.0
        self.pontuations[self.current_generation] = []

        if self.current_generation > 0:
            for i in range(self.entities_per_generation):
                e = SimulatedEntity(window=self.window, target=self.target, best_weights=self.best_tree_all_entities_weights[random.randint(0, len(self.best_tree_all_entities_weights) - 1)])
                e.position = self.initial_generation_position.copy()
                self.entities.append(e)
        else:
            for i in range(self.entities_per_generation):
                e = SimulatedEntity(window=self.window, target=self.target)
                e.position = self.initial_generation_position.copy()
                self.entities.append(e)
        print(f"         [+] new generation created {self.current_generation} -> {datetime.datetime.now()}")


    @staticmethod
    async def get_gpu_video_memory():
        print(f"         [+] getting gpu vram")
        try:
            print(f"             [+] creating temp file")
            temp_file = os.path.join(os.environ["TEMP"], "dx_vram_report.xml")

            print(f"             [+] starting subprocess")
            subprocess.run(["dxdiag", "/x", temp_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=True)

            print(f"             [+] verifyng temp file")
            if os.path.exists(temp_file):

                print(f"             [+] opening temp file")
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                print(f"             [+] deleting temp file")
                os.remove(temp_file)

                print(f"             [+] reading temp file data")
                memory_mb = re.findall(r"<DedicatedMemory>(.*?)</DedicatedMemory>", content)

                much_vram = 0
                for mem_text in memory_mb:
                    numbers = "".join(filter(str.isdigit, mem_text))
                    if numbers:
                        vram_gb = round(int(numbers) / 1024)
                        if vram_gb > much_vram:
                            much_vram = vram_gb

                if much_vram > 0:
                    return much_vram

        except Exception as e:
            print(e)

        return 0

    def get_used_memory(self):
        print(f"         [+] getting used memory")
        try:
            used_memory = round(psutil.virtual_memory().used / (1024 ** 3))
            return used_memory
        except Exception as e:
            print(e)
        return 0

    async def get_initial_data(self):
        print("     [!] getting hardware info")

        print(f"         [+] getting CPU info")

        self.cpu_count = multiprocessing.cpu_count()
        self.cpu_name = platform.processor()

        print("             [+] " + str(self.cpu_count) + " Cores")
        print("             [+] " + self.cpu_name)


        print(f"         [+] getting OS info")

        self.os_name = platform.system()
        self.os_arch = platform.machine()

        print("             [+] " + self.os_name)
        print("             [+] " + self.os_arch)


        print(f"         [+] getting RAM info")

        self.memory_amount = round(psutil.virtual_memory().total / (1024 ** 3))

        print("             [+] " + str(self.memory_amount) + " GB")

        print(f"         [+] getting GPU info")

        print(f"             [+] creating WMI computer")
        #computer = wmi.WMI()
        #print(f"                 [+] computer created -> {computer}")

        #gpus = computer.Win32_VideoController()
        #self.gpu_count = len(gpus)

        #gpu = gpus[0]

        #self.gpu_name = gpu.name

        self.gpu_video_memory = self.get_gpu_video_memory()

        print("                 [+] " + str(self.gpu_count) + " GPUs")
        print("                 [+] " + self.gpu_name)
        print("                 [+] " + str(self.gpu_video_memory) + " GB")


if __name__ == "__main__":
    App()