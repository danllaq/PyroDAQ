import src.gui.guiTempVoltCalibrate as guiTempVoltCalibrate


def run_temp_volt_calibrate(niDAQ):
    """
    Runs temperature-voltage relation calibration
    :param niDAQ: object where calibration will be stored
    :return: object with the calibration information
    """
    # launches window where the user can input voltage and temperature and an expression will be calculated
    window, fig, figure_canvas_agg = guiTempVoltCalibrate.temp_volt_calibrate_window()
    niDAQ.set_task_start(1)
    niDAQ.set_task_write(1)
    # the window returns either a '1' if the user has chosen an expression or -1 if they want to go back or close window
    calibration = guiTempVoltCalibrate.temp_volt_calibrate_window_behavior(niDAQ, window, fig, figure_canvas_agg)
    niDAQ.set_task_stop(1)
    return calibration
