import numpy as np
from qtpy.QtWidgets import QLabel

from xicam.core.execution.workflow import Workflow
from xicam.plugins.guiplugin import GUILayout, GUIPlugin
from xicam.plugins.operationplugin import OperationPlugin, output_names
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor


class SamplePlugin(GUIPlugin):
    # Would be nice to make this optional...
    name = 'SamplePlugin'

    def __init__(self):

        # Set up an invert operation
        @OperationPlugin
        @output_names('inverted_data')
        def invert(data:np.ndarray = None) -> np.ndarray:
            if issubclass(data.dtype.type, np.integer):
                max = np.iinfo(data.dtype).max
            else:
                max = np.finfo(data.dtype).max
            return max - data

        # Set up our workflow
        workflow = Workflow()
        workflow.add_operation(invert)
        workflow_editor = WorkflowEditor(workflow)

        # Set up a GUI layout
        center_widget = QLabel("test")
        sample_stage_layout = GUILayout(center_widget)

        # Set up stages
        stages = {
            "Sample Stage": GUILayout(center_widget,
                                      right=workflow_editor)
        }
        self.stages = stages
        super(SamplePlugin, self).__init__()


    def appendCatalog(catalog):
        return
