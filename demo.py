import panda3d
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, PointLight
from panda3d.core import TextNode, NodePath, LightAttrib
from panda3d.core import LVector3
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *

import random
import sys
import os
import shutil
import math
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import ClockObject
from panda3d.core import *


import simplepbr
#import gltf


panda3d.core.load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    filled-wireframe-apply-shader true
    #cursor-hidden true
    
    # As an optimization, set this to the maximum number of cameras
    # or lights that will be rendering the terrain at any given time.
    stm-max-views 16

    # Further optimize the performance by reducing this to the max
    # number of chunks that will be visible at any given time.
    stm-max-chunk-count 2048
    #textures-power-2 up
    view-frustum-cull false
""")

#panda3d.core.load_prc_file_data('', 'framebuffer-srgb true')
#panda3d.core.load_prc_file_data('', 'load-display pandadx9')#pandagl,p3tinydisplay,pandadx9,pandadx8
panda3d.core.load_prc_file_data('', 'show-frame-rate-meter true')
#panda3d.core.load_prc_file_data('', 'fullscreen true')
#loadPrcFileData('', 'coordinate-system y-up-left')

loadPrcFileData("", "basic-shaders-only #t")
#loadPrcFileData("", "gl-version 3 2")
#loadPrcFileData("", "notify-level-glgsg debug")
#loadPrcFileData("", "win-size 1920 1080")

class LookingDemo(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.disable_mouse()
        self.props = WindowProperties()
                                          
        self.pipeline = simplepbr.init(use_normal_maps=True,exposure=0.8,sdr_lut_factor=0,max_lights=8)
        #---adjustable parameters---
        self.mouse_sensitivity=50
        self.move_speed=0.1
        
        self.N_trees=1
        self.animation_on_flag=False#False
        self.shadow_on_flag=True
        
        # Camera param initializations
        self.cameraHeight = 1.5     # camera Height above ground
        self.cameraAngleH = 0     # Horizontal angle (yaw)
        self.cameraAngleP = 0   # Vertical angle (pitch)
        self.camLens.setNear(0.01)
        self.camLens.setFar(1500)
        self.camera.setPos(0,0,1)
        self.mouse_rotate_flag=0

        
        self.model_ground=loader.loadModel('grass_ground_1.glb')
        self.model_ground.reparentTo(self.render)
        self.model_tree=loader.loadModel('tree_1/Tree_1.gltf')
        #self.model_tree.reparentTo(self.render)
        self.custom_parent = NodePath("custom_parent")
        self.model_instances=[]
        self.animation_instances=[]
        self.choice_var=[0]
        self.current_choice=0
        self.current_actor=None
        self.current_animation=None
        self.placeholder=None
        #---display camera pos at bottom---
        self.bottom_cam_label=DirectLabel(text='CamPos: ',pos=(-1,1,-0.9),scale=0.05,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.8),text_bg=(0,0,0,0.2),frameColor=(0, 0, 0, 0.1))
        
        self.set_keymap()
        self.current_model_index=0
        self.load_environment_models()
        self.setupLights()
        taskMgr.add(self.camera_rotate, "camera_rotateTask")
        taskMgr.add(self.camera_move, "camera_move")
        #self.sun_rotate()
        
        base.accept('tab', base.bufferViewer.toggleEnable)

        self.create_top_level_main_gui()
        #self.hide_top_level_main_gui()


    def create_top_level_main_gui(self):

        self.MenuButton_1 = DirectButton(text = "Menu",scale=.06,command=self.menubuttonDef_1,pos=(-0.75, 1,0.95))
        self.create_parameters_gui()
        self.create_daylight_gui()
        self.ScrolledFrame_d1.hide()
        self.create_general_settings_gui()
        self.ScrolledFrame_d2.hide()
        
        self.create_dropdown_main_menu()
        self.menu_dropdown_1.hide()
        
    
    def show_top_level_main_gui(self):
        self.MenuButton_1.show()
        self.bottom_cam_label.show()
        
    def hide_top_level_main_gui(self):
        self.MenuButton_1.hide()
        self.bottom_cam_label.hide()                                                                                       

    def create_dropdown_main_menu(self):
        self.menu_dropdown_1=DirectScrolledFrame(
            canvasSize=(0, 1, -0.5, 0),  # left, right, bottom, top
            frameSize=(0, 1, -0.5, 0),
            pos=(-1,0,0.9),
            #pos=(-0.35, 1,0.95)
            frameColor=(0.3, 0.3, 0.3, 0.3)
        )
        
        self.CheckButton_1 = DirectCheckButton(
            parent=self.menu_dropdown_1.getCanvas(),
            text = "Parameters" ,
            text_align=TextNode.ALeft,
            scale=.06,
            command=self.cbuttondef_1,
            pos=(0.1,1,-0.1),
            frameColor=(0, 0, 0, 0.4),
            text_fg=(1, 1, 1, 0.9),
            indicatorValue=1
            )
        self.CheckButton_3 = DirectCheckButton(
            parent=self.menu_dropdown_1.getCanvas(),
            text = "General Settings" ,
            text_align=TextNode.ALeft,
            scale=.06,
            command=self.cbuttondef_b3,
            pos=(0.1, 1,-0.2),
            frameColor=(0, 0, 0, 0.4),
            text_fg=(1, 1, 1, 0.9),
            indicatorValue=0
            )
        self.CheckButton_4 = DirectCheckButton(
            parent=self.menu_dropdown_1.getCanvas(),
            text = "Light Settings" ,
            text_align=TextNode.ALeft,
            scale=.06,
            command=self.cbuttondef_b4,
            pos=(0.1, 1,-0.3),
            frameColor=(0, 0, 0, 0.4),
            text_fg=(1, 1, 1, 0.9),
            indicatorValue=0
            )
        
    def setChoice(self):
        self.current_choice=self.choice_var[0]

    def create_parameters_gui(self):
        self.ScrolledFrame_a1=DirectScrolledFrame(
            canvasSize=(-2, 2, -2, 2),  # left, right, bottom, top
            frameSize=(-2, 2, -2, 2),
            pos=(0.1,0,0),
            frameColor=(0.3, 0.3, 0.3, 0)
        )
        canvas_1=self.ScrolledFrame_a1.getCanvas()
        self.dlabel_a1 = DirectLabel(parent=canvas_1,text='Number of objects: ',pos=(-0.8,1,0.75),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_a2 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.4, 1,0.75), command=self.SetEntryText_a2,initialText="1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.CheckButton_a3 = DirectCheckButton(parent=canvas_1,text = "enable animation" ,scale=.06,command=self.cbuttondef_a3,pos=(-0.3, 1,0.65),frameColor=(0, 0, 0, 0.4),text_fg=(1, 1, 1, 0.9),text_align=TextNode.ALeft)
        self.CheckButton_a3_2 = DirectLabel(parent=canvas_1,text = "Select an Instancing Method:" ,scale=.06,pos=(-0.35, 1,0.55),frameColor=(0, 0, 0, 0.4),text_fg=(0.7, 0.7, 1, 0.9),text_align=TextNode.ALeft)
        self.dbuttons_a3_2 = [
            DirectRadioButton(parent=canvas_1,text='No Instancing',         variable=self.choice_var, value=[0],scale=0.06, pos=(-0.3, 1,0.45), command=self.setChoice,frameColor=(0, 0, 0, 0.4),text_fg=(1, 1, 1, 0.9),text_align=TextNode.ALeft),
            DirectRadioButton(parent=canvas_1,text='Instancing',            variable=self.choice_var, value=[1],scale=0.06, pos=(-0.3, 1,0.35), command=self.setChoice,frameColor=(0, 0, 0, 0.4),text_fg=(1, 1, 1, 0.9),text_align=TextNode.ALeft),
            DirectRadioButton(parent=canvas_1,text='Hardware Instancing',   variable=self.choice_var, value=[2],scale=0.06, pos=(-0.3, 1,0.25), command=self.setChoice,frameColor=(0, 0, 0, 0.4),text_fg=(1, 1, 1, 0.9),text_align=TextNode.ALeft)
        ]
        for button in self.dbuttons_a3_2:
            button.setOthers(self.dbuttons_a3_2)
        self.dbutton_a4 = DirectButton(parent=canvas_1,text=("Set"),scale=.06, pos=(-0.3, 1,0.15),command=self.ButtonDef_a4)
        
        
    def create_daylight_gui(self):
        self.ScrolledFrame_d1=DirectScrolledFrame(
            canvasSize=(-2, 2, -2, 2),  # left, right, bottom, top
            frameSize=(-2, 2, -2, 2),
            pos=(0.1,0,0),
            #pos=(-0.35, 1,0.95)
            frameColor=(0.3, 0.3, 0.3, 0)
        )
        canvas_1=self.ScrolledFrame_d1.getCanvas()
        #self.daylight_adjuster_gui=DirectFrame(pos=(-1.35, 1,1),frameSize=(0,0.8,-0.9,0),frameColor=(0, 0, 0, 0.1))
        
        self.dlabel_c1 = DirectLabel(parent=canvas_1,text='Ambient light: intensity',pos=(-0.8,1,0.75),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_c2 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.3, 1,0.75), command=self.SetEntryText_c1,initialText="0.1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        
        self.dlabel_c3=DirectLabel(parent=canvas_1,text='R (0 to 1): ',pos=(-0.7,1,0.65),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dlabel_c4=DirectLabel(parent=canvas_1,text='G (0 to 1): ',pos=(-0.7,1,0.55),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dlabel_c5=DirectLabel(parent=canvas_1,text='B (0 to 1): ',pos=(-0.7,1,0.45),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        
        self.dentry_c6 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,0.65), command=self.SetEntryText_c6,initialText="0.1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dentry_c7 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,0.55), command=self.SetEntryText_c7,initialText="0.1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dentry_c8 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,0.45), command=self.SetEntryText_c8,initialText="0.1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)

        self.dlabel_c9 = DirectLabel(parent=canvas_1,text='Directional light(sun): intensity',pos=(-0.8,1,0.35),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_c10 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.3, 1,0.35), command=self.SetEntryText_c10,initialText="1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        
        self.dlabel_c11=DirectLabel(parent=canvas_1,text='R (0 to 1): ',pos=(-0.7,1,0.25),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dlabel_c12=DirectLabel(parent=canvas_1,text='G (0 to 1): ',pos=(-0.7,1,0.15),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dlabel_c13=DirectLabel(parent=canvas_1,text='B (0 to 1): ',pos=(-0.7,1,0.05),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        
        self.dentry_c14 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,0.25), command=self.SetEntryText_c14,initialText="1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dentry_c15 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,0.15), command=self.SetEntryText_c15,initialText="1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dentry_c16 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,0.05), command=self.SetEntryText_c16,initialText="1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)

        self.dlabel_c17=DirectLabel(parent=canvas_1,text='H (0 to 360): ',pos=(-0.7,1,-0.05),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dlabel_c18=DirectLabel(parent=canvas_1,text='P (0 to 360): ',pos=(-0.7,1,-0.15),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dlabel_c19=DirectLabel(parent=canvas_1,text='R (0 to 360): ',pos=(-0.7,1,-0.25),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        
        self.dentry_c20 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,-0.05), command=self.SetEntryText_c20,initialText="0", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dentry_c21 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,-0.15), command=self.SetEntryText_c21,initialText="0", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dentry_c22 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=10,pos=(-0.35, 1,-0.25), command=self.SetEntryText_c22,initialText="0", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)

        self.dlabel_c23=DirectLabel(parent=canvas_1,text='X: ',pos=(-1.3,1,-0.35),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_c24 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=8,pos=(-1.25, 1,-0.35), command=self.SetEntryText_c24,initialText="0", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dlabel_c25=DirectLabel(parent=canvas_1,text='Y: ',pos=(-0.6,1,-0.35),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_c26 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=8,pos=(-0.55, 1,-0.35), command=self.SetEntryText_c26,initialText="0", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dlabel_c27=DirectLabel(parent=canvas_1,text='Z: ',pos=(0.1,1,-0.35),scale=0.06,text_align=TextNode.ACenter,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_c28 = DirectEntry(parent=canvas_1,text = "", scale=0.06,width=8,pos=(0.55, 1,-0.35), command=self.SetEntryText_c28,initialText="0", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)

    def create_general_settings_gui(self):
        self.ScrolledFrame_d2=DirectScrolledFrame(
            canvasSize=(-2, 2, -2, 2),  # left, right, bottom, top
            frameSize=(-2, 2, -2, 2),
            pos=(0.1,0,0),
            #pos=(-0.35, 1,0.95)
            frameColor=(0.3, 0.3, 0.3, 0)
        )
        canvas_2=self.ScrolledFrame_d2.getCanvas()
        #self.daylight_adjuster_gui=DirectFrame(pos=(-1.35, 1,1),frameSize=(0,0.8,-0.9,0),frameColor=(0, 0, 0, 0.1))
        
        self.dlabel_d1 = DirectLabel(parent=canvas_2,text='Mouse Sensitivity (0-100,default 50): ',pos=(-1.1,1,0.75),scale=0.06,text_align=TextNode.ALeft,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_d2 = DirectEntry(parent=canvas_2,text = "", scale=0.06,width=10,pos=(0.3, 1,0.75), command=self.SetEntryText_d1,initialText="50", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        self.dlabel_d3 = DirectLabel(parent=canvas_2,text='Mouse Speed (0-1,default 0.1): ',pos=(-1.1,1,0.65),scale=0.06,text_align=TextNode.ALeft,text_fg=(1, 1, 1, 0.9),text_bg=(0,0,0,0.3),frameColor=(0, 0, 0, 0.2))
        self.dentry_d4 = DirectEntry(parent=canvas_2,text = "", scale=0.06,width=10,pos=(0.3, 1,0.65), command=self.SetEntryText_d4,initialText="0.1", numLines = 1, focus=0,frameColor=(0,0,0,0.3),text_fg=(1, 1, 1, 0.9),focusInCommand=self.focusInDef,focusOutCommand=self.focusOutDef)
        
        
    def cbuttondef_1(self,status):
        if status:
            self.ScrolledFrame_a1.show()
        else:
            self.ScrolledFrame_a1.hide()


    def cbuttondef_a3(self,status):
        if status:
            self.animation_on_flag=True
        else:
            self.animation_on_flag=False
            
            
    def cbuttondef_b3(self,status):
        if status:
            self.ScrolledFrame_d2.show()
        else:
            self.ScrolledFrame_d2.hide()

    def cbuttondef_b4(self,status):
        if status:
            self.ScrolledFrame_d1.show()
        else:
            self.ScrolledFrame_d1.hide()
            
    def SetEntryText_a2(self,textEntered):
        try:
            self.N_trees=int(textEntered)
        except:
            print('entry1 error')

    def SetEntryText_c1(self,textEntered):
        try:
            self.ambientLight_Intensity=float(textEntered)
            cur_color=self.ambientLight.getColor()
            self.ambientLight.setColor((self.ambientLight_Intensity,self.ambientLight_Intensity,self.ambientLight_Intensity, 1))
            self.dentry_c6.enterText(str(self.ambientLight_Intensity))
            self.dentry_c7.enterText(str(self.ambientLight_Intensity))
            self.dentry_c8.enterText(str(self.ambientLight_Intensity))
        except ValueError:
            print('value entered in entry c1 is not number')

    def SetEntryText_d1(self,textEntered):
        try:
            self.mouse_sensitivity=float(textEntered)
        except ValueError:
            print('value entered in entry d1 is not number')

    def SetEntryText_d4(self,textEntered):
        try:
            self.move_speed=float(textEntered)
        except ValueError:
            print('value entered in entry d4 is not number')
            
    def SetEntryText_c6(self,textEntered):
        try:
            self.dentry_c6.enterText(textEntered)
            cur_color=self.ambientLight.getColor()
            self.ambientLight.setColor((float(textEntered),cur_color[1],cur_color[2], 1))
        except ValueError:
            print('value entered in entry6 is not number')

    def SetEntryText_c7(self,textEntered):
        try:
            self.dentry_c7.enterText(textEntered)
            cur_color=self.ambientLight.getColor()
            self.ambientLight.setColor((cur_color[0],float(textEntered),cur_color[2], 1))
        except ValueError:
            print('value entered in entry7 is not number')

    def SetEntryText_c8(self,textEntered):
        try:
            self.dentry_c8.enterText(textEntered)
            cur_color=self.ambientLight.getColor()
            self.ambientLight.setColor((cur_color[0],cur_color[1],float(textEntered), 1))
        except ValueError:
            print('value entered in entry8 is not number')            

    def SetEntryText_c10(self,textEntered):
        try:
            self.directionalLight_intensity=float(textEntered)
            cur_color=self.directionalLight.getColor()
            self.directionalLight.setColor((self.directionalLight_intensity,self.directionalLight_intensity,self.directionalLight_intensity, 1))
            self.dentry_c14.enterText(str(self.directionalLight_intensity))
            self.dentry_c15.enterText(str(self.directionalLight_intensity))
            self.dentry_c16.enterText(str(self.directionalLight_intensity))
        except ValueError:
            print('value entered in entry c1 is not number')

    def SetEntryText_c14(self,textEntered):
        try:
            self.dentry_c14.enterText(textEntered)
            cur_color=self.directionalLight.getColor()
            self.directionalLight.setColor((float(textEntered),cur_color[1],cur_color[2], 1))
        except ValueError:
            print('value entered in entry is not number')

    def SetEntryText_c15(self,textEntered):
        try:
            self.dentry_c15.enterText(textEntered)
            cur_color=self.directionalLight.getColor()
            self.directionalLight.setColor((cur_color[0],float(textEntered),cur_color[2], 1))
        except ValueError:
            print('value entered in entry is not number')

    def SetEntryText_c16(self,textEntered):
        try:
            self.dentry_c16.enterText(textEntered)
            cur_color=self.directionalLight.getColor()
            self.directionalLight.setColor((cur_color[0],cur_color[1],float(textEntered), 1))
        except ValueError:
            print('value entered in entry is not number')            

    def SetEntryText_c20(self,textEntered):
        try:
            self.dentry_c20.enterText(textEntered)
            cur_color=self.dlight1.getHpr()
            self.dlight1.setHpr(float(textEntered),cur_color[1],cur_color[2])
        except ValueError:
            print('value entered in entry is not number')

    def SetEntryText_c21(self,textEntered):
        try:
            self.dentry_c21.enterText(textEntered)
            cur_color=self.dlight1.getHpr()
            self.dlight1.setHpr(cur_color[0],float(textEntered),cur_color[2])
        except ValueError:
            print('value entered in entry is not number')

    def SetEntryText_c22(self,textEntered):
        try:
            self.dentry_c22.enterText(textEntered)
            cur_color=self.dlight1.getHpr()
            self.dlight1.setHpr(cur_color[0],cur_color[1],float(textEntered))
        except ValueError:
            print('value entered in entry is not number')            

    def SetEntryText_c24(self,textEntered):
        try:
            self.dentry_c24.enterText(textEntered)
            cur_color=self.dlight1.getPos()
            self.dlight1.setPos(float(textEntered),cur_color[1],cur_color[2])
        except ValueError:
            print('value entered in entry is not number')

    def SetEntryText_c26(self,textEntered):
        try:
            self.dentry_c26.enterText(textEntered)
            cur_color=self.dlight1.getPos()
            self.dlight1.setPos(cur_color[0],float(textEntered),cur_color[2])
        except ValueError:
            print('value entered in entry is not number')

    def SetEntryText_c28(self,textEntered):
        try:
            self.dentry_c28.enterText(textEntered)
            cur_color=self.dlight1.getPos()
            self.dlight1.setPos(cur_color[0],cur_color[1],float(textEntered))
        except ValueError:
            print('value entered in entry is not number')


    def focusInDef(self):
        #self.ignoreAll()
        self.accept('escape', sys.exit)
       
    def focusOutDef(self):
        #self.set_keymap()
        pass

    def ButtonDef_a4(self):
        try:
            textEntered=self.dentry_a2.get()
            self.N_trees=int(textEntered)
            self.dentry_a2['focus']=0
        except:
            print('entry1 error')
        self.load_environment_models()

    def menubuttonDef_1(self):
        if self.menu_dropdown_1.isHidden():
            self.menu_dropdown_1.show()
        else:
            self.menu_dropdown_1.hide()


    def cleanup_all(self):
        #---choice 0 cleanup---
        if self.custom_parent.getNumChildren() > 0:
            for child in self.custom_parent.getChildren():
                child.removeNode()
                child=None
            for mdl in self.model_instances:
                mdl.cleanup()
            del self.model_instances
            del self.animation_instances
            
        self.model_instances=[]
        self.animation_instances=[]
        
        #---choice 1 cleanup---
        #self.current_actor=None
        #self.current_animation=None
        #self.placeholder=None
        # Later, to clean up
        if self.placeholder is not None:
            self.placeholder.removeNode()
            self.placeholder.clear()
            self.placeholder=None
        if self.current_actor is not None:
            self.current_actor.cleanup()
            self.current_actor.removeNode()
            self.current_actor=None
    
    def load_environment_models(self):
        if self.current_choice==0:
            self.cleanup_all()
            for i in range(self.N_trees):
                #copied_model_0=loader.loadModel('tree_1/Tree_1.gltf')
                copied_model_0=self.model_tree.copyTo(self.custom_parent)
                copied_model = Actor(copied_model_0)
                copied_model.reparentTo(self.render)
                copied_model.setPos(30-random.random()*60,30-random.random()*60,0)
                self.model_instances.append(copied_model)
            if self.animation_on_flag:
                for mdl in self.model_instances:
                    self.animation1 = mdl.getAnimControl('Action')
                    self.animation_instances.append(self.animation1)
                    self.animation_instances[-1].loop(0)
        if self.current_choice==1:
            self.cleanup_all()
            
            self.current_actor = Actor(self.model_tree)
            if self.animation_on_flag:
                self.current_animation=self.current_actor.getAnimControl('Action')
                self.current_animation.loop(0)
            for i in range(self.N_trees):
                self.placeholder = render.attachNewNode("Tree_placeholder")
                self.placeholder.setPos(30-random.random()*60,30-random.random()*60,0)
                self.current_actor.instanceTo(self.placeholder)
        if self.current_choice==2:
            self.cleanup_all()
            
            # An array for N matrices.
            instanced_array = PTA_LMatrix4f.emptyArray(self.N_trees)
            for i in range(self.N_trees):
                # Creating a transformation for 1 copy.
                scale = LMatrix4f().scale_mat((1, 1, 1))
                rotate_x = LMatrix4f().rotate_mat(0, (1, 0, 0))
                rotate_y = LMatrix4f().rotate_mat(0, (0, 1, 0))
                #rotate_z = LMatrix4f().rotate_mat(45, (0, 0, 1))
                rotate_z = LMatrix4f().rotate_mat(0, (0, 0, 1))
                x_rand=int(30-random.random()*60)
                y_rand=int(30-random.random()*60)
                translate = LMatrix4f().translate_mat((x_rand, y_rand, 0))

                transform = scale * ( rotate_y * rotate_x * rotate_z) * translate
                # Add the transformation matrix for i th copy to the array.
                instanced_array.set_element(i, transform)

            self.current_actor = Actor(self.model_tree)
            if self.animation_on_flag:
                self.current_animation=self.current_actor.getAnimControl('Action')
                self.current_animation.loop(0)
            # A hack to disable culling.
            self.current_actor.node().set_bounds(OmniBoundingVolume())
            self.current_actor.node().set_final(True)
            self.current_actor.reparent_to(render)
            # We inform the GPU that this geometry needs to be drawn in multiples of the specified number.
            self.current_actor.set_instance_count(self.N_trees)
            self.current_actor.set_shader(Shader.load(Shader.SL_GLSL, vertex = 'shaders/instancing_vertex.glsl', fragment = 'shaders/instancing_fragment.glsl'))
            # Passing an array of two matrices to the shader.
            self.current_actor.set_shader_input("instanced_object", ShaderBuffer('DataBuffer', StringStream(instanced_array).get_data(), GeomEnums.UH_static))
                
    def set_keymap(self):
        self.keyMap = {"move_forward": 0, "move_backward": 0, "move_left": 0, "move_right": 0,"gravity_on":1,"show_gui":1,"right_click":0}
        self.accept('escape', sys.exit)
        self.accept("w", self.setKey, ["move_forward", True])
        self.accept("s", self.setKey, ["move_backward", True])
        self.accept("w-up", self.setKey, ["move_forward", False])
        self.accept("s-up", self.setKey, ["move_backward", False])
        self.accept("a", self.setKey, ["move_left", True])
        self.accept("d", self.setKey, ["move_right", True])
        self.accept("a-up", self.setKey, ["move_left", False])
        self.accept("d-up", self.setKey, ["move_right", False])
        self.accept("mouse3", self.setKey, ["right_click", True])
        self.accept("mouse3-up", self.setKey, ["right_click", False])
        self.accept("b", self.setKey, ["gravity_on", None])
        self.accept("m", self.setKey, ["show_gui", True])                                                                
        
                
    # Records the state of the keys
    def setKey(self, key, value):
        
        if key=="gravity_on":
            self.keyMap[key]=not(self.keyMap[key])
        elif key=="show_gui":
            self.keyMap[key]=not(self.keyMap[key])
            if self.keyMap[key]==True:
                self.show_top_level_main_gui()
            else:
                self.hide_top_level_main_gui()                             
        else:
            self.keyMap[key] = value


    def setupLights(self):  # Sets up some default lighting
        self.ambientLight = AmbientLight("ambientLight")
        self.ambientLight_Intensity=0.3
        self.ambientLight.setColor((self.ambientLight_Intensity,self.ambientLight_Intensity,self.ambientLight_Intensity, 1))
        self.render.setLight(self.render.attachNewNode(self.ambientLight))
        self.directionalLight = DirectionalLight("directionalLight_1")
        self.directionalLight_intensity=5
        self.directionalLight.setColor((self.directionalLight_intensity,self.directionalLight_intensity,self.directionalLight_intensity, 1))
        if self.shadow_on_flag:
            self.directionalLight.setShadowCaster(True, 512, 512)
        self.dlight1=self.render.attachNewNode(self.directionalLight)
        self.dlight1.setHpr(0, -45, 0)
        self.dlight1.setPos(0,0,20)
                     
        self.dlight1.node().get_lens().set_film_size(50, 50)
        self.dlight1.node().get_lens().setNearFar(1, 50)
        self.dlight1.node().show_frustum()
        self.render.setLight(self.dlight1)
        
                                             
    def camera_rotate(self,task):
        # Check to make sure the mouse is readable
        if self.mouseWatcherNode.hasMouse():
            if self.keyMap['right_click']==True:
                # get the mouse position as a LVector2. The values for each axis are from -1 to
                # 1. The top-left is (-1,-1), the bottom right is (1,1)
                mpos = self.mouseWatcherNode.getMouse()
                if self.mouse_rotate_flag==0:
                    self.props.setCursorHidden(True)
                    self.win.requestProperties(self.props)
                    self.win.movePointer(0, int(self.win.getXSize() / 2), int(self.win.getYSize() / 2))
                    self.mouse_rotate_flag=1
                mouse = self.win.getPointer(0)
                mx, my = mouse.getX(), mouse.getY()
                # Reset mouse to center to prevent edge stopping
                self.win.movePointer(0, int(self.win.getXSize() / 2), int(self.win.getYSize() / 2))

                # Calculate mouse delta
                dx = mx - int(self.win.getXSize() / 2)
                dy = my - int(self.win.getYSize() / 2)

                # Update camera angles based on mouse movement
                self.cameraAngleH -= dx * self.mouse_sensitivity * globalClock.getDt()
                self.cameraAngleP -= dy * self.mouse_sensitivity * globalClock.getDt()

                # Clamp pitch to avoid flipping
                self.cameraAngleP = max(-90, min(90, self.cameraAngleP))
                
                #self.camera.setPos(camX, camY, camZ)
                self.camera.setHpr(self.cameraAngleH, self.cameraAngleP, 0)

            else:
                self.mouse_rotate_flag=0
                self.props.setCursorHidden(False)
                self.win.requestProperties(self.props)
        return Task.cont  # Task continues infinitely

    def sun_rotate(self):
        self.dlight1_rot=self.dlight1.hprInterval(10.0, Point3(0, 360, 0))
        self.dlight1_rot.loop()
        return 1
    
    def camera_move(self,task):
        pos_val=self.camera.getPos()
        heading=(math.pi*(self.camera.getH()))/180
        pitch=(math.pi*(self.camera.getP()))/180
        newval_1=pos_val[1]
        newval_2=pos_val[0]
        newval_3=pos_val[2]
        if self.keyMap['move_forward']==True:
            newval_1=pos_val[1]+self.move_speed*math.cos(heading)*math.cos(pitch)
            newval_2=pos_val[0]-self.move_speed*math.sin(heading)*math.cos(pitch)
            newval_3=pos_val[2]+self.move_speed*math.sin(pitch)
        if self.keyMap['move_backward']==True:
            newval_1=pos_val[1]-self.move_speed*math.cos(heading)*math.cos(pitch)
            newval_2=pos_val[0]+self.move_speed*math.sin(heading)*math.cos(pitch)
            newval_3=pos_val[2]-self.move_speed*math.sin(pitch)
        if self.keyMap['move_left']==True==1:
            newval_1=pos_val[1]+self.move_speed*math.cos(heading+(math.pi/2))
            newval_2=pos_val[0]-self.move_speed*math.sin(heading+(math.pi/2))
        if self.keyMap['move_right']==True:
            newval_1=pos_val[1]-self.move_speed*math.cos(heading+(math.pi/2))
            newval_2=pos_val[0]+self.move_speed*math.sin(heading+(math.pi/2))
        if self.keyMap['gravity_on']==True:
            newval_3=1
        self.camera.setPos(newval_2,newval_1,newval_3)
        self.bottom_cam_label.setText('CamPos: %0.2f,%0.2f,%0.2f'%(newval_2,newval_1,newval_3))
        return Task.cont



demo=LookingDemo()
demo.run()


