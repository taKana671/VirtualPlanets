import math
from dataclasses import dataclass
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBaseGlobal import globalClock

from panda3d.core import NodePath, PandaNode, RenderAttrib
from panda3d.core import Point3, Vec3, LColor, LRotation
from panda3d.core import PNMImage, Texture, TextureStage, StackedPerlinNoise2
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from direct.particles.ForceGroup import ForceGroup
# from direct.particles.LinearVectorForce import LinearVectorForce
# from direct.tkpanels.ParticlePanel import ParticlePanel

from panda3d.physics import PointParticleFactory
from panda3d.physics import SparkleParticleRenderer

from panda3d.physics import SphereSurfaceEmitter, BaseParticleRenderer



from noise import PerlinNoise, SimplexNoise, TileableSimplexNoise, Fractal2D, TileablePerlinNoise, Fractal3D
import numpy as np


# @dataclass
# class Planet:

#     name: str
#     rx: float
#     rz: float
#     speed: float
#     tilt: tuple

#     def create_planet(self):
#         return SphereModel(
#             rx=self.rx,
#             rz=self.rz,
#             speed=self.speed,



#         )


class Sun(NodePath):

    def __init__(self):
        super().__init__(PandaNode('sun'))
        self.model = base.loader.load_model('models/sphere_rad2.bam')
        self.model.reparent_to(self)
        self.set_scale(1.5)

        # noise = PerlinNoise()
        noise = TileablePerlinNoise()
        noise = Fractal2D(noise.pnoise2)

        # noise = SimplexNoise()
        # noise = TileableSimplexNoise()
        # noise = Fractal2D(noise.snoise2)

        # noise = StackedPerlinNoise2(0.3, 0.3, 4, 2.0, 0.5)
        size = 256
        img = PNMImage(size, size, 3)

        color_dark = LColor(0.3, 0.0, 0.0, 1.0)
        color_mid = LColor(1.0, 0.3, 0.0, 1.0)
        color_high = LColor(1.0, 0.9, 0.2, 1.0)

        # fractal perlin
        for j, y in enumerate(np.linspace(0, 12, size)):
            for i, x in enumerate(np.linspace(0, 12, size)):
        
        # fratal simplex
        # for j, y in enumerate(range(size)):
        #     for i, x in enumerate(range(size)):
        
                # fractal perlin
                if (val := noise.fractal(x, y)) < 0.5:
                
                # fractal simplex
                # if (val := noise.fractal(x / size * 10, y / size * 10)) < 0.5:
                    t = val * 2.0
                    final_color = color_dark * (1.0 - t) + color_mid * t
                else:
                    t = (val - 0.5) * 2.0
                    final_color = color_mid * (1.0 - t) + color_high * t

                img.set_xel(i, j, final_color.get_xyz())

        self.sun_tex1 = Texture()
        self.sun_tex1.load(img)
        self.sun_tex1.set_wrap_u(Texture.WM_repeat)
        self.sun_tex1.set_wrap_v(Texture.WM_repeat)

        self.ts1 = TextureStage('sun_ts1')
        self.ts1.set_mode(TextureStage.M_modulate)
        self.set_texture(self.ts1, self.sun_tex1)

        self.ts2 = TextureStage('sun_tx2')
        self.ts2.set_mode(TextureStage.M_add)
        self.set_texture(self.ts2, self.sun_tex1)
        self.set_tex_scale(self.ts2, 1.5, 1.5)

        self.set_color_scale((2.0, 1.8, 1.2, 1.0))

        # base.filters = CommonFilters(base.win, base.cam)
        # base.filters.set_bloom(
        #     blend=(0.5, 0.5, 0.5, 1.0),
        #     desat=-0.5,
        #     intensity=5.0,
        #     size="large"
        # )


        # base.enable_particles()
        # self.spark_effect = ParticleEffect()
        # self.set_sparks()
        # self.spark_effect.reparent_to(self)
        # self.spark_effect.start(self)



        base.task_mgr.add(self.update, 'update_sun')

    def set_sparks(self):
        p = Particles()
        # p.set_factory('PointParticleFactory')
        # p.set_renderer('SparkParticleRenderer')
        # p.set_emitter('SphereSurfaceEmitter')
        factory = PointParticleFactory()
        renderer = SparkleParticleRenderer()
        emitter = SphereSurfaceEmitter()

        p.set_factory(factory)
        p.set_renderer(renderer)
        p.set_emitter(emitter)

        emitter.set_radius(1.0)
        emitter.set_emission_type(SphereSurfaceEmitter.ET_RADIATE)
        emitter.set_amplitude(2.5)
        emitter.set_amplitude_spread(0.5)

        # renderer.set_birth_radius(0.04)
        # renderer.set_initial_vertex_scale(0.04)
        # renderer.set_final_vertex_scale(0.01)
        # renderer.setDeathRadius(0.01)
        renderer.set_center_color(LColor(1.0, 0.9, 0.3, 1.0)) # 明るい黄色
        renderer.set_edge_color(LColor(0.5, 0.1, 0.0, 0.0))
        renderer.set_alpha_mode(BaseParticleRenderer.PR_ALPHA_OUT)

        p.set_pool_size(500)
        p.set_birth_rate(0.02)
        p.set_litter_size(3)
        # p.set_litter_velocity_scale(2.5)

        p.set_system_lifespan(0.0)
        factory.set_lifespan_base(1.0)
        factory.set_lifespan_spread(0.5)

        f_group = ForceGroup('spark_forces')
        # p.add_focce_group(f_group)
        self.spark_effect.add_particles(p)

    def update(self, task):
        dt = globalClock.get_dt()
        offset_u1 = task.time * 0.03
        offset_v1 = task.time * 0.02
        self.set_tex_offset(self.ts1, offset_u1, offset_v1)

        offset_u2 = task.time * -0.02
        offset_v2 = task.time * -0.04
        self.setTexOffset(self.ts2, offset_u2, offset_v2)

        self.set_h(self.get_h() + 2 * dt)  # これいる？
        return task.cont




        
        
        
        
        
        
        
        # base color
        # self.set_color(LColor(1.0, 0.6, 0.1, 1.0))
        # self.set_color_scale(LColor(2.5, 1.5, 0.3, 1.0))
        # self.set_light_off()        
        # base.filters = CommonFilters(base.win, base.cam)
        # base.filters.set_bloom(
        #     blend=(0.3, 0.3, 0.3, 1.0),
        #     desat=-0.5,
        #     intensity=3.5,
        #     size="large",
        #     glowMethod=RenderAttrib.M_glow
        # ) 





