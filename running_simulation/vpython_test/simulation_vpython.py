from vpython import *
from running_simulation.engine import System, Particle

def run_3d_visualization(system: System, duration: float, delta: float):
    # Konfiguracja sceny
    scene.title = "3D Particle Simulation"
    scene.width = 1200
    scene.height = 700
    scene.background = color.black
    scene.range = 5
    scene.fullscreen = False
    scene.autoscale = False
    scene.camera.pos = vector(4, 4, 4)
    scene.camera.axis = vector(-4, -4, -4)

    # Rysowanie osi XYZ
    def draw_axes(length=2.0, thickness=0.05, font_size=15):
        arrow(pos=vector(0, 0, 0), axis=vector(length, 0, 0), color=color.red, shaftwidth=thickness)
        label(pos=vector(length + 0.2, 0, 0), text='X', color=color.red, box=False, height=font_size)

        arrow(pos=vector(0, 0, 0), axis=vector(0, length, 0), color=color.green, shaftwidth=thickness)
        label(pos=vector(0, length + 0.2, 0), text='Y', color=color.green, box=False, height=font_size)

        arrow(pos=vector(0, 0, 0), axis=vector(0, 0, length), color=color.blue, shaftwidth=thickness)
        label(pos=vector(0, 0, length + 0.2), text='Z', color=color.blue, box=False, height=font_size)

    draw_axes()

    # Tworzenie kul reprezentujących cząstki
    vparticles = {}
    for particle in system.particles.values():
        color_choice = vector.random()
        vparticles[particle] = sphere(pos=vector(*particle.position), radius=0.1, color=color_choice)

    # Zmienne kontrolne
    t = 0.0
    playing = False

    # Interfejs tekstowy czasu
    scene.append_to_caption("\n")
    time_display = wtext(text=f"Symulacja czasu: t = {t:.2f}\n")

    # Pole do wpisywania kroku symulacji
    scene.append_to_caption(" Krok (s): ")
    step_input = winput(text=f"{delta:.2f}", width=60)
    scene.append_to_caption("\n")

    # Funkcja aktualizująca pozycje cząstek
    def update_particles():
        for particle in system.particles.values():
            particle.move_to_time(t)
        for particle, vsphere in vparticles.items():
            vsphere.pos = vector(*particle.position)
        time_display.text = f"Symulacja czasu: t = {t:.2f}\n"

    # Obsługa przycisków
    def on_play():
        nonlocal playing
        playing = True

    def on_pause():
        nonlocal playing
        playing = False

    def on_step_forward():
        nonlocal t
        try:
            step = float(step_input.text)
        except ValueError:
            step = delta
        t = min(t + step, duration)
        update_particles()

    def on_step_back():
        nonlocal t
        try:
            step = float(step_input.text)
        except ValueError:
            step = delta
        t = max(t - step, 0.0)
        update_particles()

    # Przyciski sterujące
    button(text="⏮️", bind=on_step_back)
    scene.append_to_caption(" ")
    button(text="▶️ Play", bind=on_play)
    scene.append_to_caption(" ")
    button(text="⏸️ Pause", bind=on_pause)
    scene.append_to_caption(" ")
    button(text="⏭️", bind=on_step_forward)
    scene.append_to_caption("\n\n")

    # Początkowa aktualizacja
    update_particles()

    # Główna pętla symulacji
    while True:
        rate(60)
        if playing:
            t += delta
            if t > duration:
                t = duration
                playing = False
            update_particles()
