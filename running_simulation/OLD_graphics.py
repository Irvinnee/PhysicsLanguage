import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import random

class GraphicsEngine:


    # Funkcja do rysowania kuli w przestrzeni 3D
    def draw_sphere(self, radius, position):
        slices = 20  # Liczba poziomych cięć
        stacks = 20  # Liczba pionowych cięć

        # Rysowanie kuli
        quadric = gluNewQuadric()
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])  # Przemieszczanie kuli na odpowiednią pozycję
        gluSphere(quadric, radius, slices, stacks)  # Rysowanie kuli
        glPopMatrix()

    # Funkcja do inicjalizacji okna Pygame i ustawienia OpenGL
    def init_gl(self, width, height):
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Tło okna (czarne)
        glEnable(GL_DEPTH_TEST)  # Włączenie testu głębokości (potrzebne do rysowania w 3D)
        gluPerspective(45, width / height, 0.1,
                       50.0)  # Perspektywa (kąt, stosunek wymiarów okna, minimalna i maksymalna odległość)
        glTranslatef(0.0, 0.0, -5)  # Ustawienie kamery w odpowiednim miejscu

