#Adapted from Teedee's HW instancing code: https://www.panda3d.org/forums/viewtopic.php?f=1&t=13057&hilit=hardware+instancing

import sys
import os
import random
from math import pi, sin, cos

from direct.task import Task
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import loadPrcFileData,loadPrcFile
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename,Spotlight,DirectionalLight,VBase4,PerspectiveLens,CardMaker,Shader,PTA_LMatrix4f,OmniBoundingVolume,UnalignedLMatrix4f,BoundingSphere,LPoint3f,Fog
from panda3d.core import FadeLODNode,NodePath
from direct.gui.OnscreenText import OnscreenText

#Interrogate Module with the culling method
from TestInterrogate import *

loadPrcFileData('', 'threading-model /Draw')
loadPrcFileData('', 'sync-video False')


 
class Panda3dApp(ShowBase):
    def __init__(self, width, height, nbinstances):
        """Arguments:
        width -- width of the window
        height -- height of the window
        nbinstances -- nb of instances
        """

        self.nbinstances = nbinstances
        self.visible_instances = 0
        self.cullingmode = False
        self.shadow = True

        ShowBase.__init__(self)
        wp = WindowProperties()
        wp.setOrigin(50, 50)
        wp.setSize(width, height)
        base.openDefaultWindow(props=wp, gsg=None)
        
        #Initialize shaders
        self.MainInstancedNP = base.render.attachNewNode("MainInstancedDobj")
        self.ShaderInstances = []
        strVertexShader = Filename("HardwareInstancing_VS.glsl")
        strFragmentShader = Filename("HardwareInstancing_FS.glsl")
        v = open(strVertexShader.toOsSpecific()).read()
        f = open(strFragmentShader.toOsSpecific()).read()
        self.ShaderInstances  = [Shader.make(Shader.SLGLSL, v % i, f) for i in range(self.nbinstances + 1)]
        
        self.loadModels()

        cm = CardMaker("plane")
        cm.setFrame(-20, 20, -20, 20)
        cm.setHasNormals(True)
        self.m_2 = render.attachNewNode(cm.generate())
        self.m_2.setTwoSided(True)
        self.m_2.setP(270)
        self.m_2.setDepthOffset(-1)

        self.spotlight = Spotlight('light')
        spnp = render.attachNewNode(self.spotlight)
        self.spotlight.setColor(VBase4(1.0, 1.0, 0.0, 1))
        self.spotlight.setShadowCaster(True,512,512)
        lens = PerspectiveLens()
        self.spotlight.setLens(lens)
        render.setShaderAuto()
        spnp.setPos(-10, -5.0, 250)
        spnp.lookAt(self.s)
        render.setLight(spnp)
        colour = (0.5,0.8,0.5)
        expfog = Fog("Scene-wide exponential Fog object")
        expfog.setColor(*colour)
        expfog.setExpDensity(0.005)
        render.setFog(expfog)
        self.s.setShaderInput("has_fog",1.0)
        base.setBackgroundColor(*colour)
        base.setFrameRateMeter(True)

        OnscreenText(text = 'Hardware Instancing snippet - \nF1 to change the culling mode Python/C++', pos = (-0.9, .92), scale = 0.04, mayChange=True, fg=(1,1,1,1))
        self.text = OnscreenText(text = 'Python culling mode', pos = (-0.98, 0.80), scale = 0.04, mayChange=True, fg=(1,0.2,1,1))
        self.textnbinstances = OnscreenText(text = '', pos = (-0.98, 0.75), scale = 0.04, mayChange=True, fg=(1,0.2,1,1))

        base.cam.setPos(-20,-20,150);
        base.cam.lookAt(5,5,5)
 
        
        base.accept('f1',self.changeCullingMode)
        #base.accept('f2',self.takeScreenshot)
        
        base.run()
 
    def loadModels(self):
        self.s =  loader.loadModel("panda")
        self.s.reparentTo(render)
        self.s.setZ(10)
        bs = OmniBoundingVolume()
        self.s.node().setBounds(bs)
        self.s.node().setFinal(True)
        self.s.clearModelNodes()
        self.s.flattenLight()
        self.s.setDepthOffset(-1)
        self.s.hide() #Do not Show it before the Shader to update (remove the first instance effect)
        #Calculate the center / radius of the original model
        pt1, pt2 = self.s.getTightBounds()
        self.center = (pt1+pt2)*0.5
        self.ray = (LPoint3f(self.center)- LPoint3f(pt2)).length()
        for t in range(0,self.nbinstances):
            d = self.MainInstancedNP.attachNewNode('Instance'+str(t))
            d.setZ(10+t+random.uniform(0,10))
            d.setX(random.uniform(-10,10))
            d.setScale(random.uniform(0.3,0.5))

        taskMgr.add(self.UpdateShaderTask,"Update Shader")
 
   
    def DisplayNbInstances(self):
        text = str(self.visible_instances) + " visibles instances"
        self.textnbinstances.setText(text)


    def takeScreenshot(self):
        self.screenshot("HWInstancing.png")	

    def UpdateShaderTask(self, task):
        angleDegrees = task.time * 8.0
        angleRadians = angleDegrees * (pi / 180.0)
        for np in self.MainInstancedNP.getChildren():
             np.setHpr(angleDegrees,0.0,0.0)
        
        self.DisplayNbInstances()
        if self.cullingmode == True: #C++ culling mode
            self.s.show()
            shader_data = PTA_LMatrix4f()
            shader_data = TestInterrogate.updateShaderTask(self.MainInstancedNP,self.s,base.cam,self.center,self.ray) #Fonctionne
            self.visible_instances = len(shader_data)
            if self.visible_instances < 1: #The shader requires at least 1 instance.So when when nothing could be displayed, hide the model.
                self.s.hide() #Make sure there is no instance to display
            else:
                self.s.setShader(self.ShaderInstances[self.visible_instances])
                self.s.setInstanceCount(self.visible_instances)
                self.s.setShaderInput('shader_transformmatrix', shader_data)
            return Task.cont
        else: #Python culling mode
            self.s.show()
            lens = base.camLens
            lens.setNear(0.1)
            lens.setFar(5000.0)
            lensBounds = lens.makeBounds()
            bounds = None
            self.shader_data = PTA_LMatrix4f()
            t = 0
            for np in self.MainInstancedNP.getChildren():
                newcenter = np.getMat().xformPointGeneral(self.center) # Transform the model center in the instanciated np's World coordinates
                bounds = BoundingSphere(newcenter,self.ray*np.getScale().getX())
                bounds.xform(np.getParent().getMat(base.cam)) #Convert the bounds into the cam view space // Need to use getParent() to work 
                if lensBounds.contains(bounds):
                    self.shader_data.pushBack(UnalignedLMatrix4f())
                    self.shader_data[t] = UnalignedLMatrix4f(np.getMat(render))
                    t+=1
            
            self.visible_instances = len(self.shader_data)

            if self.visible_instances  < 1: #The shader requires at least 1 instance. So when when nothing could be displayed, hide the model.
                self.s.hide()
            else:
                self.s.setShader(self.ShaderInstances[self.visible_instances])
                self.s.setInstanceCount(self.visible_instances)
                self.s.setShaderInput('shader_transformmatrix', self.shader_data)
            return Task.cont

    def changeCullingMode(self):
        if self.cullingmode == True:
            self.cullingmode = False
            self.text.setText("Python culling mode")
        else:
            self.cullingmode = True
            self.text.setText("C++ culling mode")
# Test
if __name__ == "__main__":
    app = Panda3dApp(800,600,500)

