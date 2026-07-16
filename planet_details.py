from typing import NamedTuple
from dataclasses import dataclass

from panda3d.core import NodePath
from panda3d.core import Vec3, Point3, LColor


@dataclass(frozen=True)
class OrbitDetails:
    """Orbit details. Used to calculate a planet's position and to create models depicting its orbit.
        rx: Semi-major axis
        ry: Semi-minor axis
        tilt: Orbital inclination
        eccentricity: Indicates how much a celestial body's orbit deviates from a perfect circle.
        planet_name: Name of satellites in orbit
    """

    rx: float
    ry: float
    tilt: Vec3
    eccentricity: float
    center: Point3
    planet_name: str = None

    @property
    def major_axis(self):
        return self.rx * 2

    @property
    def minor_axis(self):
        return self.ry * 2


@dataclass(frozen=True)
class RingDetails:
    """Details of a ring of particles surrounding a planet.
        color: The color of particles
        hpr: Ring inclination
        particle_size: The size of the particles forming the ring
        particle_cnt: The number of the particles forming the ring
        thickness: The width of the concentric ring
        planet_name: The name of the planet located at the center of the ring
    """

    color: LColor
    hpr: Vec3
    particle_size: float
    particle_cnt: int
    thickness: float
    planet_name: str = None


class AsteroidBeltDetails(NamedTuple):
    """Details of an asteroid belt
        orbit: Asteroids' orbit details
        asteroids: A nodepath of the asteroids that make up the asteroid belt
    """

    orbit: OrbitDetails
    asteroids: NodePath


@dataclass(frozen=True)
class AtmosphereDetails:
    """Details of a planetary atmosphere created by applying a shader to a sphere
       slightly larger than the planet itself.
        hpr: Inclination of the sphere to which the shader is applied
        scale: Scale of the sphere to which the shader is applied
        planet_name: The name of the planet located at the center of the sphere
    """

    hpr: Vec3
    scale: float
    planet_name: str = None


@dataclass(frozen=True)
class PlanetDetails:
    """Planet Details
        name: planet name
        speed: The speed at which a planet orbits
        orbit: Orbit details
        ring: Details of a ring of particles surrounding a planet; default is None.
        atmosphere: Details of a planetary atmosphere; default is None.
        asteroids: Details of an asteroid belt; default is None.
    """

    name: str
    speed: float
    scale: float
    orbit: OrbitDetails
    ring: RingDetails = None
    atmosphere: AtmosphereDetails = None
    asteroids: AsteroidBeltDetails = None

    def __post_init__(self):
        if self.orbit:
            object.__setattr__(self.orbit, 'planet_name', self.name)

        if self.ring:
            object.__setattr__(self.ring, 'planet_name', self.name)

        if self.atmosphere:
            object.__setattr__(self.atmosphere, 'planet_name', self.name)

    @property
    def planet(self):
        return self.name, self.speed, self.scale, self.orbit


class AtlasDetails(NamedTuple):
    """Details on the atlas textures Used in rogue planet
        file_name: Image file name
        size: image size
        cols:
            A value indicating how many small images of the same size fit
            horizontally within a single image.
        rows:
            A value indicating how many small images of the same size fit
            vertically within a single image.
    """

    file_name: str
    size: float = 1
    cols: int = 8
    rows: int = 8


class RoguePlanetDetails(NamedTuple):
    """Rogue planet Details
        start: Start point
        end: The point where the explosion begins
        scale: Planet's Scale
        speed: Movement Speed
    """

    vfx: AtlasDetails
    start: Point3
    end: Point3
    scale: float
    speed: float