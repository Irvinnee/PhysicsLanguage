import threading
from os import system
from time import sleep

from running_simulation.engine import System
from running_simulation.visualisation_engine import Graphics


class Simulation:

    system: System
    graphics_engine: Graphics
    max_time = 0.0
    delta = 1

    def __init__(self, particles, delta_time):
        import copy
        self.particles = particles
        self.initial_state = copy.deepcopy(particles)
        self.delta_time = delta_time
        self.time = 0.0
        self.total_time = 10.0

    # Silnik symulacji
    def simulation_engine(self):
        while not self.stop_event.is_set():
            with self.graphics_engine.time_lock:
                # print(self.time)
                # print(self.graphics_engine.history.keys())

                while abs(self.graphics_engine.sim_time * self.max_time - self.system.time) > self.delta:
                    if self.graphics_engine.sim_time * self.max_time - self.system.time > 0:
                        self.system.step(self.delta)
                        self.time += self.delta_time

                        with self.graphics_engine.data_lock:
                            self.graphics_engine.particles = self.system.particles
                            if self.time not in self.graphics_engine.history.keys():
                                self.graphics_engine.history[self.time] = {
                                    name: p.position[:] for name, p in self.graphics_engine.particles.items()
                                }
                    else:
                        break
                        # self.system.step(-self.delta)
                        # self.time -= self.delta_time

                    if  self.stop_event.is_set():
                        break


            sleep(0.01)

    # Program graficzny
    def graphics(self):
        self.graphics_engine.run_simulation()

    def run(self, system: System, max_time, delta):
        self.system = system
        self.particles_data = system.particles
        self.max_time = max_time
        self.delta = delta
        self.stop_event = threading.Event()

        self.graphics_engine = Graphics(self.system.particles, self.stop_event, self.system)

        engine_thread = threading.Thread(target=self.simulation_engine)
        engine_thread.start()

        self.graphics()
        self.stop_event.set()
        engine_thread.join(5)

    def reset(self):
        import copy
        self.particles = copy.deepcopy(self.initial_state)
        self.time = 0.0

    def step(self):
        print(self.time)
        print(self.graphics_engine.history)

        # for p in self.particles:
        #     for i in range(3):
        #         p.position[i] += p.velocity[i] * self.delta_time
        system.step(self.delta_time)
        self.time += self.delta_time

    def simulate_to_time(self, target_time: float):
        print(self.time)
        print(self.graphics_engine.history)

        self.reset()
        steps = int(target_time / self.delta_time)
        for _ in range(steps):
            self.step()