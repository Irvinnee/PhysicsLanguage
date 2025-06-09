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
    stop_event: threading.Event



    WIDTH, HEIGHT = 800, 600
    screen = None

    def __init__(self, particles, stop_event: threading.Event, system):
        self.particles = particles
        self.stop_event = stop_event
        self.system = system  # zapamiętaj system, jeśli potrzebujesz
        self.dragging_slider = False
        self.dragging_camera = False
        self.last_mouse_pos = None
        self.camera_angle = [35, -135]
        self.camera_pos = [50, 50, -50]
        self.light_pos = [0, 100, -100]


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
            radius = max(int(p.mass * 5), 5)

            if p not in self.colors:
                self.colors[p] = (
                    random.randint(200, 255),  # dużo czerwonego
                    random.randint(50, 100),  # trochę zieleni
                    random.randint(150, 255)  # fioletowy/niebieski ton
                )

            # Wektor z cząsteczki do światła
            lx = self.light_pos[0] - p.position[0]
            ly = self.light_pos[1] - p.position[1]
            lz = self.light_pos[2] - p.position[2]
            light_len = math.sqrt(lx ** 2 + ly ** 2 + lz ** 2)
            if light_len == 0:
                light_len = 1
            light_dir = (lx / light_len, ly / light_len, lz / light_len)

            # Normalna cząstki (tutaj uproszczenie: kierunek do kamery)
            nx = self.camera_pos[0] - p.position[0]
            ny = self.camera_pos[1] - p.position[1]
            nz = self.camera_pos[2] - p.position[2]
            norm_len = math.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
            if norm_len == 0:
                norm_len = 1
            normal = (nx / norm_len, ny / norm_len, nz / norm_len)

            # Iloczyn skalarny = intensywność światła
            dot = max(0, light_dir[0] * normal[0] + light_dir[1] * normal[1] + light_dir[2] * normal[2])
            intensity = 0.3 + 0.7 * dot  # zakres [0.3, 1.0]

            # Przeskaluj kolor
            r, g, b = self.colors[p]

            def shade_component(c, intensity):
                return int((c * intensity) + (30 * (1 - intensity)))  # cień = trochę czerni

            lit_color = (
                min(255, shade_component(r, intensity)),
                min(255, shade_component(g, intensity)),
                min(255, shade_component(b, intensity)),
            )

            pygame.draw.circle(self.screen, lit_color, (int(x), int(y)), radius)

    def handle_camera_movement(self):
        keys = pygame.key.get_pressed()
        move_speed = 1
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

        if self.camera_angle[1] > 180:
            self.camera_angle[1] -= 360
        elif self.camera_angle[1] < -180:
            self.camera_angle[1] += 360



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

    def draw_axes(self):
        axis_length = 50.0
        origin = (0, 0, 0)

        axes = {
            'X': ((axis_length, 0, 0), (255, 0, 0)),  # Red
            'Y': ((0, axis_length, 0), (0, 255, 0)),  # Green
            'Z': ((0, 0, -axis_length), (0, 0, 255))  # Blue
        }

        font = pygame.font.SysFont("Arial", 16, bold=True)

        for label, (endpoint, color) in axes.items():
            start_2d = self.project_to_2d(*origin, self.camera_pos, self.camera_angle)
            end_2d = self.project_to_2d(*endpoint, self.camera_pos, self.camera_angle)

            pygame.draw.line(self.screen, color, start_2d, end_2d, 3)

            # Draw arrowhead
            dx = end_2d[0] - start_2d[0]
            dy = end_2d[1] - start_2d[1]
            length = math.hypot(dx, dy)
            if length > 0:
                ux, uy = dx / length, dy / length
                perp = (-uy, ux)

                tip = (end_2d[0], end_2d[1])
                left = (tip[0] - ux * 10 + perp[0] * 5, tip[1] - uy * 10 + perp[1] * 5)
                right = (tip[0] - ux * 10 - perp[0] * 5, tip[1] - uy * 10 - perp[1] * 5)

                pygame.draw.polygon(self.screen, color, [tip, left, right])

            # Draw label
            label_surface = font.render(label, True, color)
            self.screen.blit(label_surface, (end_2d[0] + 5, end_2d[1] + 5))



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
        while running and not self.stop_event.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.stop_event.set()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # lewy przycisk myszy
                        if slider_rect.collidepoint(event.pos):
                            self.dragging_slider = True
                        else:
                            self.dragging_camera = True
                            self.last_mouse_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_slider = False
                        self.dragging_camera = False
                        self.last_mouse_pos = None

                elif event.type == pygame.MOUSEWHEEL:
                    self.camera_pos[2] += -event.y * 5  # przesuń kamerę wzdłuż osi Z


                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_slider:
                        slider_value = (event.pos[0] - slider_rect.left) / slider_rect.width
                        slider_value = max(0, min(1, slider_value))  # zakres [0, 1]


                    elif self.dragging_camera:
                        x, y = event.pos
                        last_x, last_y = self.last_mouse_pos
                        dx = x - last_x
                        dy = y - last_y
                        self.last_mouse_pos = event.pos

                        self.camera_angle[1] += dx * 0.2  # yaw
                        self.camera_angle[0] += dy * 0.2  # pitch
                        self.camera_angle[0] = max(-89, min(89, self.camera_angle[0]))  # ograniczenie pitch

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
                self.draw_axes()
                self.draw_particles()

             # Rysowanie cząsteczek
            self.draw_slider(slider_rect, slider_value * slider_rect.width)  # Rysowanie suwaka
            pygame.display.flip()  # Aktualizowanie okna
            # print(self.camera_pos,"   a", self.camera_angle)
            pygame.time.Clock().tick(60)  # Ograniczenie liczby klatek na sekundę

        pygame.quit()
