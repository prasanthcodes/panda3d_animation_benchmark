from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from panda3d.core import NodePath, AmbientLight, DirectionalLight

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set up the camera
        #self.disableMouse()
        self.camera.setPos(0, -10, 2)

        # Load the GLB model as an Actor
        self.actor = Actor("tree_1/Tree_1.gltf")  # Replace with your GLB file path
        self.actor.reparentTo(self.render)

        # List available animations
        animations = self.actor.getAnimNames()
        if not animations:
            print("No animations found in the GLB model")
            return

        print("Available animations:", animations)
        anim_name = 'Action'  # Use the first animation

        # Get animation control
        anim_control = self.actor.getAnimControl(anim_name)
        if not anim_control:
            print("Failed to get animation control")
            return

        # Animation parameters
        fps = 30  # Adjust if your animation has a different FPS
        num_frames = 60
        frame_duration = 1.0 / fps
        anim_duration = num_frames * frame_duration  # Duration of 60 frames in seconds

        # Check total frames
        total_frames = anim_control.getNumFrames()
        print(f"Total frames in animation: {total_frames}")
        if total_frames < num_frames:
            print(f"Warning: Animation has only {total_frames} frames, less than 60")
            num_frames = total_frames  # Adjust to available frames
            anim_duration = num_frames * frame_duration

        # Method 1: Use setPlayRate for reverse playback
        def play_forward():
            print("Playing forward: frames 0 to", num_frames)
            self.actor.setPlayRate(1, anim_name)  # Normal speed
            self.actor.play(anim_name, fromFrame=0, toFrame=num_frames)

        def play_reverse():
            print("Playing reverse: frames", num_frames, "to 0")
            self.actor.setPlayRate(-1, anim_name)  # Reverse speed
            self.actor.play(anim_name, fromFrame=0, toFrame=num_frames)

        # Create sequence for forward and reverse
        self.anim_sequence = Sequence(
            Func(play_forward),
            Wait(anim_duration-2*frame_duration),
            Func(play_reverse),
            Wait(anim_duration-2*frame_duration)
        )

        # Alternative Method 2: Manual reverse playback using pose() (uncomment to try)
        """
        def play_reverse_manual():
            print("Playing reverse manually: frames", num_frames, "to 0")
            for frame in range(num_frames, -1, -1):
                self.actor.pose(anim_name, frame)
                self.taskMgr.step()  # Update the scene
                self.taskMgr.doMethodLater(frame_duration, lambda task: None, 'wait')
        self.anim_sequence = Sequence(
            Func(play_forward),
            Wait(anim_duration),
            Func(play_reverse_manual),
            Wait(anim_duration)
        )
        """

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

# Run the application
app = MyApp()
app.run()