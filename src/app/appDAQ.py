import src.daqTools as dt
import src.gui.guiDAQ as guiDAQ


def run_select_daq():
    """
    Runs daq selection
    :return:
    """
    while True:
        try:
            # creates object where DAQ information is stored
            modelsDAQ, exitFlag = guiDAQ.select_daq_window(dt.modelsDAQ)
            # DAQ initiation with its corresponding model
            niDAQ = dt.niDAQ(modelsDAQ, exitFlag)
            if not exitFlag:
                niDAQ.initiate_daq()
            return niDAQ
        except ValueError as e:
            guiDAQ.no_daq_detected_popup(e)
