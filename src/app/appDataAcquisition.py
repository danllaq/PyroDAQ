import src.gui.guiDataAcquisition as guiDataAcquisition


def run_data_acquisition(niDAQ):
    """
    Runs data acquisition
    :param niDAQ: object where data will be stored
    :return:
    """
    # launches window where the user can input calibration expression
    window, fig, figure_canvas_agg = guiDataAcquisition.data_acquisition_window(niDAQ.calibration)
    niDAQ.set_task_start(1)
    niDAQ.set_task_write(1)
    guiDataAcquisition.data_acquisition_window_behavior(niDAQ, window, fig, figure_canvas_agg)
    niDAQ.set_task_stop(1)
