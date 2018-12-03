'''

Author: Chirag Balakrishna

CCID : cbalakri@ualberta.ca

Computer Graphics Assignment 3 : Volume Rendering, Interaction and Histogram Computation

Student ID : 1559633

Note : Some elements of the following program has been adapted from the VTK examples websites.
https://www.vtk.org/Wiki/VTK/Examples/

The custom interaction style class was written by referring to some stack overflow issues
posted by the community.
https://stackoverflow.com/questions/32636503/how-to-get-the-key-code-in-a-vtk-keypressevent-using-python

'''

import vtk
import sys
print(sys.version)
print(vtk.vtkVersion.GetVTKSourceVersion())
print("Assignment 3 : Volume Rendering, Interaction and Histogram Computation")
print("\n\n")

# Create a class for detecting key press events and for mouse scroll events.
class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None, plane=None, render=None):
        self.parent = None
        self.plane = None
        self.render = None
        self.AddObserver("KeyPressEvent",self.keyPressEvent)
        self.AddObserver("MouseWheelForwardEvent", self.mouseWheelForwardEvent)
        self.AddObserver("MouseWheelBackwardEvent", self.mouseWheelBackwardEvent)

    #Call back for key press events. Note: Only arrow keys (Left and Right) are used for moving the plane slicer
    def keyPressEvent(self,obj,event):
        key = self.parent.GetKeySym()
        if key == 'Left':
            print(key)
            print("current slice-pos:", self.plane.GetSlicePosition())
            self.plane.SetSlicePosition(self.plane.GetSlicePosition() - 1)
            # self.plane.StartSliceMotion()
        elif key == 'Right':
            print(key)
            print("current slice-pos:", self.plane.GetSlicePosition())
            self.plane.SetSlicePosition(self.plane.GetSlicePosition() + 1)
        self.render.Render()
        return

    # Call back to detect mouse wheel event.
    def mouseWheelBackwardEvent(self, obj,event):
        self.plane.SetSlicePosition(self.plane.GetSlicePosition() - 1)
        self.render.Render()
        return

    # Call back to detect mouse wheel event.
    def mouseWheelForwardEvent(self, obj,event):
        self.plane.SetSlicePosition(self.plane.GetSlicePosition() + 1)
        self.render.Render()
        return




#1. read DICOM Data
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName("D:\Chirag B\CompGraph\Assignment3\CTDATA")
reader.Update()
print(reader)
print("Loaded Data...")
print("Preparing to render data...")

#2. Create a colour transfer function
color_trans = vtk.vtkColorTransferFunction()
color_trans.AddRGBPoint(-3024, 0.0, 0.0, 0.0)
color_trans.AddRGBPoint(-77, 0.55, 0.25, 0.15)
color_trans.AddRGBPoint(94, 0.88, 0.60, 0.29)
color_trans.AddRGBPoint(179, 1.0, 0.94, 0.95)
color_trans.AddRGBPoint(260, 0.62, 0.0, 0.0)
color_trans.AddRGBPoint(3071, 0.82, 0.66, 1.0)
print("Created colour tansfer function.")

#3. Create an opacity transfer function
opac_func = vtk.vtkPiecewiseFunction()
opac_func.AddPoint(-3024, 0.0)
opac_func.AddPoint(-77, 0.0)
opac_func.AddPoint(94, 0.29)
opac_func.AddPoint(179, 0.55)
opac_func.AddPoint(260, 0.84)
opac_func.AddPoint(3071, 0.875)
print("Created opacity transfer function.")


#Create a volume mapper
ctMapper = vtk.vtkSmartVolumeMapper()
ctMapper.SetInputConnection(reader.GetOutputPort())

# Add the opacity and colour transfer functions defined above
ctProp = vtk.vtkVolumeProperty()
ctProp.SetScalarOpacity(opac_func)
ctProp.SetColor(color_trans)
ctProp.ShadeOn()
# To define a volume actor
ctVolume = vtk.vtkVolume()
volRen = vtk.vtkRenderer()
#Set volume actor properties
ctVolume.SetMapper(ctMapper)
ctVolume.SetProperty(ctProp)

#Create a render window
mainWindow = vtk.vtkRenderWindow()
windInteract = vtk.vtkRenderWindowInteractor()
mainWindow.SetSize(800,800)
windInteract.SetRenderWindow(mainWindow)
mainWindow.AddRenderer(volRen)


#Render the volume
volRen.AddVolume(ctVolume)
volRen.SetViewport(0, 0, 0.5, 1)
mainWindow.Render()


#5. Create a plane widget
planeWid = vtk.vtkImagePlaneWidget()
planeWid.SetInputConnection(reader.GetOutputPort())
planeWid.DisplayTextOn()
planeWid.SetInteractor(windInteract) #Set the plane interactor.

# Place Widget
planeWid.PlaceWidget()
planeWid.On()

#6. Sample some data and view it
sample = planeWid.GetResliceOutput()  # Get sample data from the plane
sample.Modified()
range = sample.GetScalarRange()
sampleActor = vtk.vtkImageActor()
sampleActor.SetInputData(sample)
#Create sample renderer
sampleRen = vtk.vtkRenderer()
sampleRen.AddActor(sampleActor)
sampleRen.SetViewport(0.6, 0.5, 1, 1)
mainWindow.AddRenderer(sampleRen)


#Create Histogram data
imgAcc = vtk.vtkImageAccumulate() #Compute image histogram.
imgAcc.AddInputData(sample)
imgAcc.SetComponentExtent(int(range[0]), int(range[1]), 0,0,0,0)
imgAcc.Update()

#7. Plot histogram of sampled data
plotHist = vtk.vtkXYPlotActor() #XYPlot actor to plot histogram
plotHist.ExchangeAxesOff()
plotHist.SetLabelFormat("%g")
plotHist.SetXTitle("Gray Level")
plotHist.SetYTitle("Frequency")
plotHist.SetXValuesToValue()
plotHist.GetPositionCoordinate().SetValue(0,0)
plotHist.GetActualPosition2Coordinate().SetValue(0.8,0.8)
plotHist.AddDataSetInputConnection(imgAcc.GetOutputPort(0))

#Create a histogram renderer
histRender = vtk.vtkRenderer()
histRender.AddActor(plotHist)
histRender.SetViewport(0.6, 0, 1, 0.5)
mainWindow.AddRenderer(histRender)
mainWindow.Render()


#instantiate a custom interactor.
inter = CustomInteractorStyle()
# Set parameters
inter.parent = windInteract
inter.plane = planeWid
inter.render = mainWindow
windInteract.SetInteractorStyle(inter)
windInteract.SetRenderWindow(mainWindow)


#Write output to JPEG file
wind2Im = vtk.vtkWindowToImageFilter()
writer = vtk.vtkJPEGWriter()

wind2Im.SetInput(mainWindow)
wind2Im.Update()
writer.SetInputConnection(wind2Im.GetOutputPort())
writer.SetFileName('assignment3_screenshot.jpg')
writer.Write()



windInteract.Initialize()
windInteract.Start()



