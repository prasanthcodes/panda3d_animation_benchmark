# Based on Epihaius's work.
# https://discourse.panda3d.org/viewtopic.php?f=8&t=19317&p=108866#p108866
# Revision: adding Equator, Center, Standing slices rotation.

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import LerpHprInterval, Func, Sequence


def createCube(parent, x, y, z, position, cubeMembership, walls):

    vertexFormat = GeomVertexFormat.getV3n3cp()
    vertexData = GeomVertexData("cube_data", vertexFormat, Geom.UHStatic)
    tris = GeomTriangles(Geom.UHStatic)

    posWriter = GeomVertexWriter(vertexData, "vertex")
    colWriter = GeomVertexWriter(vertexData, "color")
    normalWriter = GeomVertexWriter(vertexData, "normal")

    vertexCount = 0

    for direction in (-1, 1):

        for i in range(3):

            normal = VBase3()
            normal[i] = direction
            rgb = [0., 0., 0.]
            rgb[i] = 1.

            if direction == 1:
                rgb[i-1] = 1.

            r, g, b = rgb
            color = (r, g, b, 1.)

            for a, b in ( (-1., -1.), (-1., 1.), (1., 1.), (1., -1.) ):

                pos = VBase3()
                pos[i] = direction
                pos[(i + direction) % 3] = a
                pos[(i + direction * 2) % 3] = b

                posWriter.addData3f(pos)
                colWriter.addData4f(color)
                normalWriter.addData3f(normal)

            vertexCount += 4

            tris.addVertices(vertexCount - 2, vertexCount - 3, vertexCount - 4)
            tris.addVertices(vertexCount - 4, vertexCount - 1, vertexCount - 2)

    geom = Geom(vertexData)
    geom.addPrimitive(tris)
    node = GeomNode("cube_node")
    node.addGeom(geom)
    cube = parent.attachNewNode(node)
    cube.setScale(.4)
    cube.setPos(x, y, z)
    membership = set() # the walls this cube belongs to
    position[cube] = [x, y, z]
    cubeMembership[cube] = membership
    # In Panda3D, X axis straightly points to right.
    # Y axis goes inside perpendicular to the screen.
    # Z axis is pointing up.
    
    
    if x == 1:
        walls["right"].append(cube)
        membership.add("right")
    elif x == -1:
        walls["left"].append(cube)
        membership.add("left")
    elif x == 0:
        walls["center"].append(cube)
        membership.add("center")
        
    if y == 1:
        walls["back"].append(cube)
        membership.add("back")
    elif y == -1:
        walls["front"].append(cube)
        membership.add("front")
    elif y==0:
        walls["standing"].append(cube)
        membership.add("standing")
        
    if z == -1:
        walls["down"].append(cube)
        membership.add("down")
    elif z == 1:
        walls["up"].append(cube)
        membership.add("up")
    elif z==0:
        walls["equator"].append(cube)
        membership.add("equator")

    return cube