class SphereModel(NodePath):

    def __init__(self, rx, rz, speed, tilt):
        super().__init__(PandaNode('sphere'))
        # self.model = base.loader.load_model('models/sphere_rad2.bam')
        self.model = base.loader.load_model('models/Island_20260620214009.bam')
        self.model.reparent_to(self)
        self.set_scale(0.5)

        # self.set_color(LColor(1, 0, 0, 1), 1)

        # self.rx = 28.0
        # self.rz = 18.0
        # self.speed = 0.8
        # self.tilt = Vec3(-10, 25, 0)
        # self.angle = 0

        # self.rx = 50.0
        # self.rz = 30.0
        # self.speed = 0.2
        # self.tilt = Vec3(45, 0, 45)
        # self.angle = 0

        self.rx = rx
        self.rz = rz
        self.speed = speed
        self.tilt = tilt
        self.angle = 0


class Scene:

    def __init__(self):
        self.root = NodePath('root')
        self.root.reparent_to(base.render)
        # self.sphere = SphereModel()
        # self.sphere.reparent_to(self.root)
        # self.sphere.set_pos(Point3(0, 0, 0))

        self.sun = Sun()
        # self.sun.set_pos(Point3(0, 0, 0))
        # self.sun_pos = Point3(0, 0, 0)
        self.sun.reparent_to(self.root)

        self.planets = [
            # SphereModel(rx=10.0, rz=10.0, speed=2.0, tilt=(0, 0, 0)),
            # SphereModel(rx=18.0, rz=14.0, speed=1.2, tilt=(15, 0, 5)),
            # SphereModel(rx=28.0, rz=18.0, speed=0.8, tilt=(-10, 25, 0)),
            SphereModel(rx=38.0, rz=35.0, speed=0.5, tilt=(5, 45, -5)),
            # SphereModel(rx=50.0, rz=30.0, speed=0.2, tilt=(45, 0, 45)),
        ]

        for planet in self.planets:
            planet.reparent_to(self.root)

    def update(self, dt):
        for planet in self.planets:
            planet.angle += planet.speed * dt

            x = math.cos(planet.angle) * planet.rx
            z = math.sin(planet.angle) * planet.rz
            pos = Vec3(x, 0, z)

            tilt_rot = LRotation(*planet.tilt)
            tilted_pos = tilt_rot.xform(pos)
            final_pos = self.sun.get_pos() + tilted_pos
            planet.set_pos(final_pos)
            planet.set_pos(final_pos)
            planet.set_h(planet.get_h() + 50 * dt)



        # self.sphere.angle += self.sphere.speed * dt

        # x = math.cos(self.sphere.angle) * self.sphere.rx
        # z = math.sin(self.sphere.angle) * self.sphere.rz
        # pos = Vec3(x, 0, z)

        # tilt_rot = LRotation(*self.sphere.tilt)
        # tilted_pos = tilt_rot.xform(pos)
        # final_pos = self.sun_pos + tilted_pos
        # self.sphere.set_pos(final_pos)
        # self.sphere.set_pos(final_pos)
        # self.sphere.set_h(self.sphere.get_h() + 50 * dt)


