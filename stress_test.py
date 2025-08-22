from panda3d.core import loadPrcFileData, PTA_LMatrix4f, LMatrix4f, Shader, ShaderBuffer, StringStream,\
 GeomEnums, OmniBoundingVolume

loadPrcFileData("", "show-frame-rate-meter #t")
loadPrcFileData("", "sync-video 0")

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

import random

class InstancedBasics(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.cam.set_pos(0, -800.0, 0)

        INSTANCE = 1000

        instanced_array = PTA_LMatrix4f.emptyArray(INSTANCE)

        for i in range(INSTANCE):
            scale = LMatrix4f().scale_mat((1, 1, 1))
            rotate_x = LMatrix4f().rotate_mat(random.uniform(-90, 90), (1, 0, 0))
            rotate_y = LMatrix4f().rotate_mat(random.uniform(-90, 90), (0, 1, 0))
            rotate_z = LMatrix4f().rotate_mat(random.uniform(-90, 90), (0, 0, 1))
            translate = LMatrix4f().translate_mat((random.uniform(-150, 150), random.uniform(-150, 150), random.uniform(-150, 150)))

            transform = scale * ( rotate_y * rotate_x * rotate_z) * translate
            instanced_array.set_element(i, transform)

        self.model = Actor('panda', {'walk' : 'panda-walk'})
        self.model.node().set_bounds(OmniBoundingVolume())
        self.model.node().set_final(True)
        self.model.loop('walk')
        self.model.reparent_to(render)

        self.model.set_instance_count(INSTANCE)
        self.model.set_shader(Shader.load(Shader.SL_GLSL, vertex = 'shaders/instancing_vertex.glsl', fragment = 'shaders/instancing_fragment.glsl'))
        self.model.set_shader_input("instanced_object", ShaderBuffer('DataBuffer', StringStream(instanced_array).get_data(), GeomEnums.UH_static))

instanced_basics = InstancedBasics()
instanced_basics.run()