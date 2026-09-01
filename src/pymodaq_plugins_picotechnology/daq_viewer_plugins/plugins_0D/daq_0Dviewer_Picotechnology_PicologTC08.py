import os
import time

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
        # Pur listing : on ouvre/ferme chaque unité juste pour lire son numéro de série,
        # sans rien garder ouvert. Sûr à appeler depuis ini_attributes(), même sur une
        # instance jetable.
        found = PicoLogTC08.discover_units(close_after=True)
        self.emit_status(ThreadCommand('Update_Status', [f"Découverte : {list(found.keys())}"]))
        self.settings.child('device_serial_number').setLimits(list(found.keys()))


    def ini_attributes(self):
        import os
        print(f"PID du process plugin : {os.getpid()}", flush=True)
        self.controller: PicoLogTC08 = None
        self.emit_status(ThreadCommand('Update_Status', [f"ini_attributes() appelé, PID={os.getpid()}"]))

        self.get_connected_serials()
        self.serial = self.settings.child('device_serial_number').value() or None

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
        info = ""
        if self.is_master:
            try:
                self.emit_status(ThreadCommand('Update_Status', ["ini_detector() : tentative d'ouverture"]))
                self.controller = PicoLogTC08(serial_number=self.serial) if self.serial else PicoLogTC08()
                initialized = bool(self.controller)
                if initialized:
                    connected_serial = list(self.controller.dictionary_of_detected_units.keys())[0]
                    self.settings.child('device_serial_number').setValue(connected_serial)
                    self.emit_status(ThreadCommand('Update_Status', [f"Connecté : {connected_serial}"]))
                info = "Whatever info you want to log"
            except ConnectionError as e:
                self.emit_status(ThreadCommand('Update_Status', [f"Connexion au PicoLog impossible : {e}"]))
                info = str(e)
                initialized = False
        else:
            self.controller = controller
            initialized = True
        return info, initialized

    def close(self):
        self.emit_status(ThreadCommand('Update_Status',
                                       [f"close() appelé, PID={os.getpid()}, is_master={self.is_master}, controller={self.controller}"]))
        if self.is_master and self.controller is not None:
            self.controller.close_all_units()
            self.emit_status(ThreadCommand('Update_Status', ["close_all_units() terminé"]))
        else:
            print(
                f"[{time.strftime('%H:%M:%S')}] close() : rien à fermer (is_master={self.is_master}, controller={self.controller})",
                flush=True)

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
        return ''


if __name__ == '__main__':
    main(__file__)
