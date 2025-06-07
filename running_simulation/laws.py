from running_simulation.engine import Particle, System
from running_simulation.engine import Law


def gravity_law(p: Particle, system: System, dt: float):
    """
    Dodaje siłę grawitacji działającą na cząstkę w kierunku -Y.
    """
    g = -9.81  # m/s^2
    force = [0.0, g * p.mass, 0.0]
    p.apply_force(force)


def air_resistance_law(p: Particle, system: System, dt: float):
    """
    Prosty model oporu powietrza (siła przeciwdziałająca ruchowi).
    """
    drag_coefficient = 0.1
    drag = [-v * drag_coefficient for v in p.velocity]
    p.apply_force(drag)


# Przykład rejestracji w run_phys.py:
#
# from laws import gravity_law, air_resistance_law
# from running_simulation.engine.law import Law
#
# system.register_law(Law(fn=gravity_law, scope="global", target="particle"))
# system.register_law(Law(fn=air_resistance_law, scope="global", target="particle"))
