import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_picotechnology.hardware.PicoLogTC08 import PicoLogTC08


class DAQ_0DViewer_Picotechnology_PicologTC08(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    params = comon_parameters + [
        {'title': 'Device serial number :', 'name': 'device_serial_number', 'type': 'str', 'value': 'A0138/766'},
        {'title': 'TC type :', 'name': 'tc_type', 'type': 'str', 'value': 'K', 'readonly': True},
        {'title': 'Activated Channels', 'name': 'activated_channels', 'type': 'group', 'children': [
            {'title': f'Channel {i} :', 'name': f'channel_{i}', 'type': 'bool'} for i in range(1, 9)
        ]}
    ]

    def ini_attributes(self):
        self.controller: PicoLogTC08 = None
        self.serial = self.settings.child("device_serial_number").value()

    def commit_settings(self, param: Parameter):
        if param.name() == 'device_serial_number':
            self.serial = param.value()

    def ini_detector(self, controller=None):
        info = ""
        if self.is_master:
            try:
                self.controller = PicoLogTC08(self.serial)
                initialized = True
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.emit_status(ThreadCommand('Update_Status', [f"Connexion au PicoLog impossible : {e}"]))
                self.controller = None
                initialized = False
            info = f"PicoLog TC-08 {self.serial} ouvert"
        else:
            self.controller = controller
            initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master and self.controller is not None:
            self.controller.close_unit()
            self.controller = None

    def grab_data(self, Naverage=1, **kwargs):
        self.controller.set_channel_specs(1, 'K')
        self.controller.set_mains()
        self.controller.get_minimum_interval()
        data_tot = self.controller.get_single()
        self.dte_signal.emit(DataToExport(name='Temperature',
                                          data=[DataFromPlugins(name='Channel_1', data=data_tot[1],
                                                                dim='Data0D', labels=['Channel 1 [°C]'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''


if __name__ == '__main__':
    main(__file__)