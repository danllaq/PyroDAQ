import src.gui.guiCalibrationMethod as guiCalibrationMethod
import src.app.appTempVoltCalibrate as appTempVoltCalibrate
import src.app.appExpressionInputCalibrate as appExpressionInputCalibrate


def run_calibrate(niDAQ):
    """
    Runs calibrate menu
    :param niDAQ: object with DAQ information and where all things related is stored
    :return:
    """
    while True:
        try:
            if niDAQ.is_calibration_set():
                layout = guiCalibrationMethod.layout_with_expression(niDAQ.calibrations_log)
                # launches window where calibration expression and/or method will be selected
                window = guiCalibrationMethod.calibration_method_window(layout)
                method = guiCalibrationMethod.run_calibration_method_window(window, niDAQ)
            else:
                layout = guiCalibrationMethod.get_layout_no_calibration()
                window = guiCalibrationMethod.calibration_method_window(layout)
                method = guiCalibrationMethod.run_calibration_method_no_calibration_window(window)
            match method:
                case 'TEMP_VOLTAGE':
                    calibration = appTempVoltCalibrate.run_temp_volt_calibrate(niDAQ)
                    if calibration is not None:
                        niDAQ.add_calibration_to_log(calibration)
                        niDAQ.set_calibration(repr(calibration))
                case 'EXPRESSION_INPUT':
                    calibration = appExpressionInputCalibrate.run_expression_input_calibrate(niDAQ)
                    if calibration is not None:
                        niDAQ.add_calibration_to_log(calibration)
                        niDAQ.set_calibration(repr(calibration))
                case 'ACQUIRE_DATA':
                    if niDAQ.is_calibration_set:
                        break
                    else:
                        raise ValueError("No calibration assigned")
                case 'EXIT':
                    niDAQ.set_exit_request()
                    break
                case _:
                    raise ValueError("Wrong calibration method chosen.")
        except ValueError as e:
            print(f"Error: {e}")
