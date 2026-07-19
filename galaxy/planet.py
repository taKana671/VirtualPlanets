import math
import random

import numpy as np
from direct.motiontrail.MotionTrail import MotionTrail
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath, PandaNode
from panda3d.core import Point3, Vec3, LRotation, LColor
from panda3d.core import TransparencyAttrib
from panda3d.core import Shader
from panda3d.core import Texture, TextureStage

from noise import Fractal2D, PerlinNoise
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


class Tail(MotionTrail):

    def __init__(self, planet, trail):
        super().__init__(f'{trail.moving_object_name}_tail', planet.model)
        self.create_motion_trail(trail)

    def create_noise_texture(self):
        perlin = PerlinNoise()
        noise = Fractal2D(perlin.pnoise2)

        size = 512
        t = random.uniform(0, 1000)

        arr = np.array(
            [noise.fractal(x + t, y + t)
                for y in np.linspace(0, 4, size)
                for x in np.linspace(0, 4, size)]
        )

        # Increase the black areas of the fractal noise to make
        # the contrast between black and white more distinct.
        min_val = np.min(arr)
        max_val = np.max(arr)
        arr = (arr - min_val) / (max_val - min_val)
        arr = np.power(arr, 1.5) * 1.2

        # Change shape from (size ** 2,) to (size, size, 3)
        arr = arr.reshape((size, size))
        arr = np.repeat(arr[:, :, np.newaxis], 3, axis=2)
        arr = np.clip(arr * 255, a_min=0, a_max=255).astype(np.uint8)
        # cv2.imwrite('sample.png', arr)

        # Sets the texture as an empty 2-d texture.
        tex = Texture('noise_image')
        tex.setup_2d_texture(
            size,
            size,
            Texture.T_unsigned_byte,
            Texture.F_rgb
        )

        # Fill the image data.
        tex.set_ram_image(arr)
        return tex

    def create_motion_trail(self, trail):
        tex = self.create_noise_texture()
        self.set_texture(tex)

        self.register_motion_trail()
        self.geom_node_path.reparent_to(base.render)
        # A larger time window creates longer motion trails.
        self.time_window = trail.length

        colors = (
            LColor(0.98, 0.75, 0.95, 1.0),
            LColor(0.90, 0.80, 0.98, 1.0),
            LColor(0.65, 0.88, 0.98, 1.0),
            LColor(0.55, 0.92, 0.95, 1.0)
        )

        theta = np.linspace(0, 2 * np.pi, 13)
        z_arr = trail.radius * np.cos(theta)
        x_arr = trail.radius * np.sin(theta)

        # Define the shape of the cross-section polygon that is to be
        # extruded along the motion trail.
        for i, (x, z) in enumerate(zip(x_arr, z_arr)):
            vertex = Point3(x, 0, z)
            self.add_vertex(vertex)

            start_color = colors[i % len(colors)] * 1.1
            end_color = LColor(0.58, 0.91, 0.95, 1.0)
            # end_color = LColor(0.75, 0.85, 0.98, 1.0)
            self.set_vertex_color(i, start_color, end_color)

        self.update_vertices()
        # LerpTexOffsetInterval(self.geom_node_path, 4, (1, 1), (1, 0)).loop()

    def update(self, _):
        frame_time = globalClock.get_frame_time()
        offset_v = frame_time * 0.4
        offset_v %= 1

        self.geom_node_path.set_tex_offset(TextureStage.get_default(), 0, offset_v)