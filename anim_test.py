from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task import Task
from panda3d.core import NodePath, AmbientLight, DirectionalLight

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set up the camera
        self.disableMouse()
        self.camera.setPos(0, -10, 2)

        # Load the GLB model as an Actor
        self.actor = Actor("tree_1/Tree_1.gltf")  # Replace with your GLB file path
        self.actor.reparentTo(self.render)

        # List available animations
        animations = self.actor.getAnimNames()
        if not animations:
            print("Error: No animations found in the GLB model")
            return

        print("Available animations:", animations)
        self.anim_name = animations[0]  # Use the first animation

        # Get animation control
        self.anim_control = self.actor.getAnimControl(self.anim_name)
        if not self.anim_control:
            print("Error: Failed to get animation control for", self.anim_name)
            return

        # Animation parameters
        self.fps = 30  # Adjust if your animation has a different FPS
        self.num_frames = 60
        self.frame_duration = 1.0 / self.fps
        self.anim_duration = self.num_frames * self.frame_duration

        # Check total frames
        self.total_frames = self.anim_control.getNumFrames()
        print(f"Total frames in animation: {self.total_frames}")
        if self.total_frames < self.num_frames:
            print(f"Warning: Animation has only {self.total_frames} frames, adjusting to match")
            self.num_frames = self.total_frames
            self.anim_duration = self.num_frames * self.frame_duration

        # Define forward playback
        def play_forward():
            print("Playing forward: frames 0 to", self.num_frames)
            self.actor.setPlayRate(1, self.anim_name)  # Ensure normal speed
            self.actor.play(self.anim_name, fromFrame=0, toFrame=self.num_frames)




        # Define reverse playback using pose() in a task
        def start_reverse():
            print("Starting reverse playback: frames", self.num_frames, "to 0")
            self.current_frame = self.num_frames
            self.taskMgr.add(self.reverse_task, "reverse_task")
            return 1
            
        # Create sequence
        self.anim_sequence = Sequence(
            Func(play_forward),
            Wait(self.anim_duration),
            Func(start_reverse),
            Wait(self.anim_duration),
        )

        # Start the sequence
        self.anim_sequence.loop()

        # Add lighting
        ambient_light = self.render.attachNewNode(AmbientLight("ambient_light"))
        ambient_light.node().setColor((0.3, 0.3, 0.3, 1))
        self.render.setLight(ambient_light)

        directional_light = self.render.attachNewNode(DirectionalLight("directional_light"))
        directional_light.node().setDirection((-1, -1, -1))
        directional_light.node().setColor((0.7, 0.7, 0.7, 1))
        self.render.setLight(directional_light)

    # Task to manually play frames in reverse
    def reverse_task(self, task):
        if self.current_frame <= 0:
            print("Finished reverse playback")
            return Task.done
        print(f"Posing frame: {self.current_frame}")
        self.actor.pose(self.anim_name, self.current_frame)
        self.current_frame -= 1
        self.taskMgr.doMethodLater(
            0.1,self.do_nothing, 'do_nothing', extraArgs=[]
        )
        return Task.cont
        
    def do_nothing(self):
        pass
# Run the application
app = MyApp()
app.run()