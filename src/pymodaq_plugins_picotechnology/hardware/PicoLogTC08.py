# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 16:24:12 2025

@author: bpons
"""

# TO DO ONCE WITH A NEW COMPUTER :
# This program do not need anything to run except PicoSDK to download from PicoTech official website.
# See : https://www.picotech.com/downloads and then go to PicoLog Data Loggers/TC-08/Software.
# The downloaded file has to be run with administrators access, and it works perfectly with the default configuration.
# When it is done, find the path to "usbtc08.dll" in your computer and copy/paste it to replace mine in the __init__
# section below from PicoLogTC08 class. Your path should be very similar to mine.
# When this has been done for your computer everything should run perfectly !

# Note : A python wrapper was also made by PicoTech, see my tutorial to install their packages and use it if you prefer.
# See : https://github.com/picotech/picosdk-python-wrappers/tree/master/usbtc08Examples and my documentation word file.

import ctypes
import time

class PicoLogTC08:
    """Class for communicating with a PicoLog TC-08 connected to a USB port of the computer."""

    def __init__(self, serial_number : str = None):
        # The path below should be adapted for your computer.
        self.tc08dll = ctypes.CDLL("C:\Program Files\Pico Technology\SDK\lib/usbtc08.dll")
    
        # Those values can be changed or adapted if required.
        self.buffer_length = 64 # It means that the buffer should be checked with get_temp at least every 64*interval_pico_log
        # (indeed : interval_pico_log <= interval_reading_buffer <= self.buffer_length * interval_pico_log)
        self.string_length = 16
        self.format_string_length = 256 # At least 256 but works well for now.
        self.units = ctypes.c_int16(0)  # Units value (0: °C, 1: °F, 2: K, 3: Rankine)
        self.dictionary_of_detected_units = {}
        self.get_dictionary_of_detected_units() # Make sure to call close_all_units() at the end of you program !
        if serial_number:
            if serial_number in self.dictionary_of_detected_units:
                self.handle = self.dictionary_of_detected_units[serial_number]
                print(f"Ouverture {serial_number}")
            else :
                raise ConnectionError(f"Serial number {serial_number} not found in detected units.")
        else :
            if self.dictionary_of_detected_units:
                for unit in self.dictionary_of_detected_units:
                    self.handle = self.dictionary_of_detected_units[unit]
                    print(f"Ouverture {unit}")
                    break
            else :
                raise ConnectionError("No unit found, check connection and driver installation.")

    # The following methods represents every native function from a TC08 device except the asynchronous and the
    # legacy mode ones.

    def open_unit(self) -> int:
        """Opens the USB TC-08 unit and gets a valid USB handle. Creates attribute self.handle"""
        self.handle = self.tc08dll.usb_tc08_open_unit()
        if self.handle == -1:
            self.get_last_error()
            raise ConnectionError("Error opening a unit.")
        elif self.handle == 0 :
            raise ConnectionError("No more unit found.")
        else:
            return self.handle
    
    def close_unit(self, handle : int = None):
        """Closes the handle. Note that if no handle is specified, it tries to close the unit with the self.handle attribute"""
        if not handle :
            handle = self.handle
        status = self.tc08dll.usb_tc08_close_unit(handle)
        if status == 0:
            self.get_last_error()
            raise ConnectionError(f"Error closing the unit linked to the handle {handle}.")
        elif status == 1:
#            print("Unit closed.")
            pass
        else:
            raise ValueError(f"Closing unit status not listed : {status}.")
            
    def stop_streaming(self):
        """Stops the unit streaming."""
        status = self.tc08dll.usb_tc08_stop(self.handle)
        if status == 0:
            raise ValueError("Invalid parameter.")
        elif status == 1:
#            print("Streaming stopped.")
            pass
        else:
            raise ValueError(f"Stop streaming status not listed : {status}.")
    
    def set_mains(self, reject50Hz : bool = True):
        """Sets the mains interference rejection filter to either 50 Hz or 60 Hz. (Default : rejects 50Hz.)"""
        if not reject50Hz :
            rejection_value = 1
        else:
            rejection_value = 0
        status = self.tc08dll.usb_tc08_set_mains(self.handle, rejection_value)
        if status == 0:
            self.get_last_error()
            raise ValueError("An error occurred while setting the filter value.")
        elif status == 1:
#            print("Filter has been set up as defined.")
            pass
        else:
            raise ValueError(f"Filter settings status not listed : {status}.")
            
    def get_minimum_interval(self) -> str:
        """Returns the minimum sampling interval for the current setup."""
        interval = self.tc08dll.usb_tc08_get_minimum_interval_ms(self.handle)
        if interval == 0:
            self.get_last_error()
            raise ValueError("An error occurred while getting the minimum sampling interval.")
        else:
            print(f"Minimum time interval : {interval} ms.")
            return interval

    def get_dictionary_of_detected_units(self):
        """Opens every unit available and link their serial number to their handle.
        Creates self.dictionary_of_detected_units but need to call close_all_units at the end of your program."""
        while True:
            try:
                handle = self.open_unit()
                serial_number = self.get_unit_info()
                self.dictionary_of_detected_units[serial_number] = handle
            except Exception as e :
                # print(f"Error getting dictionary of detected units : {e}")
                break
        if self.dictionary_of_detected_units:
            print(f"Dictionary of detected units : {self.dictionary_of_detected_units}")
        else :
            print("No unit detected.")

    def close_all_units(self):
        """Closes all units opened with get_dictionary_of_detected_units method."""
        if self.dictionary_of_detected_units:
            for unit in self.dictionary_of_detected_units:
                handle = self.dictionary_of_detected_units[unit]
                self.close_unit(handle)
        else :
            print("No unit found in self.dictionary_of_detected_units.")

    def get_unit_info(self, line_number : int = 4):
        """Retrieves specific information on a unit and presents it as a string."""
        string_obj = ctypes.c_int8 * self.string_length
        string = string_obj()
        if not 0 <= line_number <= 5:
            raise ValueError(f"Invalid line number value : {line_number}.")
        line = ctypes.c_int16(line_number)
        status = self.tc08dll.usb_tc08_get_unit_info2(self.handle, string, self.string_length, line)
        if status == 0:
            self.get_last_error()
            raise ValueError("An error occurred while getting the unit information.")
        else :
            # print(f"Unit info : {bytes(string[:status]).decode()}.")
            return bytes(string[:status]).decode()
    
    def get_formatted_info(self) -> str:
        """Retrieves information on a particular unit and presents it in string form."""
        unit_format_info_obj = ctypes.c_int8 * self.format_string_length
        unit_format_info = unit_format_info_obj()
        status = self.tc08dll.usb_tc08_get_formatted_info(self.handle, unit_format_info, self.format_string_length)
        if status == 0:
            print("Too many bytes to copy, change self.format_string_length to a higher value.")
        elif status == 1:
            print(f"Formated information for the handle {self.handle} : \n{bytes(unit_format_info).decode()}")
        else:
            raise ValueError(f"Formated information status not listed : {status}.")
        return bytes(unit_format_info).decode()
    
    def get_last_error(self):
        """Returns the last error for a specified unit or for a call to open a unit."""
        error_code = self.tc08dll.usb_tc08_get_last_error(self.handle)
        if error_code == 0:
#            print("No error occurred.")
            pass
        elif error_code == 1:
            raise ConnectionError("The driver does not support the current operating system.")
        elif error_code == 2:
            raise ConnectionError("A call to SetChannelSpecs is required.")
        elif error_code == 3:
            raise ConnectionError("One or more of the function arguments were invalid.")
        elif error_code == 4:
            raise ConnectionError("The hardware version is not supported. Download the latest driver.")
        elif error_code == 5:
            raise ConnectionError("An incompatible mix of legacy and non-legacy functions was called "
                                  "(or usb_tc08_get_single was called while in streaming mode).")
        elif error_code == 6:
            raise ConnectionError(" usb_tc08_open_unit_async was called again while a background enumeration "
                                  "was already in progress.")
        elif error_code == 7:
            raise ConnectionError("Cannot get a reply from a USB TC-08.")
        elif error_code == 8:
            raise ConnectionError("Unable to download firmware.")
        elif error_code == 9:
            raise ConnectionError("Missing or corrupted EEPROM.")
        elif error_code == 10:
            raise ConnectionError("Cannot find enumerated device.")
        elif error_code == 11:
            raise ConnectionError("A threading function failed.")
        elif error_code == 12:
            raise ConnectionError("Can not get USB pipe information.")
        elif error_code == 13:
            raise ConnectionError("No calibration date was found.")
        elif error_code == 14:
            raise ConnectionError("An old picopp.sys driver was found on the system.")
        elif error_code == 15:
            raise ConnectionError("The PC has lost communication with the device.")
        else:
            raise ValueError(f"Error code not listed : {error_code}.")
            
    def set_channel_specs(self, channel : int, tc_type : str):
        """Sets up a USB TC-08 channel."""
        if not (type(channel) == int)&(0 <= channel <= 8):
            raise ValueError(f"Entered channel do not exist; should be an integer between 0 and 8, value entered : {channel}.")
        if not tc_type in ['B', 'E', 'J', 'K', 'N', 'R', 'S', 'T', ' ', 'X']:
            raise ValueError(f"Thermocouple entered type is not supported : {tc_type}.")
        selected_channel = ctypes.c_int16(channel)
        tc = ctypes.c_char(bytes(tc_type, encoding = 'utf-8'))
        status = self.tc08dll.usb_tc08_set_channel(self.handle, selected_channel, tc)
        if status == 0:
            self.get_last_error()
            raise ConnectionError("An error occurred while setting the channel.")
        elif status == 1:
#            print(f"Channel {channel} has been set up.")
            pass
        else:
            raise ValueError(f"Channel status not listed : {status}.")
            
    def run_streaming(self, interval : int):
        """Starts the USB TC-08 unit streaming."""
        # Note : if the time interval passed in argument is shorter than the minimum one (for the configuration),
        # the PicoLog TC08 will use the latest to avoid errors.
        selected_interval = ctypes.c_int16(interval)
        status = self.tc08dll.usb_tc08_run(self.handle, selected_interval)
        if status == 0:
            self.get_last_error()
            raise ConnectionError("An error occured while running the unit streaming.")
        else:
            print(f"Time interval between two samples : {status} ms.")
            
    def get_single(self):
        """Converts readings from currently set up channels on demand."""
        temp_array_obj = ctypes.c_float * 9
        temp_array = temp_array_obj()
        overflow = ctypes.c_int16()
        status = self.tc08dll.usb_tc08_get_single(self.handle, temp_array, overflow, self.units)
        if status == 0:
            self.get_last_error()
            raise ConnectionError("An error occurred while getting a single reading.")
        elif status == 1:
#            print("Single reading taken.")
            pass
        else:   
            raise ValueError(f"Single reading status not listed : {status}.")
        return temp_array[:]
    
    def get_temp(self, channel : int) -> tuple:
        """In streaming mode, retrieves temperature readings from a specified channel."""
        if not (type(channel) == int)&(0 <= channel <= 8):
            raise ValueError(f"Entered channel do not exist; should be an integer between 0 and 8, value entered : {channel}.")
        temp_buffer_obj = ctypes.c_float * (9 * self.buffer_length)
        temp_buffer = temp_buffer_obj()
        times_buffer = ctypes.c_int32()
        overflow = ctypes.c_int16()
        selected_channel = ctypes.c_int16(channel)
        # fill_missing value can be set to 0 : 0Nan or 1 : replace the missing value with the last known one.
        fill_missing = ctypes.c_int16(0)
        status = self.tc08dll.usb_tc08_get_temp(self.handle, temp_buffer, times_buffer, self.buffer_length,
                                                overflow, selected_channel, self.units, fill_missing)
        if status == -1:
            self.get_last_error()
            raise ConnectionError("An error occurred while reading the temperature buffer in streaming mode.")
        elif status == 0:
            raise ValueError("No data available in the buffer.")
        else:
            # print(f"There are {status} values in the buffer.")
            return status, temp_buffer[:]

    
# ------------------------------------------------- 
# The following functions are examples of what can be done and how to use the methods created above.
# -------------------------------------------------


def single_data_reading_example() -> list:
    """Example of connection to a PicoLog device to make a single temperature reading."""
    try :
        # If you know the serial number of your device, you can call :
        # PicoLogA = PicoLogTC08('AO024/303')
        # If you just want to connect to a device, or list the available ones, call :
        PicoLogA = PicoLogTC08()
        # Note that you are connected to the first device from the dictionary.
        PicoLogA.get_formatted_info()

        # Setting up the channels for data reading.
        # Note that 'X' returns the voltage read by the thermocouple and ' ' ignores the channel (it's easier not to set
        # it up in that case). Channel 0 is the cold-junction.
        PicoLogA.set_channel_specs(1, 'K')
        PicoLogA.set_channel_specs(2, 'K')
        PicoLogA.set_channel_specs(3, ' ')
        PicoLogA.set_channel_specs(5, 'K')
        PicoLogA.set_mains()
        PicoLogA.get_minimum_interval()
        collected_temp_data = PicoLogA.get_single()
    except Exception as e:
        print(f"Unexpected error : {e}")
    finally :
        PicoLogA.close_all_units()
        return [time.strftime("%Y-%m-%d", time.localtime()), time.strftime("%H:%M:%S", time.localtime())] + collected_temp_data

#print(single_data_reading_example())


def grab_data_finite_loop_example(channel : int, type_tc : str, interval_pico_log : int,
                                  interval_reading_buffer : int, reading_number : int) -> list:
    """Example of connection to a PicoLog device to grab some data in streaming mode.
    ===============================
    channel : int (channel where the data will be collected)
    type_tc : str (thermocouple type of the channel)
    interval_pico_log : int (time interval in ms at which the PicoLog will send data to a buffer)
    interval_reading_buffer : int (time interval in seconds at which the computer will read the buffer, must be greater or
    at least equal to interval_pico_log)
    reading_number : int (number of readings of the buffer)"""
    try :
        PicoLogA = PicoLogTC08()
        PicoLogA.set_channel_specs(channel, type_tc)
        PicoLogA.set_mains()
        PicoLogA.get_minimum_interval()
        PicoLogA.run_streaming(interval_pico_log)
        print(time.strftime("%Y-%m-%d", time.localtime()) +' ' + time.strftime("%H:%M:%S", time.localtime()) + " : Streaming starts.")
        list_of_grabbed_data = []
        for i in range(0, reading_number):
            print(f"Reading number {i}")
            time.sleep(interval_reading_buffer)
            number_of_values_in_buffer, collected_temp_data = PicoLogA.get_temp(channel)
            print(collected_temp_data[:number_of_values_in_buffer])
            list_of_grabbed_data += collected_temp_data[:number_of_values_in_buffer]
    except Exception as e:
        print(f"Unexpected error : {e}")
    finally :
       print(time.strftime("%Y-%m-%d", time.localtime()) +' ' + time.strftime("%H:%M:%S", time.localtime()) + " : Streaming ends.")
       PicoLogA.stop_streaming()
       PicoLogA.close_all_units()
       return list_of_grabbed_data

# grab_data_finite_loop_example(1, 'K', 100, 5, 5)

def grab_data_infinite_loop_example(channel : int, type_tc : str, interval_pico_log : int,
                                    interval_reading_buffer: int) -> list:
    """Example of user-interrupted streaming mode from a PicoLog device.
    =====================================
    channel : int (channel where the data will be collected)
    type_tc : str (thermocouple type of the channel)
    interval_pico_log : int (time interval in ms at which the PicoLog will send data to a buffer)
    interval_reading_buffer : int (time interval in seconds at which the computer will read the buffer, must be greater or
    at least equal to interval_pico_log)"""
    try :
        PicoLogA = PicoLogTC08()
        PicoLogA.set_channel_specs(channel, type_tc)
        PicoLogA.set_mains()
        PicoLogA.get_minimum_interval()
        PicoLogA.run_streaming(interval_pico_log)
        print(time.strftime("%Y-%m-%d", time.localtime()) +' ' + time.strftime("%H:%M:%S", time.localtime()) + " : Streaming starts.")
        list_of_grabbed_data = []
        while True:
            time.sleep(interval_reading_buffer)
            number_of_values_in_buffer, collected_temp_data = PicoLogA.get_temp(channel)
            print(collected_temp_data[:number_of_values_in_buffer])
            list_of_grabbed_data += collected_temp_data[:number_of_values_in_buffer]
    except Exception as e:
        print(f"Unexpected error : {e}")
    except KeyboardInterrupt :
        print("Streaming stopped by the user.")
    finally :
       print(time.strftime("%Y-%m-%d", time.localtime()) +' ' + time.strftime("%H:%M:%S", time.localtime()) + " : Streaming ends.")
       PicoLogA.stop_streaming()
       PicoLogA.close_all_units()
       return list_of_grabbed_data
   
# grab_data_infinite_loop_example(4, 'K', 1000, 1)

