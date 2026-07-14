import random
import time


from panda3d.core import NodePath
from panda3d.core import Point3, Vec3, LColor

from galaxy import Asteroids, AsteroidBelt
from galaxy import Galaxy
from galaxy import Sun
from galaxy import Planet, OrbitLine, ParticleRing, Atmosphere
from galaxy import GalaxyAmbientLight, SunPointLignt
from galaxy import RoguePlanet
from planet_details import OrbitDetails, RingDetails, PlanetDetails
from planet_details import AsteroidBeltDetails, AtmosphereDetails
from planet_details import RoguePlanetDetails, TextureAtlasDetails


class Scene:

    def __init__(self):
        self.root = NodePath('root')
        self.root.reparent_to(base.render)

        self.galaxy = Galaxy()
        self.asteroids = Asteroids()


        # self.rogue_routes = [
        #     {"start": Point3(-60, -40, 10), "end": Point3(-10, -10, 2), "scale": 2.0, "speed": 0.05, "spawn_time": 1.0},  # 1機目（既存）
        #     {"start": Point3(-55, -50, -5), "end": Point3(5, -15, -2),   "scale": 2.5, "speed": 0.04, "spawn_time": 15.0}, # 2機目（迫力）
        #     {"start": Point3(50, -45, 25),  "end": Point3(15, -5, -5),   "scale": 1.8, "speed": 0.06, "spawn_time": 30.0}, # 3機目（危機一髪）
        #     {"start": Point3(60, 45, 8),    "end": Point3(8, 18, 2),     "scale": 2.2, "speed": 0.03, "spawn_time": 45.0}  # 4機目（奥側）
        # ]

        tex = TextureAtlasDetails('spark3.png', size=14, cols=8, rows=8)

        rogue_planets = [
            # RoguePlanetDetails(start=Point3(-60, -40, 10), end=Point3(-10, -10, 2), scale=2.0, speed=0.05, spawn_time=1.0),  # 1機目（既存）
            # RoguePlanetDetails(start=Point3(-55, -50, -5), end=Point3(5, -15, -2), scale=2.5, speed=0.04, spawn_time=15.0), # 2機目（迫力）
            # RoguePlanetDetails(start=Point3(50, -45, 25), end=Point3(15, -5, -5), scale=1.8, speed=0.06, spawn_time=30.0), # 3機目（危機一髪）
            # RoguePlanetDetails(tex=tex, start=Point3(60, 45, 8), end=Point3(8, 18, 2), scale=2.2, speed=0.03, spawn_time=45.0)  # 4機目（奥側）
            RoguePlanetDetails(tex=tex, start=Point3(15, 150, -180), end=Point3(-15, -25, 50), scale=2.2, speed=0.04, spawn_time=1.0),  # 4機目（奥側）
            # RoguePlanetDetails(tex=tex, start=Point3(0, 150, -140), end=Point3(0, -25, 70), scale=2.2, speed=0.04, spawn_time=1.0)
        ]

        # self.rogue_planet = RoguePlanet(
        #     self.asteroids, Point3(-60, -40, 10), Point3(-10, -10, 2), 2)

        self.rogue_planet = RoguePlanet(
            self.asteroids, *rogue_planets[0])

        # self.rogue_planet.set_pos(Point3(0, -30, 5))
        # self.rogue_planet.set_scale(2)
        self.rogue_planet.reparent_to(base.render)

        self.planets = []
        sun_pos = Point3(0, 0, 0)
        self.create_sun(sun_pos)
        self.create_planets(sun_pos)

    def get_planet_details(self, sun_pos):
        green = OrbitDetails(rx=12.0, ry=9.0, tilt=Vec3(15, 0, 5), eccentricity=0.0, center=sun_pos)
        snow = OrbitDetails(rx=20.0, ry=15.0, tilt=Vec3(-10, 25, 0), eccentricity=0.2, center=sun_pos)
        earth = OrbitDetails(rx=29.0, ry=21.75, tilt=Vec3(5, 45, -5), eccentricity=0.58, center=sun_pos)
        desert = OrbitDetails(rx=38.0, ry=28.5, tilt=Vec3(25, -20, 15), eccentricity=0.45, center=sun_pos)
        ice = OrbitDetails(rx=51.0, ry=38.25, tilt=Vec3(-10, -55, 25), eccentricity=0.6, center=sun_pos)

        atmosphere = AtmosphereDetails(hpr=Vec3(0, -30, 0), scale=Vec3(6.5))
        belt = AsteroidBeltDetails(orbit=desert, asteroids=self.asteroids)
        ring = RingDetails(color=LColor(0.58, 0.67, 0.74, 0.6), hpr=Vec3(0, 45, 0), particle_size=1.1, particle_cnt=2000, thickness=4)

        planet_details = [
            PlanetDetails(name='green', orbit=green, speed=1.6, scale=0.25),
            PlanetDetails(name='snow', orbit=snow, speed=1.0, scale=0.4, atmosphere=atmosphere),
            PlanetDetails(name='earth', orbit=earth, speed=0.6, scale=0.62),
            PlanetDetails(name='desert', orbit=desert, speed=0.3, scale=0.45, asteroids=belt),
            PlanetDetails(name='ice', orbit=ice, speed=0.12, scale=0.65, ring=ring),
        ]

        return planet_details

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

    def update(self, dt):
        for planet in self.planets:
            planet.update(dt)

        if self.rogue_planet is not None:
            if (result := self.rogue_planet.update(dt)) is not None \
                    and not result:
                print('rogue planet disappeard')
                self.rogue_planet.remove_node()
                self.rogue_planet = None



# なぜ他の惑星と「絶対にぶつからない」のか？
# 一番大きな理由は、既存の5つの惑星の軌道リングが、
# 太陽を中心に「それぞれバラバラな3Dの角度（tilt）」でダイナミックに斜めに傾いているからです。
# 平面の2Dで見ると軌道線が網の目のように複雑に重なって見えますが、
# 3D空間上では、それぞれの惑星の軌道は「ねじれの位置（高さや奥行きが違う立体交差）」になっています。