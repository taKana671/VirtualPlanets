import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Point3, Vec3, Vec2
from panda3d.core import NodePath
from panda3d.core import AntialiasAttrib
from panda3d.core import load_prc_file_data

from scene import Scene
from lights import GalaxyAmbientLight, SunPointLignt


load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    window-title FluidCube
    filled-wireframe-apply-shader true
    stm-max-views 8
    stm-max-chunk-count 2048
    framebuffer-multisample 1
    multisamples 2""")


class Planets(ShowBase):

    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.render.set_antialias(AntialiasAttrib.MAuto)
        # self.setBackgroundColor(0., 0., 0., 0.)
        # self.win.set_clear_color((0, 0, 0, 0))

        self.camera_root = NodePath('camera_root')
        self.camera_root.reparent_to(self.render)
        self.camera.reparent_to(self.camera_root)
        self.camera.set_pos(Point3(0, -100, 100))
        self.camera.look_at(Point3(0, 0, 0))

        # self.particles = BoxCollection()
        # self.particles.create()
        self.scene = Scene()
        self.ambient_light = GalaxyAmbientLight()
        self.sun_light = SunPointLignt(self.scene.sun)

        self.clicked = False
        self.dragging = False
        self.before_mouse_pos = None
        self.do_move = False

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        # self.accept('m', self.start_move_particles)

        self.taskMgr.add(self.update, 'update')

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        if globalClock.get_frame_time() - self.dragging_start_time < 0.2:
            self.clicked = True

        self.dragging = False
        self.before_mouse_pos = None

    def rotate_camera(self, mouse_pos, dt):
        if self.before_mouse_pos:
            angle = Vec3()

            if (delta := mouse_pos.x - self.before_mouse_pos.x) < 0:
                angle.x += 180
            elif delta > 0:
                angle.x -= 180

            if (delta := mouse_pos.y - self.before_mouse_pos.y) < 0:
                angle.z -= 180
            elif delta > 0:
                angle.z += 180

            angle *= dt
            self.camera_root.set_hpr(self.camera_root.get_hpr() + angle)

        self.before_mouse_pos = Vec2(mouse_pos.xy)

    def update(self, task):
        dt = globalClock.get_dt()

        if self.mouseWatcherNode.has_mouse():
            mouse_pos = self.mouseWatcherNode.get_mouse()

            if self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    self.rotate_camera(mouse_pos, dt)

        # if self.do_move:
        #     if self.particles.move(dt):
        #         self.do_move = False
        self.scene.update(dt)
        return task.cont


if __name__ == '__main__':
    app = Planets()
    app.run()