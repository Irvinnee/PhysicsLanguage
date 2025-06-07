import threading
from os import environ
from platform import system

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
    stop_event: threading.Event
    system: Optional[System] = None

    camera_angle = [0, 0]
    camera_pos = [0, 0, -5]
    WIDTH, HEIGHT = 800, 600
    screen = None



    def __init__(self, particles, stop_event: threading.Event, system: System):
        self.particles = particles
        self.stop_event = stop_event
        self.system = system



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

            with self.time_lock:
                t = self.sim_time

            simulated_pos = p.position


            x, y = self.project_to_2d(simulated_pos[0], simulated_pos[1], simulated_pos[2], self.camera_pos,self.camera_angle)
            radius = max(int(p.mass * 5), 5)  # Zwiększenie rozmiaru cząsteczek
            if p not in self.colors.keys():
                self.colors[p] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pygame.draw.circle(self.screen, self.colors[p], (int(x), int(y)), radius)


    def handle_camera_movement(self):
        keys = pygame.key.get_pressed()
        move_speed = 0.1
        angle_speed = 1.5

        if keys[pygame.K_UP]:
            self.camera_pos[2] += move_speed
        if keys[pygame.K_DOWN]:
            self.camera_pos[2] -= move_speed
        if keys[pygame.K_LEFT]:
            self.camera_pos[0] += move_speed
        if keys[pygame.K_RIGHT]:
            self.camera_pos[0] -= move_speed
        if keys[pygame.K_SPACE]:
            self.camera_pos[1] += move_speed
        if keys[pygame.K_LSHIFT]:
            self.camera_pos[1] -= move_speed

        if keys[pygame.K_w]:
            self.camera_angle[0] += angle_speed
        if keys[pygame.K_s]:
            self.camera_angle[0] -= angle_speed
        if keys[pygame.K_a]:
            self. camera_angle[1] -= angle_speed
        if keys[pygame.K_d]:
            self.camera_angle[1] += angle_speed



    # Funkcja do rysowania estetycznego suwaka
    def draw_slider(self, slider_rect, value):
        start_color = (0, 0, 255)
        end_color = (255, 0, 0)
        color = tuple([
            min(255, max(0, int(start_color[i] + (end_color[i] - start_color[i]) * (value / slider_rect.width))))
            for i in range(3)
        ])

        pygame.draw.rect(self.screen, (150, 150, 150), slider_rect)
        handle_width = 20
        handle_x = int(slider_rect.left + value - handle_width / 2)
        handle_rect = pygame.Rect(handle_x, slider_rect.top - 5, handle_width, slider_rect.height + 10)
        pygame.draw.rect(self.screen, color, handle_rect, border_radius=4)

    # Inicjalizacja Pygame
    def run_simulation(self):
        CENTER = (self.WIDTH // 2, self.HEIGHT // 2)

        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("3D Particle Viewer")
        font = pygame.font.SysFont("Arial", 22, bold=True)

        # Wczytaj grafiki
        play_img = pygame.image.load("running_simulation/assets/play.png")
        pause_img = pygame.image.load("running_simulation/assets/pause.png")

        # Skaluj do wielkości przycisku
        icon_size = 40
        play_img = pygame.transform.smoothscale(play_img, (icon_size, icon_size))
        pause_img = pygame.transform.smoothscale(pause_img, (icon_size, icon_size))

        button_radius = 25
        button_center = (50 + button_radius, self.HEIGHT - 50 + button_radius // 2)
        is_playing = False

        running = True
        start_time = time.time()
        prev_time = start_time

        while running and not self.stop_event.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.stop_event.set()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()

                    # Obsługa kliknięcia przycisku ▶ / ⏸
                    dx = mx - button_center[0]
                    dy = my - button_center[1]
                    if dx * dx + dy * dy <= button_radius * button_radius:
                        is_playing = not is_playing
                    else:
                        # Sprawdź kliknięcie na cząstce
                        closest = None
                        closest_dist = 20
                        for p in self.particles.values():
                            sim_pos = p.position_at_time(self.sim_time)
                            px, py = self.project_to_2d(*sim_pos, self.camera_pos, self.camera_angle)
                            dist = math.hypot(mx - px, my - py)
                            if dist < closest_dist:
                                closest = p
                                closest_dist = dist
                        if closest:
                            print(f"Particle info: mass={closest.mass}, pos={closest.position}, vel={closest.velocity}")

            self.handle_camera_movement()

            current_time = time.time()
            delta_time = current_time - prev_time
            prev_time = current_time

            with self.time_lock:
                if is_playing:
                    self.system.step(delta_time)

            self.screen.fill((245, 245, 220))  # tło


            img = play_img if not is_playing else pause_img
            img_rect = img.get_rect(center=button_center)
            self.screen.blit(img, img_rect)

            with self.data_lock:
                self.draw_particles()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()

