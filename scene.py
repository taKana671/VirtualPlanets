import random
from collections import deque

from panda3d.core import NodePath
from panda3d.core import Point3, Vec3, LColor

from galaxy import Asteroids, AsteroidBelt
from galaxy import Galaxy
from galaxy import Sun
from galaxy import Planet, OrbitLine, ParticleRing, Atmosphere, Tail
from galaxy import GalaxyAmbientLight, SunPointLignt
from galaxy import RoguePlanet
from planet_details import OrbitDetails, RingDetails, PlanetDetails
from planet_details import AsteroidBeltDetails, AtmosphereDetails
from planet_details import RoguePlanetDetails, AtlasDetails
from planet_details import TrailDetailds


class Scene:

    def __init__(self):
        self.root = NodePath('root')
        self.root.reparent_to(base.render)

        self.galaxy = Galaxy()
        self.asteroids = Asteroids()

        self.planets = []
        sun_pos = Point3(0, 0, 0)
        self.create_sun(sun_pos)
        self.create_planets(sun_pos)

        self.rogue_queue = self.get_rogue_planet_details()
        self.spawn_time = 20
        self.spawn_timer = 0
        self.rogue_planet = None

    def get_planet_details(self, sun_pos):
        green = OrbitDetails(rx=12.0, ry=9.0, tilt=Vec3(15, 0, 5), eccentricity=0.0, center=sun_pos)
        snow = OrbitDetails(rx=20.0, ry=15.0, tilt=Vec3(-10, 25, 0), eccentricity=0.2, center=sun_pos)
        earth = OrbitDetails(rx=29.0, ry=21.75, tilt=Vec3(5, 45, -5), eccentricity=0.58, center=sun_pos)
        desert = OrbitDetails(rx=38.0, ry=28.5, tilt=Vec3(25, -20, 15), eccentricity=0.45, center=sun_pos)
        ice = OrbitDetails(rx=51.0, ry=38.25, tilt=Vec3(-10, -55, 25), eccentricity=0.6, center=sun_pos)
        sakura = OrbitDetails(rx=54.0, ry=40.5, tilt=Vec3(-10, 55, 80), eccentricity=0.4, center=sun_pos)

        atmosphere = AtmosphereDetails(hpr=Vec3(0, -30, 0), scale=Vec3(6.5))
        belt = AsteroidBeltDetails(orbit=desert, asteroids=self.asteroids)
        ring = RingDetails(color=LColor(0.58, 0.67, 0.74, 0.6), hpr=Vec3(0, 45, 0), particle_size=1.1, particle_cnt=2000, thickness=4)
        trail = TrailDetailds(radius=1.2, length=2)

        planet_details = [
            PlanetDetails(name='green', orbit=green, speed=1.6, scale=0.25),
            PlanetDetails(name='snow', orbit=snow, speed=1.0, scale=0.4, atmosphere=atmosphere),
            PlanetDetails(name='earth', orbit=earth, speed=0.6, scale=0.62),
            PlanetDetails(name='desert', orbit=desert, speed=0.3, scale=0.45, asteroids=belt),
            PlanetDetails(name='ice', orbit=ice, speed=0.12, scale=0.65, ring=ring),
            PlanetDetails(name='sakura', orbit=sakura, speed=0.5, scale=0.15, trail=trail),
        ]

        return planet_details

    def get_rogue_planet_details(self):
        spark = 'spark3.png'
        rogue_planet_details = [
            RoguePlanetDetails(vfx=AtlasDetails(spark, size=15.5), start=Point3(15, 150, -180), end=Point3(-15, -55, 40), scale=2.5, speed=0.04),
            RoguePlanetDetails(vfx=AtlasDetails(spark, size=14.5), start=Point3(-15, -80, 80), end=Point3(-22, 40, -50), scale=2.4, speed=0.1),
            RoguePlanetDetails(vfx=AtlasDetails(spark, size=14), start=Point3(1, -80, 80), end=Point3(22, 35, -40), scale=2.2, speed=0.1),
            RoguePlanetDetails(vfx=AtlasDetails(spark, size=15), start=Point3(10, 120, -130), end=Point3(25, -55, 60), scale=2.5, speed=0.04),
            RoguePlanetDetails(vfx=AtlasDetails(spark, size=18), start=Point3(10, 120, -130), end=Point3(-25, -55, 45), scale=3, speed=0.05)
        ]

        random.shuffle(rogue_planet_details)
        return deque(rogue_planet_details)

    def create_sun(self, sun_pos):
        sun = Sun(sun_pos, Vec3(0, -10, 0))
        sun.reparent_to(self.root)
        self.planets.append(sun)

        self.ambient_light = GalaxyAmbientLight()
        self.sun_light = SunPointLignt(sun)

    def create_planets(self, sun_pos):
        planet_details = self.get_planet_details(sun_pos)

        for details in planet_details:
            planet = Planet(*details.planet)
            planet.reparent_to(self.root)
            self.planets.append(planet)

            orbit_line = OrbitLine(details.orbit)
            orbit_line.reparent_to(self.root)

            if details.asteroids is not None:
                belt = AsteroidBelt(*details.asteroids, planet)
                belt.reparent_to(self.root)
                self.planets.append(belt)

            if details.atmosphere is not None:
                atmosphere = Atmosphere(details.atmosphere)
                atmosphere.reparent_to(planet)

            if details.ring is not None:
                ring = ParticleRing(details.ring, planet)
                ring.reparent_to(planet.directional_nd)

            if details.trail is not None:
                trail = Tail(planet, details.trail)
                self.planets.append(trail)

    def update(self, dt):
        for planet in self.planets:
            planet.update(dt)

        if self.rogue_planet is None:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_time:
                details = self.rogue_queue[0]
                self.rogue_planet = RoguePlanet(self.asteroids, *details)
                self.rogue_planet.reparent_to(base.render)

        if self.rogue_planet is not None:
            if not self.rogue_planet.update(dt):
                self.rogue_planet.remove_node()
                self.rogue_planet = None
                self.spawn_timer = 0
                self.rogue_queue.rotate(-1)