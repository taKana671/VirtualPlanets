import math
from typing import NamedTuple

import numpy as np
from panda3d.core import NodePath, PandaNode
from panda3d.core import Point3, Vec3, LRotation
from panda3d.core import TransparencyAttrib
from panda3d.core import Shader


from shapes import EllipticalPrism, Particles
from shapes import ShatteredSphere
from voronoi_generator.voronoi_3d.clip2sphere import VoronoiClip2Sphere


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

    def revolve(self, sun_pos, dt):
        if self.angle > math.tau:
            self.angle -= math.tau

        seed_multiplier = 1.0 / (1.0 + self.orbit.eccentricity * math.cos(self.angle))
        self.angle += self.speed * seed_multiplier * dt

        x = math.cos(self.angle) * self.orbit.rx
        y = math.sin(self.angle) * self.orbit.ry
        pos = Vec3(x, y, 0)
        tilt_rot = LRotation(*self.orbit.tilt)
        tilted_pos = tilt_rot.xform(pos)
        final_pos = sun_pos + tilted_pos
        self.set_pos(final_pos)

        hpr = Vec3(self.directional_nd.get_h() + 50 * dt, 0, 0)
        self.directional_nd.set_hpr(hpr)


class OrbitLine(NodePath):

    def __init__(self, orbit, thickness=0.02, height=0.02):
        super().__init__(PandaNode('orbit_line'))

        orbit_line = EllipticalPrism(
            major_axis=orbit.major_axis,
            minor_axis=orbit.minor_axis,
            thickness=thickness,
            height=height
        ).create()

        orbit_line.reparent_to(self)
        self.set_hpr(orbit.tilt)


class ParticleRing(NodePath):

    def __init__(self, planet, color, hpr, particle_size=1.1, particle_cnt=2000, ring_thickness=4):
        super().__init__(PandaNode("ring"))
        ring = self.create_particles(planet, ring_thickness, particle_cnt)
        ring.reparent_to(self)
        self.set_render_mode_thickness(particle_size)
        self.set_color(color)
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.set_hpr(hpr)

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

    def __init__(self, hpr, scale):
        super().__init__(PandaNode("atmosphere"))
        model = base.loader.load_model('models/sun.bam')
        model.reparent_to(self)
        self.set_hpr_scale(hpr, scale)
        self.set_transparency(TransparencyAttrib.MAlpha)
        # self.reparent_to(planet)

        cloud_shader = Shader.load(Shader.SL_GLSL, 'shaders/cloud_v.glsl', 'shaders/cloud_f.glsl')
        model.set_shader(cloud_shader)


class Asteroids(NodePath):

    def __init__(self, cut_points=30, max_depth=3, scale=1):
        super().__init__(PandaNode('asteroids'))
        self.cut_points = cut_points
        self.max_depth = max_depth
        self.scale = scale
        self.create_asteroids()

    def create_asteroids(self):
        for i, (polygons, spherical_idx) in enumerate(VoronoiClip2Sphere(self.cut_points)):
            model_creator = ShatteredSphere(polygons, spherical_idx, self.max_depth, self.scale)
            asteroid = model_creator.create()
            asteroid.set_pos(Point3(*model_creator.polyhedron_org_center))
            asteroid.reparent_to(self)


class Asteroid(NamedTuple):

    model: NodePath
    base_delay: float
    side_spread: float
    is_front: bool


class AsteroidBelt(NodePath):

    def __init__(self, asteroids, planet, orbit):
        super().__init__(PandaNode('asteroid_belt'))
        self.orbit = orbit
        self.planet = planet
        self.asteroids = [a for a in self.create_astroid_belt(asteroids)]

    def get_random_scale(self):
        return np.random.uniform(0.6, 1.1)

    def get_base_delay(self, distance):
        """Squaring the random numbers creates a density gradient in which most of the asteroids cluster
            just behind the planet, while only a few extend far behind it at the given distance.
        """
        return (np.random.uniform(0.5, 1.5) ** 2) * distance

    def get_side_spread(self, base_delay):
        """The farther away from the planet (as `base_delay` increases),
            the wider the orbital ring spreads in the width direction.
        """
        return np.random.uniform(-1.0, 1.0) * (base_delay * 6.0)

    def create_astroid_belt(self, asteroids):
        for asteroid in asteroids.get_children():
            # asteroid behind the direction of travel
            model = asteroid.copy_to(self)
            model.set_scale(self.get_random_scale())

            yield Asteroid(
                model=model,
                base_delay=(delay := self.get_base_delay(0.55)),
                side_spread=self.get_side_spread(delay),
                is_front=False
            )

            # asteroid ahead the direction of travel
            model = model.copy_to(self)
            model.set_scale(self.get_random_scale())

            yield Asteroid(
                model=model,
                base_delay=(delay := self.get_base_delay(0.40)),
                side_spread=self.get_side_spread(delay),
                is_front=True
            )

    # def revolve(self, planet_angle, sun_pos):
    def revolve(self, sun_pos, _):
        tilt_rot = LRotation(*self.orbit.tilt)

        for asteroid in self.asteroids:
            if asteroid.is_front:
                # angle = planet_angle + asteroid.base_delay
                angle = self.planet.angle + asteroid.base_delay
            else:
                angle = self.planet.angle - asteroid.base_delay

            x = math.cos(angle) * self.orbit.rx
            y = math.sin(angle) * self.orbit.ry

            # By adding `side_spread` based on the orientation of the ellipse (cos, sin),
            # the trail will not extend beyond the orbit ring and will trail neatly behind it.
            x += math.cos(angle) * asteroid.side_spread
            y += math.sin(angle) * asteroid.side_spread

            pos = Vec3(x, y, 0)
            tilted_pos = tilt_rot.xform(pos)
            final_pos = sun_pos + tilted_pos
            asteroid.model.set_pos(final_pos)