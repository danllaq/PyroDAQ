import src.guiTools as gt

from src.guiTools import sg


def get_layout_no_calibration():
    """
    Defines layout for the window when there is no calibration set
    :return: list with the layout
    """
    sg.theme(gt.DEFAULT_THEME)
    column = sg.Column([
        [sg.Push(), sg.Image(gt.ICON_PATH, size=(200, 200)), sg.Push()],
        [sg.Frame('Calibration Expression', [
            [sg.Text('No calibration yet...', pad=(10, 10))]
        ], element_justification='center', expand_x=True, pad=(10, 10), relief=sg.RELIEF_RAISED)],
        [sg.Text('Choose Calibration Method:')],
        [sg.Radio(gt.CAL_METHOD_TEMP_VOLT, group_id="calMethod", k='-TEMP_AND_VOLT-', default=True,
                  enable_events=True)],
        [sg.Radio(gt.CAL_METHOD_EXP, group_id="calMethod", k='-EXP-', default=False, enable_events=True)],
        [sg.Push(),
         sg.Button('Calibrate', key="-CALIBRATE-"),
         sg.Button('Acquire Data', key='-DATA-', visible=False)]
    ], pad=((0, 0), (0, 110)))
    layout = [
        [sg.VPush()],
        [column],
        [sg.VPush()]
    ]
    return layout


def calibration_method_window(layout):
    """
    Creates window for the calibration menu
    :param layout: desired layout to show in the window
    :return: pysimplegui window
    """
    return sg.Window("Sensor Calibration", layout, size=(gt.WINDOW_WIDTH, gt.WINDOW_HEIGHT),
                     element_justification='center')


def layout_with_expression(calibration_log):
    """
    Layout when there are already logged calibrations
    :param calibration_log: list of past calibrations
    :return: list with the layout
    """
    sg.theme(gt.DEFAULT_THEME)

    column = sg.Column([
        [sg.Push(), sg.Image(gt.ICON_PATH, size=(200, 200)), sg.Push()],
        [sg.Frame('Calibration Expression', [
            [sg.Combo(calibration_log,
                      default_value=calibration_log[0],
                      key='-CALIBRATIONS_LOG-',
                      expand_x=True,
                      enable_events=True,
                      pad=(10, 10))],
        ], element_justification='center', expand_x=True, pad=(10, 10), relief=sg.RELIEF_RAISED)],
        [sg.Text('Choose Calibration Method:')],
        [sg.Radio(gt.CAL_METHOD_TEMP_VOLT, group_id="calMethod", k='-TEMP_AND_VOLT-', default=True,
                  enable_events=True)],
        [sg.Radio(gt.CAL_METHOD_EXP, group_id="calMethod", k='-EXP-', default=False, enable_events=True)],
        [sg.Push(),
         sg.Button('Calibrate', key="-CALIBRATE-"),
         sg.Button('Acquire Data', key='-DATA-', visible=True)]
    ], pad=((0, 0), (0, 110)))

    layout = [
        [sg.VPush()],
        [column],
        [sg.VPush()]
    ]
    return layout


def run_calibration_method_no_calibration_window(window):
    """
    Runs pysimplegui window behavior when there is no calibration set
    :param window: pysimplegui window
    :return: string with the option selected by user['EXIT', 'EXPRESSION_INPUT', 'ACQUIRE_DATA']
    """

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            window.close()
            return 'EXIT'

        if event == '-CALIBRATE-':
            if values['-TEMP_AND_VOLT-']:
                window.close()
                return 'TEMP_VOLTAGE'
            elif values['-EXP-']:
                window.close()
                return 'EXPRESSION_INPUT'

        if event == '-DATA-':
            window.close()
            return 'ACQUIRE_DATA'


def run_calibration_method_window(window, niDAQ):
    """
    Runs pysimplegui window behavior when there are calibrations logged
    :param window: pysimplegui window
    :param niDAQ: object with past calibrations
    :return: string with the option selected by user['EXIT', 'EXPRESSION_INPUT', 'ACQUIRE_DATA']
    """
    while True:
        event, values = window.read()  # window.read returns event and values

        if event == sg.WIN_CLOSED:
            window.close()
            return 'EXIT'

        if event == '-CALIBRATIONS_LOG-':
            niDAQ.set_calibration(values['-CALIBRATIONS_LOG-'])

        if event == '-CALIBRATE-':
            if values['-TEMP_AND_VOLT-']:
                window.close()
                return 'TEMP_VOLTAGE'
            elif values['-EXP-']:
                window.close()
                return 'EXPRESSION_INPUT'

        if event == '-DATA-':
            window.close()
            return 'ACQUIRE_DATA'
