import csv
import nidaqmx

import datetime as dt
import src.guiTools as gt

from nidaqmx.constants import (TerminalConfiguration)

# DAQ model list
modelsDAQ = ['USB-6211', 'USB-6001', 'USB-6002']

alarm_log_fieldnames = ['Alarm Type', 'Temperature', 'Time Interval']

AO_DAQ_NAME = "wheatstone_vcc"
AO_DAQ_MIN_VAL = 0
AO_DAQ_VAL = 1
AO_DAQ_MAX_VAL = 5


def is_daq_connected():
    system = nidaqmx.system.System.local()
    devices = system.devices
    return len(devices) > 0


class niDAQ:
    """
        Class with DAQ information.

        Attributes:
            model (string): DAQ model selected by the user.
        """

    def __init__(self, model, exit_requested):
        self.model = model
        self.task_ai_ao = []
        self.exit_requested = exit_requested
        self.calibration = ""
        self.calibrations_log = []
        self.alarm_min = None
        self.alarm_max = None
        self.sample_rate = None
        self.n_samples = None
        self.start_acquisition_time = ""
        self.data = []
        self.time_intervals = []
        self.alarms_log = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        """
        When object[index] is used, accesses data list to retrieve value
        :param index: index to access
        :return: pair with [voltage, temperature]
        """
        return self.data[index]

    def __repr__(self):
        return f"model: {self.model}, " \
               f"calibration: {repr(self.calibration)}, " \
               f"alarm: [min, max] = {[self.alarm_min, self.alarm_max]} ºC"

    def set_tasks(self):
        if is_daq_connected():
            for channel in range(2):
                self.task_ai_ao.append(nidaqmx.Task())
        else:
            raise ValueError("Number of devices found in system is 0")

    def set_exit_request(self):
        """
        Sets exit request to True
        :return: bool in True
        """
        self.exit_requested = True

    def set_alarm_min(self, alarm_min):
        """
        Sets minimum alarm parameter
        :param alarm_min:
        :return:
        """
        self.alarm_min = alarm_min

    def set_alarm_max(self, alarm_max):
        """
        Sets maximum alarm parameter
        :param alarm_max:
        :return:
        """
        self.alarm_max = alarm_max

    def set_calibration(self, expression):
        """
        Sets to true if user has assigned a calibration
        :return:
        """
        self.calibration = expression

    def set_time_log(self):
        """
        Sets time log to current date/month/year hour:minute:second
        :return:
        """
        self.start_acquisition_time = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")

    def set_sample_rate(self, sample_rate):
        """
        Sets sample rate of data acquisition
        :param sample_rate: sample rate introduced by user
        :return:
        """
        self.sample_rate = sample_rate

    def set_n_samples(self, n_samples):
        """
        Sets number of samples in data acquisition
        :param n_samples: number of samples introduced by user
        :return:
        """
        self.n_samples = n_samples

    def get_sample_rate(self):
        """
        Sets sample rate of data acquisition
        :return: sample rate introduced by user
        """
        return self.sample_rate

    def get_n_samples(self):
        """
        Sets number of samples in data acquisition
        :return: number of samples introduced by user
        """
        return self.n_samples

    def get_time_log(self):
        """
        Returns moment when the data acquisition started
        :return: string "date/month/year hour:minute:second"
        """
        return self.start_acquisition_time

    def get_alarm_min(self):
        """
        Returns min alarm value
        :return: min temperature in [ºC]
        """
        return self.alarm_min

    def get_alarm_max(self):
        """
        Return max alarm value
        :return: max temperature in [ºC]
        """
        return self.alarm_max

    def get_calibration(self):
        """
        Returns the calibration object
        :return:
        """
        repr_calibration = [repr(calibrations) for calibrations in self.calibrations_log]
        return self.calibrations_log[repr_calibration.index(self.calibration)]

    def disable_alarms(self):
        """
        Disables alarms
        :return:
        """
        self.alarm_max = None
        self.alarm_min = None

    def is_exit_requested(self):
        """
        Returns True if exit has been requested
        :return: bool
        """
        return self.exit_requested

    def has_data(self):
        """
        Returns true is there has been data collected
        :return: True: data > 0
        """
        return len(self) > 0

    def is_alarm_min_set(self):
        """
        Returns true if min alarm is set
        :return:
        """
        return self.alarm_min is not None

    def is_alarm_max_set(self):
        """
        Returns true if max alarm is set
        :return:
        """
        return self.alarm_max is not None

    def is_calibration_set(self):
        """
        Checks if there has been a calibration assigned
        :return: True if there has been
        """
        return self.calibration != ""

    def is_sampling_underway(self):
        """
        Checks if finite data acquisition is underway
        :return: True is the number of samples taken is smaller than the number of samples introduced by the user
        """
        return len(self) < self.n_samples

    def calculate_time_interval_ms(self):
        """
        Calculates period in milliseconds given a sample_rate in Hertz
        :return: calculated period in milliseconds
        """
        if self.sample_rate == 0:
            raise ValueError("Sample rate cannot be zero.")
        return (1 / self.sample_rate) * 1000

    def read_voltage(self):
        """
        Simulates the reading of the voltage by the DAQ

        returns:
            voltage (float): reading of voltage by the DAQ
        """
        self.set_task_start(0)
        match self.model:
            case 'USB-6211':
                # simulation of temperature reading by the DAQ
                voltage = self.task_ai_ao[0].read()
            case 'USB-6001':
                # simulation of temperature reading by the DAQ
                voltage = self.task_ai_ao[0].read()
            case 'USB-6002':
                # simulation of temperature reading by the DAQ
                voltage = self.task_ai_ao[0].read()
            case _:
                raise ValueError(f"No matching model found.\nExpected: {modelsDAQ}\nGot: {self.model}.")
        self.set_task_stop(0)
        return round(voltage, 3)

    def add_calibration_to_log(self, calibration):
        """
        Adds calibration parameters to log
        :param calibration: calibration object
        :return:
        """
        self.calibrations_log.append(calibration)

    def add_data(self, voltage_temperature: list, time_interval):
        """
        Given a voltage and temperature and time_interval, adds to data
        :param voltage_temperature: list [voltage, temperature]
        :param time_interval: time interval between sampling
        :return:
        """
        self.data.append(voltage_temperature)
        self.add_time(time_interval)

    def acquire_data(self, calibration, time_interval):
        """
        Reads voltage from DAQ, converts to temperature with calibration, adds points to data
        :param time_interval:
        :param calibration:
        :return:
        """
        # reads voltage
        voltage = self.read_voltage()
        # calculates temperature
        temperature = calibration.calculate_temperature(voltage)
        # adds data
        self.add_data([voltage, temperature], time_interval)

    def add_time(self, time_interval):
        if not self.time_intervals:
            # If the list is empty, adds the first value starting from 0
            self.time_intervals.append(0)
        else:
            # If the list is not empty, adds the next value with the given interval
            self.time_intervals.append(int(self.time_intervals[-1] + time_interval))

    def add_alarms_log(self, is_min):
        alarm_entry = {
            'Alarm Type': 'Below Minimum' if is_min else 'Above Maximum',
            'Temperature': self[-1][1],
            'Time Interval': self.time_intervals[-1]
        }
        self.alarms_log.append(alarm_entry)

    def clear_data_acquisition(self):
        """
        Clears stored information from past logs like the data, parameters and time
        :return:
        """
        self.data.clear()
        self.time_intervals.clear()
        self.alarms_log.clear()
        self.sample_rate = None
        self.n_samples = None
        self.start_acquisition_time = ""

    def save_data_acquisition(self, file_name):
        if not file_name.lower().endswith(".csv"):
            file_name += ".csv"
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)

            # writes date and time
            writer.writerow([self.start_acquisition_time])
            writer.writerow([])

            # writes calibration
            writer.writerow(["CALIBRATION"])
            writer.writerow([self.calibration])
            writer.writerow([])

            # writes number of samples and sample rate
            writer.writerow(["PARAMETERS"])
            writer.writerow(["Number of samples", "Sample rate [Sa/s]"])
            writer.writerow([self.n_samples, self.sample_rate])
            writer.writerow([])

            # writes alarm logs
            writer.writerow(["ALARM LOGS"])
            writer.writerow(["Min alarm", "Max alarm"])
            writer.writerow([self.alarm_min, self.alarm_max])
            dic_writer = csv.DictWriter(file, fieldnames=alarm_log_fieldnames)
            dic_writer.writeheader()
            for entry in self.alarms_log:
                dic_writer.writerow(entry)
            writer.writerow([])

            # writes data
            writer.writerow(["DATA"])
            writer.writerow(["Voltage [V]", "Temperature [ºC]"])
            for voltage, temperature in self.data:
                writer.writerow([voltage, temperature])

    def generate_index_list(self):
        """
        Generates a list that goes from 1 to the number of data samples stored
        :return:
        """
        return [i for i in range(1, len(self.data) + 1)]

    def trigger_alarms(self, window, alarm_icon_keys):
        """
        Checks if alarms should be triggered and if so logs and triggers them
        :param window: gui window
        :param alarm_icon_keys: ['-MIN_TEMP_ICON-', '-MAX_TEMP_ICON-']
        :return:
        """
        if self.is_alarm_min_set():
            if self[-1][1] < self.get_alarm_min():
                self.add_alarms_log(is_min=True)
                window[alarm_icon_keys[0]].metadata = True
            else:
                window[alarm_icon_keys[0]].metadata = False
        if self.is_alarm_max_set():
            if self[-1][1] > self.get_alarm_max():
                self.add_alarms_log(is_min=False)
                window[alarm_icon_keys[1]].metadata = True
            else:
                window[alarm_icon_keys[1]].metadata = False

    def trigger_alarm_icon(self, window, alarm_icon_keys):
        # update min alarm image
        window[alarm_icon_keys[0]].update(
            source=gt.ALARM_MIN_ON_PATH if window[alarm_icon_keys[0]].metadata else
            (gt.ALARM_MIN_OFF_PATH if self.is_alarm_min_set() else gt.ALARM_UNSET_PATH))
        # update max alarm image
        window[alarm_icon_keys[1]].update(
            source=gt.ALARM_MAX_ON_PATH if window[alarm_icon_keys[1]].metadata else
            (gt.ALARM_MAX_OFF_PATH if self.is_alarm_max_set() else gt.ALARM_UNSET_PATH))

    def perform_data_acquisition(self, window, fig, figure_canvas_agg, calibration, time_interval, alarm_icon_keys):
        self.acquire_data(calibration, time_interval)
        self.update_figure(fig, figure_canvas_agg)
        self.trigger_alarms(window, alarm_icon_keys)

    def update_figure(self, fig, figure_canvas_agg):
        axes = fig.axes  # getting the subplots
        axes[0].clear()
        axes[0].set_xlabel("Readings (ms)")
        axes[0].set_ylabel("Temperature (ºC)")
        axes[0].grid()
        if self.has_data():
            self.plot_temperature_points(axes)
        if self.is_alarm_min_set() or self.is_alarm_max_set():
            self.plot_temperature_alarms(axes)

        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    def plot_temperature_alarms(self, axes):

        x = [0, self.time_intervals[-1] if self.has_data() else 10]

        if self.is_alarm_min_set():
            y = [self.alarm_min] * 2
            axes[0].plot(x, y, 'b--')
        if self.is_alarm_max_set():
            y = [self.alarm_max] * 2
            axes[0].plot(x, y, 'r--')

    def plot_temperature_points(self, axes):
        x = self.time_intervals
        y = [temperature[1] for temperature in self.data]
        axes[0].plot(x, y, color='orange', linestyle='-')

    def set_task_start(self, index_ai_ao):
        self.task_ai_ao[index_ai_ao].start()

    def set_task_stop(self, index_ai_ao):
        self.task_ai_ao[index_ai_ao].stop()

    def set_task_write(self, value: float):
        self.task_ai_ao[1].write(value)

    def initiate_daq(self):
        self.set_tasks()
        # assignation of analog input
        self.add_analog_input()
        # assignation of analog output
        self.add_analog_output()

    def add_analog_input(self):
        """
        Defines analog input in DAQ
        :return:
        """
        self.task_ai_ao[0].ai_channels.add_ai_voltage_chan("Dev1/ai0", terminal_config=TerminalConfiguration.DIFF)

    def add_analog_output(self):
        self.task_ai_ao[1].ao_channels.add_ao_voltage_chan("Dev1/ao0", AO_DAQ_NAME,
                                                           min_val=AO_DAQ_MIN_VAL, max_val=AO_DAQ_MAX_VAL)

    def exit(self):
        print("Exit requested before calibration")
        self.set_task_stop(0)
        self.set_task_stop(1)