class MyApp(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        
        walls = {}
        pivots = {}
        rotations = {}
        position = {}
        cubeMembership = {}
        #Equator slice is the slice between up and down faces, center slice between left and right faces, standing slice the left one,
        wallIDs = ("front", "back", "left", "right", "down", "up", "equator", "center", "standing")
        hprs = {}
        # VBase(Z,X,Y) if spin around Z, VBase3(90., 0., 0.).
        # The degree is positive following the right hand rule.
        hprs["right"] = VBase3(0., -90., 0.)
        hprs["center"] = VBase3(0., -90., 0.) # The ratation direction of the standing slice follows the front face.
        hprs["left"] = VBase3(0., 90., 0.)
        hprs["back"] = VBase3(0., 0., -90.)
        hprs["front"] = VBase3(0., 0., 90.)
        hprs["standing"] = VBase3(0., 0., 90.)# The ratation direction of the center slice follows the right face.
        hprs["down"] = VBase3(90., 0., 0.)
        hprs["up"] = VBase3(-90., 0., 0.)
        hprs["equator"] = VBase3(-90., 0., 0.) # The ratation direction of the equator slice follows the up face.      
        wallRotate = {}
        wallNegRotate = {}
        # Each rotation is a matrix.
        # The positive front rotation and the negative back rotation have the same matrix.
        # The standing slice follows the rules of the front face.
        
        wallRotate["right"] = wallRotate["center"] = wallNegRotate["left"] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
        wallRotate["left"] = wallNegRotate["right"] = wallNegRotate["center"] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]

        wallRotate["back"] = wallNegRotate["standing"] = wallNegRotate["front"] = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
        wallRotate["front"] = wallRotate["standing"] = wallNegRotate["back"] = [[0, 0, -1], [0, 1, 0], [1, 0, 0]]
        
        wallRotate["up"] = wallRotate["equator"] = wallNegRotate["down"] = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
        wallRotate["down"] = wallNegRotate["equator"] = wallNegRotate["up"] = [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]
        

        for wallID in wallIDs:
            walls[wallID] = []
            pivots[wallID] = self.render.attachNewNode('pivot_%s' % wallID)
            rotations[wallID] = {"hpr": hprs[wallID]}
        #print walls
        #print pivots
        #print rotations
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for z in (-1, 0, 1):
                    createCube(self.render, x, y, z, position, cubeMembership, walls)

        self.directionalLight = DirectionalLight('directionalLight')
        self.directionalLightNP = self.cam.attachNewNode(self.directionalLight)
        self.directionalLightNP.setHpr(20., -20., 0.) 
        self.render.setLight(self.directionalLightNP)
        self.cam.setPos(7., -10., 4.)
        self.cam.lookAt(0., 0., 0.)

        def reparentCubes(wallID):
            pivot = pivots[wallID]
            children = pivot.getChildren()
            children.wrtReparentTo(self.render)
            pivot.clearTransform()
            children.wrtReparentTo(pivot)
            for cube in walls[wallID]:
                cube.wrtReparentTo(pivot)

        def updateCubeMembership(wallID, negRotation=False):
            for cube in walls[wallID]:
                oldMembership = cubeMembership[cube]
                # print "oldMembership",oldMembership
                # print "old position", position[cube]
                newMembership = set()
                cubeMembership[cube] = newMembership
                
                # X cordinate
                newPos = 0
                if not negRotation:                    
                    for j in range(3):                        
                        newPos = newPos + int(position[cube][j]) * int(wallRotate[wallID][j][0])
                else:
                    for j in range(3):
                        newPos = newPos + int(position[cube][j]) * int(wallNegRotate[wallID][j][0])

                if newPos == 1:
                    newMembership.add("right")
                elif newPos == -1:
                    newMembership.add("left")
                elif newPos == 0:
                    newMembership.add("center")
                newPosX = newPos


                # Y cordinate
                newPos = 0
                if not negRotation:                    
                    for j in range(3):                        
                        newPos = newPos + int(position[cube][j]) * int(wallRotate[wallID][j][1])
                else:
                    for j in range(3):
                        newPos = newPos + int(position[cube][j]) * int(wallNegRotate[wallID][j][1])

                if newPos == 1:
                    newMembership.add("back")
                elif newPos == -1:
                    newMembership.add("front")
                elif newPos == 0:
                    newMembership.add("standing")
                newPosY = newPos

                
                # Z cordinate
                newPos = 0
                if not negRotation:                    
                    for j in range(3):
                        newPos = newPos + int(position[cube][j]) * int(wallRotate[wallID][j][2])
                else:
                    for j in range(3):
                        newPos = newPos + int(position[cube][j]) * int(wallNegRotate[wallID][j][2])

                if newPos == 1:
                    newMembership.add("up")
                elif newPos == -1:
                    newMembership.add("down")
                elif newPos == 0:
                    newMembership.add("equator")
                newPosZ=newPos
                
                position[cube] = [newPosX, newPosY, newPosZ]
                # print "newMembership",newMembership
                # print "new position:", position[cube]
                
                for oldWallID in oldMembership - newMembership:
                    walls[oldWallID].remove(cube)
                for newWallID in newMembership - oldMembership:
                    walls[newWallID].append(cube)
                
                
        self.seq = Sequence()

        def addInterval(wallID, negRotation=False):
            self.seq.append(Func(reparentCubes, wallID))
            rot = rotations[wallID]["hpr"]
            if negRotation:
                rot = rot * -1.
            #Revision: 1.0 is the speed of rotation, 2.5 is slower.
            self.seq.append(LerpHprInterval(pivots[wallID], 1.0, rot))
            self.seq.append(Func(updateCubeMembership, wallID, negRotation))
            print ("Added " + ("negative " if negRotation else "") + wallID + " rotation.")
 

        def acceptInput():# Revision: top-->up, bottom-->down. Reverse rotation: back,up,right 
            # <F> adds a positive Front rotation
            self.accept("f", lambda: addInterval("front"))
            # <Shift+F> adds a negative Front rotation
            self.accept("shift-f", lambda: addInterval("front", True))
            # <B> adds a positive Back rotation
            self.accept("b", lambda: addInterval("back"))
            # <Shift+B> adds a negative Back rotation
            self.accept("shift-b", lambda: addInterval("back", True))


            
            # <L> adds a positive Left rotation
            self.accept("l", lambda: addInterval("left"))
            # <Shift+L> adds a negative Left rotation
            self.accept("shift-l", lambda: addInterval("left", True))
            # <R> adds a positive Right rotation
            self.accept("r", lambda: addInterval("right"))
            # <Shift+R> adds a negative Right rotation
            self.accept("shift-r", lambda: addInterval("right", True))


            
            # <D> adds d positive Down rotation
            self.accept("d", lambda: addInterval("down"))
            # <Shift+D> adds a negative Down rotation
            self.accept("shift-d", lambda: addInterval("down", True))
            # <U> adds a positive Up rotation
            self.accept("u", lambda: addInterval("up"))
            # <Shift+U> adds a negative Up rotation
            self.accept("shift-u", lambda: addInterval("up", True))
            
            # Rivision: to rotate the center slice
            # <C> adds a positive Back rotation
            self.accept("c", lambda: addInterval("center"))
            # <Shift+C> adds a negative Back rotation
            self.accept("shift-c", lambda: addInterval("center", True))            
            # Rivision: to rotate the equator slice
            # <E> adds a positive Back rotation
            self.accept("e", lambda: addInterval("equator"))
            # <Shift+E> adds a negative Back rotation
            self.accept("shift-e", lambda: addInterval("equator", True))
            # Rivision: to rotate the standing slice
            # <S> adds a positive Back rotation
            self.accept("s", lambda: addInterval("standing"))
            # <Shift+S> adds a negative Back rotation
            self.accept("shift-s", lambda: addInterval("standing", True))
            
            # <Enter> starts the sequence
            self.accept("enter", startSequence)

        def ignoreInput():
            self.ignore("f")
            self.ignore("shift-f")
            self.ignore("b")
            self.ignore("shift-b")
            self.ignore("l")
            self.ignore("shift-l")
            self.ignore("r")
            self.ignore("shift-r")
            self.ignore("d")
            self.ignore("shift-d")
            self.ignore("u")
            self.ignore("shift-u")
            self.ignore("enter")

        def startSequence():
            # do not allow input while the sequence is playing...
            ignoreInput()
            # ...but accept input again once the sequence is finished
            self.seq.append(Func(acceptInput))
            self.seq.start()
            # print "Sequence started."
            # create a new sequence, so no new intervals will be appended to the started one
            self.seq = Sequence()

        acceptInput()


app = MyApp()
app.run()