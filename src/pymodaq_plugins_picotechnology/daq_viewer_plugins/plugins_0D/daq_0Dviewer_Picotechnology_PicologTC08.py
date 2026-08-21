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
    params = comon_parameters+[
        {'title': 'Device serial number :', 'name': 'device_serial_number', 'type': 'list'},
        {'title': 'TC type :', 'name': 'tc_type', 'type': 'str', 'value':'K', 'readonly': True},
        {'title': 'Activated Channels', 'name': 'activated_channels', 'type': 'group', 'children': [
            {'title': 'Channel 1 :', 'name': 'channel_1', 'type': 'bool'},
            {'title': 'Channel 2 :', 'name': 'channel_2', 'type': 'bool'},
            {'title': 'Channel 3 :', 'name': 'channel_3', 'type': 'bool'},
            {'title': 'Channel 4 :', 'name': 'channel_4', 'type': 'bool'},
            {'title': 'Channel 5 :', 'name': 'channel_5', 'type': 'bool'},
            {'title': 'Channel 6 :', 'name': 'channel_6', 'type': 'bool'},
            {'title': 'Channel 7 :', 'name': 'channel_7', 'type': 'bool'},
            {'title': 'Channel 8 :', 'name': 'channel_8', 'type': 'bool'},
            ]}
    ]

    def get_connected_serials(self):
        temp_pico = PicoLogTC08()
        list_serial_numbers = list(temp_pico.dictionary_of_detected_units.keys())
        temp_pico.close_all_units()  # release the handle(s) opened just for discovery
        self.settings.child('device_serial_number').setLimits(list_serial_numbers)

    def ini_attributes(self):
        self.controller: PicoLogTC08 = None
        # self.serial = None
        self.get_connected_serials()
        self.serial = self.settings.child('device_serial_number').value() or None

        #TODO declare here attributes you want/need to init with a default value
        pass

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "device_serial_number":
            self.serial = param.value()
        # elif param.name() == "tc_type":
        #     self.controller.set_default_parameters()
        #     A faire mais pour toutes les channels actives

    def ini_detector(self, controller=None):
        """Detector communication initialization"""

        if self.is_master:
            if self.is_master:
                self.controller = PicoLogTC08(self.serial) if self.serial else PicoLogTC08()
                initialized = bool(self.controller)
        else:
            self.controller = controller
            initialized = True

        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='myplugin',
                                               data=[DataFromPlugins(name='Mock1',
                                                                    data=[np.array([0]), np.array([0])],
                                                                    dim='Data0D',
                                                                    labels=['Mock1', 'label2'])]))

        info = "Whatever info you want to log"
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master and self.controller is not None:
            self.controller.close_all_units()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        # synchrone version (blocking function)
        raise NotImplementedError  # when writing your own plugin remove this line
        data_tot = self.controller.your_method_to_start_a_grab_snap()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))
        #########################################################

        # asynchrone version (non-blocking function with callback)
        raise NotImplementedError  # when writing your own plugin remove this line
        self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        raise NotImplementedError  # when writing your own plugin remove this line
        self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)
