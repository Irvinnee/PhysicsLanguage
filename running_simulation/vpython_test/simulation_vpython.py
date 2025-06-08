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

    # Tworzenie kul dla każdej cząstki
    vparticles = {}
    for particle in system.particles.values():
        color_choice = vector.random()
        vparticles[particle] = sphere(pos=vector(*particle.position), radius=0.1, color=color_choice)

    # GUI
    t = 0.0
    playing = False

    time_display = wtext(text=f"Symulacja czasu: t = {t:.2f}\n")

    def update_particles():
        for particle in system.particles.values():
            particle.move_to_time(t)
        for particle, vsphere in vparticles.items():
            vsphere.pos = vector(*particle.position)
        time_display.text = f"Symulacja czasu: t = {t:.2f}\n"




    def on_slider_change():
        nonlocal t
        t = time_slider.value
        update_particles()

    def on_toggle():
        nonlocal playing
        playing = not playing
        toggle_button.text = "⏸️" if playing else "▶️"

    toggle_button = button(text="▶️", bind=on_toggle)
    scene.append_to_caption("  ")

    # Suwak czasu
    time_slider = slider(min=0, max=duration, value=0, step=delta, length=600, bind=lambda s: on_slider_change())


    update_particles()

    # Główna pętla odtwarzająca
    while True:
        rate(60)
        if playing:
            t += delta
            if t > duration:
                t = duration
                playing = False
                toggle_button.text = "▶️"
            time_slider.value = t
            scene.caption = f"Symulacja czasu: t = {t:.2f}"
            update_particles()
