# -*- coding: utf-8 -*-
'''

@author: Chirag

'''

import vtk, platform
from vtk.util.colors import banana, brown_ochre, tomato, grey, flesh, sienna, navajo_white

print platform.python_version()
print "VTK VERSION: ",vtk.vtkVersion.GetVTKSourceVersion()
########################################################################################################################

fohe = vtk.vtkBYUReader() #Reader object.
fohe.SetGeometryFileName("fohe.g") #Read the Fuel Oil Heat Exchanger object.

#Compute normals to the FOHE object
polydata_normals = vtk.vtkPolyDataNormals()
polydata_normals.SetInputConnection(fohe.GetOutputPort())

#Create Mapper of FOHE
fohe_Mapper = vtk.vtkPolyDataMapper()
fohe_Mapper.SetInputConnection(fohe.GetOutputPort())

########################################################################################################################

#Create a plane
fohe_plane = vtk.vtkPlane()
fohe_plane.SetOrigin(fohe_Mapper.GetCenter()) #Set Origin to center of the object
fohe_plane.SetNormal(1, 0, 1) #Set Normal to [1 0 1]T

#Sampling the plane to display it
plane_sample = vtk.vtkSampleFunction()
plane_sample.SetSampleDimensions(4,4,4)
plane_sample.SetModelBounds(fohe_Mapper.GetBounds()) #Setting the plane to be within the bounds of the object.
plane_sample.SetImplicitFunction(fohe_plane) #Setting the implicit function to be the plane.
plane_sample_mapper = vtk.vtkPolyDataMapper() #Create a sample mapper
plane_sample_mapper.SetInputConnection(plane_sample.GetOutputPort())
plane_sample_actor = vtk.vtkActor() #Create a sample mapper for display
plane_sample_actor.SetMapper(plane_sample_mapper)
plane_sample_actor.GetProperty().SetColor(flesh) #Set the colour of the sample actor

########################################################################################################################


#Adding custom colour to the plane
lut = vtk.vtkColorTransferFunction() #Create a lookup table
lut.AddRGBPoint(0.005, 55, 55, 55)

#Applying Contour Filter to sample to display the cutting plane
cont_filter = vtk.vtkContourFilter()
cont_filter.SetInputConnection(plane_sample.GetOutputPort())
cont_filter.SetValue(0, 0.005)
con_filt_mapper = vtk.vtkPolyDataMapper() #Create a mapper for filter
con_filt_mapper.SetLookupTable(lut) #Add colour to the plane
con_filt_mapper.SetInputConnection(cont_filter.GetOutputPort())
con_filt_actor = vtk.vtkActor() #Create an actor for filter
con_filt_actor.SetMapper(con_filt_mapper)

########################################################################################################################

#Create a clipper to clip the object/data
fohe_clipper = vtk.vtkClipPolyData()
fohe_clipper.SetInputConnection(polydata_normals.GetOutputPort())
fohe_clipper.SetClipFunction(fohe_plane) #Setting the plane to clip the data.
fohe_clipper.GenerateClipScalarsOn() #Interpolate output scalar values
fohe_clipper.GenerateClippedOutputOn() #Generate clipped out data
fohe_clipper.SetValue(0) #Clipping value of the implicit function set to 0.
fohe_clip_mapper = vtk.vtkPolyDataMapper() #Create clip mapper
fohe_clip_mapper.SetInputConnection(fohe_clipper.GetOutputPort())
fohe_clip_mapper.ScalarVisibilityOff()
backProp = vtk.vtkProperty()
fohe_clip_actor = vtk.vtkActor() #Create clip actor
fohe_clip_actor.SetMapper(fohe_clip_mapper)
fohe_clip_actor.GetProperty().SetColor(navajo_white) #Set clipped data colour
fohe_clip_actor.SetBackfaceProperty(backProp)

#VTK Cutter for displaying the intersection area
fohe_cut_edges = vtk.vtkCutter()
fohe_cut_edges.SetInputConnection(polydata_normals.GetOutputPort())
fohe_cut_edges.SetCutFunction(fohe_plane)
fohe_cut_edges.GenerateCutScalarsOn() #Interpolate output scalar values
fohe_cut_edges.SetValue(0, 0)
fohe_cut_strips = vtk.vtkStripper() #Generate triangle strips
fohe_cut_strips.SetInputConnection(fohe_cut_edges.GetOutputPort())
fohe_cut_strips.Update()
fohe_cut_poly = vtk.vtkPolyData()
fohe_cut_poly.SetPoints(fohe_cut_strips.GetOutput().GetPoints()) #Get points from strips
fohe_cut_poly.SetPolys(fohe_cut_strips.GetOutput().GetLines()) #Create polygonal data to be displayed

#Triangle Filter
triangles = vtk.vtkTriangleFilter() #Triangulate non-triangular polygon data
triangles.SetInputData(fohe_cut_poly)
cut_mapper = vtk.vtkPolyDataMapper()
cut_mapper.SetInputData(fohe_cut_poly)
cut_mapper.SetInputConnection(triangles.GetOutputPort())
cut_actor = vtk.vtkActor()
cut_actor.SetMapper(cut_mapper)
cut_actor.GetProperty().SetColor(banana)

rest_mapper = vtk.vtkPolyDataMapper() #Create mapper for remaining data
rest_mapper.SetInputData(fohe_clipper.GetClippedOutput())
rest_mapper.ScalarVisibilityOff()
rest_actor = vtk.vtkActor() #Create actor for remaining data
rest_actor.SetMapper(rest_mapper)
rest_actor.GetProperty().SetRepresentationToWireframe()

########################################################################################################################

#VTK PIPELINE
fohe_Actor = vtk.vtkActor()
fohe_Actor.SetMapper(fohe_Mapper)

#Create renderer
ren_fohe = vtk.vtkRenderer()
# ren_fohe.AddActor(fohe_Actor)

#Add actors to renderer
ren_fohe.AddActor(fohe_clip_actor)
ren_fohe.AddActor(cut_actor)
ren_fohe.AddActor(rest_actor)
ren_fohe.AddActor(con_filt_actor)

#Create a render window and set its size
render_window = vtk.vtkRenderWindow()
render_window.SetSize(600, 300)
render_window.AddRenderer(ren_fohe)
render_window.Render()

#Define an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

#Display output
interactor.Initialize()
interactor.Start()

print ren_fohe.GetActiveCamera()
