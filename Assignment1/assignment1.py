# -*- coding: utf-8 -*-
"""
Created on Sun Feb 04 02:11:07 2018

@author: chirag
"""

import vtk
import os


# Input Parameters
shuttle_object_file = "D:\Chirag B\CompGraph\Assignment1\Assignment1\space_shuttle.obj"
shuttle_texture_file = "D:\Chirag B\CompGraph\Assignment1\Assignment1\shuttle_texture.jpg"

#Output Parameter
jpeg_output_file = "assignment1_screenshot.jpg"


#Read the shuttle object.
shuttle = vtk.vtkOBJReader()
shuttle.SetFileName(shuttle_object_file)
shuttle.Update()

#Read the texture file and create the texture.
shuttle_texture_reader = vtk.vtkJPEGReader() #this object reads the JPEG file.
shuttle_texture_reader.SetFileName(shuttle_texture_file)
shuttle_texture = vtk.vtkTexture() # create a texture
shuttle_texture.SetInputConnection(shuttle_texture_reader.GetOutputPort()) # set texture to the jpeg image


# Creating polygonal data mappers for each viewport.
shuttle_mapper = vtk.vtkPolyDataMapper() #Create a polymapper for mapping polygonal data to graphics primitives.
shuttle_mapper.SetInputConnection(shuttle.GetOutputPort()) #Set mapper for polygonal data.
shuttle_mapper2 = vtk.vtkPolyDataMapper()
shuttle_mapper2.SetInputConnection(shuttle.GetOutputPort())
shuttle_mapper3 = vtk.vtkPolyDataMapper()
shuttle_mapper3.SetInputConnection(shuttle.GetOutputPort())
shuttle_mapper4 = vtk.vtkPolyDataMapper()
shuttle_mapper4.SetInputConnection(shuttle.GetOutputPort())


##############################################################################################################


## Wireframe Representation. No shading and no texture 
#Creating wireframe representation of the shuttle object
wireframe_actor = vtk.vtkActor() #Create a vtk actor
wireframe_actor.SetMapper(shuttle_mapper)
wireframe_actor.GetProperty().SetRepresentationToWireframe	() # Set the actor to be displayed in a wireframe.

#Apply transformation to rotate the object by 90.
wireframe_transform = vtk.vtkTransform()
wireframe_transform.RotateX(90)
#wireframe_transform.RotateY(45)
wireframe_actor.SetUserTransform(wireframe_transform)

#Render object for the shuttle wireframe
render_wireframe = vtk.vtkRenderer() # Create the vtk renderer object.
render_wireframe.SetViewport(0, 0.5, 0.5, 1.0) #Create a viewport in the top left corner of the render window.
render_wireframe.AddActor(wireframe_actor) #Add the wireframe actor to the renderer object.


##############################################################################################################


## Surface Representation.
#Creating surface representation of the shuttle object.
surface_actor = vtk.vtkActor()  #Create a vtk actor
surface_actor.SetMapper(shuttle_mapper2)
surface_actor.GetProperty().SetRepresentationToSurface()	# Set the actor to be displayed with a surface. 

#Apply transformation to rotate the object by 90.
surface_transform = vtk.vtkTransform()
surface_transform.RotateX(90)
#surface_transform.RotateY(45)
surface_actor.SetUserTransform(surface_transform)

#Render object for shuttle surface.
render_surface = vtk.vtkRenderer() # Create a vtk renderer.
render_surface.SetViewport(0.5, 0.5, 1.0, 1.0) #Create a viewport in the render window.
render_surface.AddActor(surface_actor) #Add the actor with surface to the renderer object.


##############################################################################################################


## Texture Representation.
#Creating texture representation of the shuttle object.
texture_actor = vtk.vtkActor()
texture_actor.SetMapper(shuttle_mapper3)
texture_actor.SetTexture(shuttle_texture)	# Set the actor to be displayed with a texture. 

#Apply transformation to rotate the object by 90.
textured_actor_transform = vtk.vtkTransform()
textured_actor_transform.RotateX(90)
#textured_actor_transform.RotateY(45)
texture_actor.SetUserTransform(textured_actor_transform)

#Render object for shuttle texture.
render_texture = vtk.vtkRenderer() # Create a vtk renderer.
render_texture.SetViewport(0, 0, 0.5, 0.5) #Create a viewport in the render window.
render_texture.AddActor(texture_actor) #Add the actor with texture to the renderer object.


##############################################################################################################


## Texture Representation with Phong Shading.
#Creating texture representation of the shuttle object.
phong_texture_actor = vtk.vtkActor()
phong_texture_actor.SetMapper(shuttle_mapper4)
phong_texture_actor.SetTexture(shuttle_texture)	# Set the actor to be displayed with a texture. 

#Apply transformation to rotate the object by 90.
phong_textured_actor_transform = vtk.vtkTransform()
phong_textured_actor_transform.RotateX(70)
#phong_textured_actor_transform.RotateY(120)
#phong_textured_actor_transform.RotateZ(-50)
phong_texture_actor.SetUserTransform(phong_textured_actor_transform)

#Compute normals for phong shading
normal = vtk.vtkPolyDataNormals()
normal.SetInputConnection(shuttle.GetOutputPort())

#Set actor properties for phong shading
properties = phong_texture_actor.GetProperty()
properties.SetInterpolationToPhong()
properties.ShadingOn()
properties.SetDiffuse(0.8) 
properties.SetAmbient(0.1)
properties.SetSpecular(0.9) 
properties.SetSpecularPower(100.0)


# Define light properties
light = vtk.vtkLight ()
light.SetLightTypeToSceneLight()
light.SetAmbientColor(1, 1, 1)
light.SetDiffuseColor(1, 1, 1)
light.SetSpecularColor(1, 1, 1)
light.SetPosition(-100, 100, 100)
light.SetFocalPoint(0,0,0)
light.SetIntensity(0.7)

#Render object for shuttle texture.
phong_render_texture = vtk.vtkRenderer() # Create a vtk renderer.
phong_render_texture.SetViewport(0.5, 0, 1.0, 0.5) #Create a viewport in the render window.
phong_render_texture.AddLight(light) # Add light to the viewport scene.
phong_render_texture.AddActor(phong_texture_actor) #Add the actor with texture to the renderer object.



##############################################################################################################

#Rest of VTK Pipeline

#Set Render Window Properties.
render_window = vtk.vtkRenderWindow()
render_window.SetSize(600, 300) #Set render window size.

#Multiple view port rendering. This will produce four different view ports.
render_window.AddRenderer(render_wireframe) #Top-Left of the render window.
render_window.AddRenderer(render_surface) #Top-Right of the render window.
render_window.AddRenderer(render_texture) #Bottom-Left of the render window.
render_window.AddRenderer(phong_render_texture) #Bottom-Right of the render window.
render_window.Render()

# Writing the rendered scene to JPEG
windowToImg = vtk.vtkWindowToImageFilter()
windowToImg.SetInput(render_window) 
windowToImg.SetMagnification(2) # Setting the output resolution to 2 times that of the render window.
windowToImg.ReadFrontBufferOff()
windowToImg.Update()

jpeg_writer = vtk.vtkJPEGWriter() # Create a jpeg file writer
jpeg_writer.SetFileName(jpeg_output_file) # output jpeg filename.
jpeg_writer.SetInputConnection(windowToImg.GetOutputPort()) # Get render window scene
jpeg_writer.Write()


iren = vtk.vtkRenderWindowInteractor() # Set render window interactor 
iren.SetRenderWindow(render_window)

iren.Initialize()
iren.Start()









