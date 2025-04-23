import threading
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import math
from running_simulation.engine import System, Particle
from typing import Callable, Dict, List, Optional, Union
import time
import random


# def  save_particle_state(particles):
#     return [copy.deepcopy(p) for p in particles]


class Graphics:
    particles : Dict[str, Particle] #with przy każdym zyskaniu, referencja do sim
    colors : Dict[Particle, tuple] = {}
    data_lock = threading.Lock()
    time_lock = threading.Lock()
    sim_time = 0.0

    camera_angle = [0, 0]
    camera_pos = [0, 0, -5]
    WIDTH, HEIGHT = 800, 600
    screen = None


    def __init__(self, particles):
        # self.data_lock = data_lock
        self.particles = particles
        # self.sim_time = sim_time
        # self.time_lock = time_lock


    def project_to_2d(self, x, y, z, camera_pos, camera_angle, fov=60, width=800, height=600):  # Zmniejszenie FOV
        pitch = camera_angle[0]
        yaw = camera_angle[1]
        cos_pitch = math.cos(math.radians(pitch))
        sin_pitch = math.sin(math.radians(pitch))
        cos_yaw = math.cos(math.radians(yaw))
        sin_yaw = math.sin(math.radians(yaw))

        dx = x - camera_pos[0]
        dy = y - camera_pos[1]
        dz = z - camera_pos[2]

        x_rot = cos_yaw * dx + sin_yaw * dz
        z_rot = -sin_yaw * dx + cos_yaw * dz

        y_rot = cos_pitch * dy - sin_pitch * z_rot
        z_rot = sin_pitch * dy + cos_pitch * z_rot

        aspect_ratio = width / height
        fov_rad = math.radians(fov)
        scale = math.tan(fov_rad / 2) * 2

        if z_rot == 0:
            return width // 2, height // 2  # Avoid division by zero

        x_2d = (x_rot / (z_rot * scale * aspect_ratio)) * (width / 2)
        y_2d = (-y_rot / (z_rot * scale)) * (height / 2)

        return x_2d + width / 2, y_2d + height / 2

    def draw_particles(self):
        for p in self.particles.values():

            x, y = self.project_to_2d(p.position[0], p.position[1], p.position[2], self.camera_pos, self.camera_angle)
            radius = max(int(p.mass * 5), 5)  # Zwiększenie rozmiaru cząsteczek
            if p not in self.colors.keys():
                self.colors[p] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pygame.draw.circle(self.screen, (0,0,255), (int(x), int(y)), radius)

    def handle_camera_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.camera_pos[2] += 0.1
        if keys[pygame.K_DOWN]:
            self.camera_pos[2] -= 0.1
        if keys[pygame.K_LEFT]:
            self.camera_pos[0] += 0.1
        if keys[pygame.K_RIGHT]:
            self.camera_pos[0] -= 0.1



    # Funkcja do rysowania estetycznego suwaka
    def draw_slider(self, slider_rect, value):
        # Gradient dla suwaka
        start_color = (0, 0, 255)  # Niebieski
        end_color = (255, 0, 0)    # Czerwony
        color = tuple([min(255, max(0, int(start_color[i] + (end_color[i] - start_color[i]) * value))) for i in range(3)])

        pygame.draw.rect(self.screen, (150, 150, 150), slider_rect)  # Tło suwaka
        pygame.draw.rect(self.screen, color, pygame.Rect(slider_rect.left + value - 5, slider_rect.top - 5, 10, slider_rect.height + 10))  # Suwak

    # Inicjalizacja Pygame
    def run_simulation(self):
        CENTER = (self.WIDTH // 2, self.HEIGHT // 2)

        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("3D Particle Viewer")

        # Inicjalizacja suwaka
        slider_rect = pygame.Rect(50, self.HEIGHT - 50, 700, 20)
        slider_value = 0  # Inicjalna wartość suwaka (czas)

        previous_slider_value = slider_value

        running = True
        start_time = time.time()
        prev_time = start_time

        # Pętla główna
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    if slider_rect.collidepoint(event.pos):
                        slider_value = (event.pos[0] - slider_rect.left) / slider_rect.width
                        slider_value = max(0, min(1, slider_value))  # Ograniczamy do zakresu [0, 1]

            self.handle_camera_movement()

            current_time = time.time()
            delta_time = current_time - prev_time  # Czas od ostatniej klatki
            prev_time = current_time

            # Jeśli suwak się zmienia, aktualizujemy stan cząsteczek
            if slider_value != previous_slider_value:
                previous_slider_value = slider_value

            with self.time_lock:
                self.sim_time = slider_value

            # Aktualizujemy pozycje cząsteczek na podstawie prędkości i upływającego czasu
            self.screen.fill((245, 245, 220))  # Tło
            with self.data_lock:
                self.draw_particles()

             # Rysowanie cząsteczek
            self.draw_slider(slider_rect, slider_value * slider_rect.width)  # Rysowanie suwaka
            pygame.display.flip()  # Aktualizowanie okna
            # print(self.camera_pos,"   a", self.camera_angle)
            pygame.time.Clock().tick(60)  # Ograniczenie liczby klatek na sekundę

        pygame.quit()
