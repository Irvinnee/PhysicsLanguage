import threading
from running_simulation.engine import System, Particle
# from running_simulation.graphics import GraphicsEngine
from typing import Callable, Dict, List, Optional, Union
import pygame
from OpenGL.GL import *

from running_simulation.visualisation_engine import Graphics


class Simulation:

    system: System
    graphics_engine: Graphics

    # particles_data: Dict[str, Particle]
    # time = 0.0
    max_time = 0.0
    #
    # # Lock do odbioru/zapisu danych
    # data_lock = threading.Lock()
    # time_lock = threading.Lock()

    # Silnik symulacji
    def simulation_engine(self):
        while True:
            with self.graphics_engine.time_lock:
                while abs(self.graphics_engine.sim_time*self.max_time - self.system.time) > 1:
                    if self.graphics_engine.sim_time*self.max_time - self.system.time > 0:
                        self.system.step(1)
                    else:
                        self.system.step(-1)

                    with self.graphics_engine.data_lock:
                        self.graphics_engine.particles = self.system.particles


                print(self.graphics_engine.sim_time*self.max_time)


    # Program graficzny
    def graphics(self):
        self.graphics_engine.run_simulation()

    def run(self, system:System, max_time):
        # Tworzenie wątków

        self.system = system
        self.particles_data = system.particles
        self.max_time = max_time

        # self.graphics_engine = Graphics(self.particles_data, self.data_lock, self.time, self.time_lock)
        self.graphics_engine = Graphics(self.particles_data)

        engine_thread = threading.Thread(target=self.simulation_engine)


        # Uruchomienie wątków
        engine_thread.start()
        # graphics_thread.start()
        self.graphics()

        # # Czekanie na zakończenie wątków
        engine_thread.join(5)
        # graphics_thread.join()
