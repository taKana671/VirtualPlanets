from panda3d.core import NodePath, PandaNode
from panda3d.core import Shader
from panda3d.core import Camera

from shapes import Box


class Galaxy(NodePath):

    def __init__(self, size=3000):
        super().__init__(PandaNode('galaxy'))
        box = Box(size, size, size).create()
        box.reparent_to(self)
        self.create_camera()

        shader = Shader.load(Shader.SL_GLSL, 'shaders/galaxy_v.glsl', 'shaders/galaxy_f.glsl')
        box.set_shader(shader)
        props = base.win.get_properties()
        win_size = props.get_size()
        box.set_shader_input('u_resolution', win_size)

    def create_camera(self):
        region = base.win.make_display_region(0, 1, 0, 1)
        cam = NodePath(Camera('sky_cam'))
        cam.node().set_lens(base.camLens)
        cam.reparent_to(self)
        region.set_camera(cam)
        region.set_sort(-1000)
