import numpy as np

from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import LColor, Vec3
from panda3d.core import NodePath, PandaNode
from panda3d.core import PNMImage, Texture, TextureStage
from panda3d.core import TransparencyAttrib
from panda3d.core import Shader

from noise import Fractal2D, PerlinNoise
from shapes import Plane


class SolarFlare(NodePath):

    def __init__(self, pos):
        super().__init__(PandaNode('solar_flare'))
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.set_pos_hpr(pos, Vec3(0, 90, 0))
        self.set_billboard_point_eye()

        shader = Shader.load(Shader.SL_GLSL, 'shaders/flare_v.glsl', 'shaders/flare_f.glsl')
        self.panel = Plane(10, 10, 4, 4).create()
        self.panel.reparent_to(self)
        self.panel.set_shader(shader)


class Sun(NodePath):

    def __init__(self, pos, hpr):
        super().__init__(PandaNode('sun'))
        self.model = base.loader.load_model('models/sphere.bam')
        self.model.reparent_to(self)
        self.set_pos_hpr_scale(pos, hpr, Vec3(2))
        self.setup_textures()

        self.flare = SolarFlare(pos)
        self.flare.reparent_to(self)

    def create_texture_img(self):
        noise = PerlinNoise()
        noise = Fractal2D(noise.pnoise2)

        size = 256
        img = PNMImage(size, size, 3)

        color_dark = LColor(0.3, 0.0, 0.0, 1.0)
        color_mid = LColor(1.0, 0.3, 0.0, 1.0)
        color_high = LColor(1.0, 0.9, 0.2, 1.0)

        for j, y in enumerate(np.linspace(0, 12, size)):
            for i, x in enumerate(np.linspace(0, 12, size)):
                if (val := noise.fractal(x, y)) < 0.5:
                    t = val * 2.0
                    final_color = color_dark * (1.0 - t) + color_mid * t
                else:
                    t = (val - 0.5) * 2.0
                    final_color = color_mid * (1.0 - t) + color_high * t

                img.set_xel(i, j, final_color.get_xyz())

        return img

    def setup_textures(self):
        img = self.create_texture_img()

        sun_tex = Texture()
        sun_tex.load(img)
        sun_tex.set_wrap_u(Texture.WM_repeat)
        sun_tex.set_wrap_v(Texture.WM_repeat)

        self.ts1 = TextureStage('sun_ts1')
        self.ts1.set_mode(TextureStage.M_modulate)
        self.set_texture(self.ts1, sun_tex)

        self.ts2 = TextureStage('sun_tx2')
        self.ts2.set_mode(TextureStage.M_add)
        self.set_texture(self.ts2, sun_tex)

        self.set_tex_scale(self.ts2, 1.5, 1.5)
        self.set_color_scale((2.0, 1.8, 1.2, 1.0))

    def update(self, dt):
        frame_time = globalClock.get_frame_time()

        offset_u1 = frame_time * 0.03
        offset_v1 = frame_time * 0.02
        self.set_tex_offset(self.ts1, offset_u1 % 1.0, offset_v1 % 1.0)

        offset_u2 = frame_time * -0.02
        offset_v2 = frame_time * -0.04
        self.set_tex_offset(self.ts2, offset_u2 % 1.0, offset_v2 % 1.0)

        self.set_h(self.get_h() + 10 * dt)