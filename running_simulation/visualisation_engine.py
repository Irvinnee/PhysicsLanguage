import threading
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import math
from running_simulation.engine import System, Particle
from typing import Callable, Dict, List, Optional, Union
import time
import random


class Graphics:
    particles : Dict[str, Particle]
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
        self.camera_angle = [-40, 45]
        self.camera_pos = [20, 20, -20]
        self.light_pos = [-100, 100, -100]
        self.auto_rotate = False
        self.orbit_radius = 80
        self.input_active = False
        self.input_text = ""
        self.input_box = pygame.Rect(600, 20, 150, 35)
        self.time_limit = system.total_time
        self.history = {}

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
        particles_with_depth = []

        for p in self.particles.values():
            dx = p.position[0] - self.camera_pos[0]
            dy = p.position[1] - self.camera_pos[1]
            dz = p.position[2] - self.camera_pos[2]

            pitch = math.radians(self.camera_angle[0])
            yaw = math.radians(self.camera_angle[1])
            cos_pitch = math.cos(pitch)
            sin_pitch = math.sin(pitch)
            cos_yaw = math.cos(yaw)
            sin_yaw = math.sin(yaw)

            x_rot = cos_yaw * dx + sin_yaw * dz
            z_rot = -sin_yaw * dx + cos_yaw * dz
            y_rot = cos_pitch * dy - sin_pitch * z_rot
            depth = sin_pitch * dy + cos_pitch * z_rot

            particles_with_depth.append((depth, p))

        particles_with_depth.sort(reverse=True, key=lambda item: item[0])

        for _, p in particles_with_depth:
            x, y = self.project_to_2d(p.position[0], p.position[1], p.position[2], self.camera_pos, self.camera_angle)
            radius = max(int(p.mass * 5), 5)

            if p not in self.colors:
                self.colors[p] = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )

            # Światło
            lx = self.light_pos[0] - p.position[0]
            ly = self.light_pos[1] - p.position[1]
            lz = self.light_pos[2] - p.position[2]
            light_len = math.sqrt(lx ** 2 + ly ** 2 + lz ** 2) or 1
            light_dir = (lx / light_len, ly / light_len, lz / light_len)

            # Normalna (kierunek do kamery)
            nx = self.camera_pos[0] - p.position[0]
            ny = self.camera_pos[1] - p.position[1]
            nz = self.camera_pos[2] - p.position[2]
            norm_len = math.sqrt(nx ** 2 + ny ** 2 + nz ** 2) or 1
            normal = (nx / norm_len, ny / norm_len, nz / norm_len)

            # Iloczyn skalarny = siła światła padającego na kulkę
            dot = max(0, light_dir[0] * normal[0] + light_dir[1] * normal[1] + light_dir[2] * normal[2])
            intensity = 0.3 + 0.9 * dot  # Zakres od 0.3 (ciemno) do 1.0 (jasno)

            r, g, b = self.colors[p]

            def shade(c, i):
                return int(c * i + 30 * (1 - i))  # ciemniejszy cień bez rzucanego cienia

            lit_color = (
                min(255, shade(r, intensity)),
                min(255, shade(g, intensity)),
                min(255, shade(b, intensity)),
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

        if self.auto_rotate:
            self.camera_angle[1] += 0.2
            if self.camera_angle[1] > 180:
                self.camera_angle[1] -= 360

            # NIE ZMIENIAMY PITCH – tylko pozycję XY w poziomie
            angle_rad = math.radians(self.camera_angle[1])

            self.camera_pos[0] = math.sin(angle_rad) * self.orbit_radius
            self.camera_pos[2] = math.cos(angle_rad) * self.orbit_radius

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

    def update_camera_angle_towards_center(self):
        dx = self.orbit_center[0] - self.camera_pos[0]
        dy = self.orbit_center[1] - self.camera_pos[1]
        dz = self.orbit_center[2] - self.camera_pos[2]

        distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        if distance == 0:
            return

        pitch = math.degrees(math.asin(dy / distance))
        yaw = math.degrees(math.atan2(dx, dz))

        self.camera_angle[0] = pitch
        self.camera_angle[1] = yaw

    def draw_axes(self):
        axis_length = 20.0
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




    def run_simulation(self):
        CENTER = (self.WIDTH // 2, self.HEIGHT // 2)

        pygame.init()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("3D Particle Viewer")

        slider_rect = pygame.Rect(50, self.HEIGHT - 50, 700, 20)
        slider_value = 0
        previous_slider_value = slider_value

        running = True
        start_time = time.time()
        prev_time = start_time

        while running and not self.stop_event.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.stop_event.set()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.input_active = True
                    else:
                        self.input_active = False

                    if event.button == 1:
                        if slider_rect.collidepoint(event.pos):
                            self.dragging_slider = True
                            mouse_x, _ = event.pos
                            slider_value = (mouse_x - slider_rect.left) / slider_rect.width
                            slider_value = max(0, min(1, slider_value))
                        else:
                            self.dragging_camera = True
                            self.last_mouse_pos = event.pos


                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_slider = False
                        self.dragging_camera = False
                        self.last_mouse_pos = None

                elif event.type == pygame.MOUSEWHEEL:
                    self.camera_pos[2] += -event.y * 5

                elif self.dragging_camera:
                    x, y = event.pos
                    last_x, last_y = self.last_mouse_pos
                    dx = x - last_x
                    dy = y - last_y
                    self.last_mouse_pos = event.pos

                    self.camera_angle[1] += dx * 0.3
                    self.camera_angle[0] -= dy * 0.3
                    self.camera_angle[0] = max(-89, min(89, self.camera_angle[0]))

                    # Oblicz nową pozycję kamery na sferze
                    pitch_rad = math.radians(self.camera_angle[0])
                    yaw_rad = math.radians(self.camera_angle[1])

                    self.camera_pos[0] = math.cos(pitch_rad) * math.sin(yaw_rad) * self.orbit_radius
                    self.camera_pos[1] = math.sin(pitch_rad) * self.orbit_radius
                    self.camera_pos[2] = math.cos(pitch_rad) * math.cos(yaw_rad) * self.orbit_radius


                elif event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            try:
                                entered_time = float(self.input_text.replace(",", "."))
                                current_time = self.sim_time * self.system.total_time

                                # Jeśli wpisano wartość ujemną, to potraktuj ją jako przesunięcie względem aktualnego czasu
                                if entered_time < 0 or entered_time > self.system.total_time:
                                    target_time = current_time + entered_time
                                else:
                                    target_time = entered_time

                                # Przytnij do zakresu [0, total_time]
                                target_time = max(0.0, min(target_time, self.system.total_time))

                                slider_value = target_time / self.system.total_time

                                with self.time_lock:
                                    self.sim_time = slider_value
                                    sim_timestamp = round(self.sim_time * self.system.total_time, 2)
                                    if sim_timestamp in self.history:
                                        with self.data_lock:
                                            for name, pos in self.history[sim_timestamp].items():
                                                if name in self.particles:
                                                    self.particles[name].position = pos[:]

                                previous_slider_value = slider_value

                            except:
                                pass
                            self.input_text = ""
                            self.input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            if len(self.input_text) < 10:
                                self.input_text += event.unicode
                    else:
                        if event.key == pygame.K_r:
                            self.auto_rotate = not self.auto_rotate

                elif self.dragging_slider and pygame.mouse.get_pressed()[0]:
                    mouse_x, _ = pygame.mouse.get_pos()
                    slider_value = (mouse_x - slider_rect.left) / slider_rect.width
                    slider_value = max(0, min(1, slider_value))

            self.handle_camera_movement()

            current_time = time.time()
            delta_time = current_time - prev_time
            prev_time = current_time

            sim_timestamp = round(self.sim_time * self.system.total_time, 2)
            with self.data_lock:
                if sim_timestamp not in self.history:
                    self.history[sim_timestamp] = {
                        name: p.position[:] for name, p in self.particles.items()
                    }
                    # print(f"[HISTORY] Zapamiętano stan w t={sim_timestamp:.2f}s")

            if slider_value != previous_slider_value:
                previous_slider_value = slider_value

            with self.time_lock:
                self.sim_time = slider_value
                sim_timestamp = round(self.sim_time * self.system.total_time, 2)
                if sim_timestamp in self.history:
                    with self.data_lock:
                        for name, pos in self.history[sim_timestamp].items():
                            if name in self.particles:
                                self.particles[name].position = pos[:]

            self.screen.fill((160, 160, 160))
            with self.data_lock:
                self.draw_axes()
                self.draw_particles()

            self.draw_slider(slider_rect, slider_value * slider_rect.width)

            pygame.draw.rect(self.screen, (255, 255, 255), self.input_box)
            pygame.draw.rect(self.screen, (0, 0, 0), self.input_box, 2)

            if self.input_active:
                display_text = self.input_text
            else:
                display_text = "" if self.input_text else "Go to t..."

            color = (0, 0, 0) if self.input_active or self.input_text else (100, 100, 100)
            text_surface = self.font.render(display_text, True, color)
            self.screen.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()