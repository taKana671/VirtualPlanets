import math

import numpy as np
from panda3d.core import NodePath, PandaNode
from panda3d.core import Point3, Vec3, LRotation
from panda3d.core import TransparencyAttrib
from panda3d.core import Shader

from shapes import EllipticalPrism, Particles


class Planet(NodePath):

    def __init__(self, name, speed, scale, orbit):
        super().__init__(PandaNode(name))
        self.directional_nd = NodePath('directional_nd')
        self.directional_nd.reparent_to(self)

        self.model = base.loader.load_model(f'models/{name}.bam')
        self.model.reparent_to(self.directional_nd)
        self.set_scale(scale)

        self.orbit = orbit
        self.speed = speed
        self.angle = 0

    def get_size(self):
        end, tip = self.model.getTightBounds()
        size = tip - end
        return size

    def update(self, dt):
        if self.angle > math.tau:
            self.angle -= math.tau

        seed_multiplier = 1.0 / (1.0 + self.orbit.eccentricity * math.cos(self.angle))
        self.angle += self.speed * seed_multiplier * dt

        x = math.cos(self.angle) * self.orbit.rx
        y = math.sin(self.angle) * self.orbit.ry
        pos = Vec3(x, y, 0)
        tilt_rot = LRotation(*self.orbit.tilt)
        tilted_pos = tilt_rot.xform(pos)
        final_pos = self.orbit.center + tilted_pos
        self.set_pos(final_pos)

        hpr = Vec3(self.directional_nd.get_h() + 50 * dt, 0, 0)
        self.directional_nd.set_hpr(hpr)


class OrbitLine(NodePath):

    def __init__(self, orbit, thickness=0.02, height=0.02):
        super().__init__(PandaNode(f'{orbit.planet_name}_orbit'))

        orbit_line = EllipticalPrism(
            major_axis=orbit.major_axis,
            minor_axis=orbit.minor_axis,
            thickness=thickness,
            height=height
        ).create()

        orbit_line.reparent_to(self)
        self.set_hpr(orbit.tilt)


class ParticleRing(NodePath):

    def __init__(self, ring, planet):
        super().__init__(PandaNode(f'{ring.planet_name}_ring'))
        ring_model = self.create_particles(planet, ring.thickness, ring.particle_cnt)
        ring_model.reparent_to(self)
        self.set_render_mode_thickness(ring.particle_size)
        self.set_color(ring.color)
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.set_hpr(ring.hpr)

    def create_particles(self, planet, ring_thickness, n):
        # Get the approximate radius.
        size = planet.get_size()
        min_r = int(size.x / 2) + 1
        max_r = min_r + ring_thickness
        center = Point3(0)

        theta = np.random.uniform(0, 2 * np.pi, n)
        r = np.random.uniform(min_r, max_r, n)
        x = center.x + r * np.cos(theta)
        y = center.y + r * np.sin(theta)

        vertices = np.column_stack((x, y))
        vertices = np.c_[vertices, np.zeros(n)]

        particles = Particles(vertices.flatten()).create()
        return particles


class Atmosphere(NodePath):

    def __init__(self, atm):
        super().__init__(PandaNode(f'{atm.planet_name}_atmosphere'))
        model = base.loader.load_model('models/sphere.bam')
        model.reparent_to(self)
        self.set_hpr_scale(atm.hpr, atm.scale)
        self.set_transparency(TransparencyAttrib.MAlpha)
        # self.reparent_to(planet)

        cloud_shader = Shader.load(Shader.SL_GLSL, 'shaders/cloud_v.glsl', 'shaders/cloud_f.glsl')
        model.set_shader(cloud_shader)