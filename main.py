import sys
import os

import src.app.appDAQ as daq
import src.app.appCalibrationMethod as calibration_method
import src.app.appDataAcquisition as data_acquisition

# Gets the path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Adds the parent directory (project root) to the Python path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


def main():

    # --- DAQ SELECTION ---
    niDAQ = daq.run_select_daq()
    while not niDAQ.is_exit_requested():
        # --- CALIBRATION ---
        calibration_method.run_calibrate(niDAQ)
        if niDAQ.is_exit_requested():
            niDAQ.exit()
            continue
        # --- ACQUIRE DATA ---
        data_acquisition.run_data_acquisition(niDAQ)


if __name__ == "__main__":
    main()
