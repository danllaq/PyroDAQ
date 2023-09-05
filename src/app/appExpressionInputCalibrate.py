import src.gui.guiExpressionInputCalibrate as guiExpressionInputCalibrate


def run_expression_input_calibrate(niDAQ):
    """
    Runs expression input calibration
    :param niDAQ: object where calibration will be stored
    :return: object with the calibration information
    """
    # launches window where the user can input calibration expression
    window, fig, figure_canvas_agg = guiExpressionInputCalibrate.expression_calibrate_window()
    # the window returns either a '1' if the user has chosen an expression or -1 if they want to go back or close window
    niDAQ.set_task_start(1)
    niDAQ.set_task_write(1)
    calibration = guiExpressionInputCalibrate.expression_input_calibrate_window_behavior(niDAQ, window,
                                                                                         fig, figure_canvas_agg)
    niDAQ.set_task_stop(1)
    return calibration
