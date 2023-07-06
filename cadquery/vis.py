from . import Shape, Workplane, Assembly, Sketch, Compound
from .occ_impl.exporters.assembly import _vtkRenderWindow

from typing import Union

from OCP.TopoDS import TopoDS_Shape

from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkMapper,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
)


def _to_assy(*objs: Union[Shape, Workplane, Assembly, Sketch]) -> Assembly:

    assy = Assembly()

    for obj in objs:
        if isinstance(obj, (Shape, Workplane, Assembly)):
            assy.add(obj)
        elif isinstance(obj, Sketch):
            assy.add(obj._faces)
            assy.add(Compound.makeCompound(obj._edges))
            assy.add(Compound.makeCompound(obj._wires))
        elif isinstance(obj, TopoDS_Shape):
            assy.add(Shape(obj))
        else:
            raise ValueError(f"{obj} has unsupported type {type(obj)}")

    return assy


def show(*objs: Union[Shape, Workplane, Assembly, Sketch]) -> vtkRenderWindow:
    """
    Show CQ objects using VTK
    """

    # construct the assy
    assy = _to_assy(*objs)

    # create a VTK window
    win = _vtkRenderWindow(assy)

    win.SetWindowName("CQ viewer")

    # rendering related settings
    win.SetMultiSamples(16)
    vtkMapper.SetResolveCoincidentTopologyToPolygonOffset()
    vtkMapper.SetResolveCoincidentTopologyPolygonOffsetParameters(1, 0)
    vtkMapper.SetResolveCoincidentTopologyLineOffsetParameters(-1, 0)

    # create a VTK interactor
    inter = vtkRenderWindowInteractor()
    inter.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
    inter.SetRenderWindow(win)

    # construct an axes indicator
    axes = vtkAxesActor()
    axes.SetNormalizedShaftLength(1, 1, 1)
    axes.SetTotalLength(10, 10, 10)
    axes.SetDragable(0)

    tp = axes.GetXAxisCaptionActor2D().GetCaptionTextProperty()
    tp.SetColor(0, 0, 0)

    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ShallowCopy(tp)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ShallowCopy(tp)

    # add to an orientation widget
    orient_widget = vtkOrientationMarkerWidget()
    orient_widget.SetOrientationMarker(axes)
    orient_widget.SetViewport(0.9, 0.0, 1.0, 0.2)
    orient_widget.SetZoom(1.1)
    orient_widget.SetInteractor(inter)
    orient_widget.EnabledOn()
    orient_widget.InteractiveOff()

    # set sie, show and return
    win.SetSize(*win.GetScreenSize())
    win.SetPosition(-10, 0)
    inter.Initialize()
    win.Render()
    inter.Start()

    return win


# alias
show_object = show
