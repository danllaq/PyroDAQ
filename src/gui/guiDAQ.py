import src.guiTools as gt

from src.guiTools import sg


def select_daq_window(modelDAQ):
    """
    Creates a window so that the user chooses their DAQ model

    Arguments:
        modelDAQ (str list): DAQ model list

    Returns:
        model: (str): DAQ model that the user has chosen
    """
    sg.theme(gt.DEFAULT_THEME)
    column = sg.Column([
        [sg.Push(), sg.Image(gt.ICON_PATH, size=(200, 200)), sg.Push()],
        [sg.Text('Select the model of the National Instruments DAQ:', pad=((0, 0), (15, 0)))],
        [sg.Combo(modelDAQ,
                  default_value="Select the model...",
                  key='-MODEL-',
                  expand_x=True,
                  tooltip='Select an option before moving forward')],
        [sg.Push(), sg.Button('OK', key='-OK-', bind_return_key=True)]
    ], pad=((0, 0), (0, 120)))
    layout = [
        [sg.VPush()],
        [column],
        [sg.VPush()]
    ]

    window = sg.Window('PyroDAQ', layout, size=(gt.WINDOW_WIDTH, gt.WINDOW_HEIGHT), element_justification='center')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            return None, True

        elif event == '-OK-':
            window['-MODEL-'].set_tooltip("")
            model = values['-MODEL-']
            window.close()
            return model, False


def no_daq_detected_popup(e):
    """
    Popup error window that warns there is no DAQ detected
    :param e: ValueError from trying to initiate DAQ
    :return:
    """
    sg.theme(gt.ACCENT_THEME)
    sg.Window('Error', [[sg.Text(f'No DAQ detected:\n{e}')]]).read()
