import math
from typing import NamedTuple

import numpy as np
from panda3d.core import NodePath, PandaNode
from panda3d.core import Point3, Vec3, LRotation, LColor

from shapes import ShatteredSphere
from voronoi_generator.voronoi_3d.clip2sphere import VoronoiClip2Sphere


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

    def __init__(self, orbit, asteroids, planet):
        super().__init__(PandaNode(f'{orbit.planet_name}_belt'))
        self.orbit = orbit
        self.planet = planet
        self.asteroids = [a for a in self.create_astroid_belt(asteroids)]
        self.set_color(LColor(0.6, 0.37, 0.19, 1.0))

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

    def revolve(self, sun_pos, _):
        tilt_rot = LRotation(*self.orbit.tilt)

        for asteroid in self.asteroids:
            direction = 1 if asteroid.is_front else -1
            angle = self.planet.angle + asteroid.base_delay * direction

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