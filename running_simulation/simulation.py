import threading
from time import sleep

from running_simulation.engine import System

from running_simulation.visualisation_engine import Graphics


class Simulation:

    system: System
    graphics_engine: Graphics

    # particles_data: Dict[str, Particle]
    # time = 0.0
    max_time = 0.0
    delta = 1
    #
    # # Lock do odbioru/zapisu danych
    # data_lock = threading.Lock()
    # time_lock = threading.Lock()

    def __init__(self, particles, delta_time):
        import copy
        self.particles = particles  # Dict[str, Particle]
        self.initial_state = copy.deepcopy(particles)
        self.delta_time = delta_time
        self.time = 0.0

    # Silnik symulacji
    def simulation_engine(self):
        while not self.stop_event.is_set():
            with self.graphics_engine.time_lock:
                while abs(self.graphics_engine.sim_time*self.max_time - self.system.time) > self.delta:
                    if self.graphics_engine.sim_time*self.max_time - self.system.time > 0:
                        self.system.step(self.delta)
                    else:
                        self.system.step(-self.delta)

                    with self.graphics_engine.data_lock:
                        self.graphics_engine.particles = self.system.particles


                # print(self.graphics_engine.sim_time*self.max_time)

            sleep(0.01)


    # Program graficzny
    def graphics(self):
        self.graphics_engine.run_simulation()

    def run(self, system:System, max_time, delta):
        # Tworzenie wątków

        self.system = system
        self.particles_data = system.particles
        self.max_time = max_time
        self.delta = delta
        self.stop_event = threading.Event()

        # self.graphics_engine = Graphics(self.particles_data, self.data_lock, self.time, self.time_lock)
        self.graphics_engine = Graphics(self.system.particles, self.stop_event, self.system)

        engine_thread = threading.Thread(target=self.simulation_engine)


        # Uruchomienie wątków
        engine_thread.start()
        # graphics_thread.start()
        self.graphics()
        self.stop_event.set()

        # # Czekanie na zakończenie wątków
        engine_thread.join(5)
        # graphics_thread.join()


        def reset(self):
            import copy
            self.particles = copy.deepcopy(self.initial_state)
            self.time = 0.0

        def step(self):
            # tutaj krok symulacji
            for p in self.particles.values():
                p.position += p.velocity * self.delta_time
                # itd...
            self.time += self.delta_time

        def simulate_to_time(self, target_time: float):
            self.reset()
            steps = int(target_time / self.delta_time)
            for _ in range(steps):
                self.step()

