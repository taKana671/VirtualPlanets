from panda3d.core import AmbientLight, PointLight
from panda3d.core import NodePath
from panda3d.core import LColor, Vec3


class GalaxyAmbientLight(NodePath):

    def __init__(self):
        super().__init__(AmbientLight('ambient_light'))
        self.node().set_color(LColor(0.6, 0.6, 0.6, 1.0))
        self.reparent_to(base.render)
        base.render.set_light(self)


class SunPointLignt(NodePath):

    def __init__(self, sun):
        super().__init__(PointLight('point_light'))
        self.set_pos(sun.get_pos())
        self.node().set_color(LColor(1, 1, 1, 1))
        self.node().set_attenuation(Vec3(0.2, 0, 0.001))
        self.node().get_lens().set_near_far(10, 10000)
        self.node().set_shadow_caster(True)

        self.reparent_to(base.render)
        base.render.set_light(self)
        # point_light.node().show_frustum()