import src.calibrationTools as ct
import src.guiTools as gt
from src.guiTools import sg
import time


text_input_keys = ['-A_INPUT-', '-B_INPUT-', '-C_INPUT-', '-M_INPUT-', '-N_INPUT-']


def expression_calibrate_window():
    """
    Window for direct expression
    :return: pysimplegui window with its layout
    """
    sg.theme(gt.DEFAULT_THEME)
    first_column = sg.Column([
        [sg.Frame('Choose Expression Type:', [
            [sg.Radio(gt.TEMP_VOLT_LIN_EQ,
                      group_id='exp_type',
                      default=True,
                      k='-LINEAR_EQ-',
                      enable_events=True,
                      pad=((10, 0), (10, 0)))],
            [sg.Text('m =', pad=((40, 0), 0), ),
             sg.Input(size=gt.SIZE_INPUT,
                      key='-M_INPUT-',
                      enable_events=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1]),
             sg.Text('n ='),
             sg.Input(size=gt.SIZE_INPUT,
                      key='-N_INPUT-',
                      enable_events=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1])],
            [sg.Radio(gt.TEMP_VOLT_NON_LINEAR_EQ,
                      group_id='exp_type',
                      default=False,
                      k='-NON_LINEAR_EQ-',
                      enable_events=True,
                      pad=((10, 0), (10, 10)))],
            [sg.Text('a =', pad=((40, 0), 0), ),
             sg.Input(size=gt.SIZE_INPUT,
                      key='-A_INPUT-',
                      enable_events=True,
                      disabled=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1]),
             sg.Text('b ='),
             sg.Input(size=gt.SIZE_INPUT,
                      key='-B_INPUT-',
                      enable_events=True,
                      disabled=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1]),
             sg.Text('c ='),
             sg.Input(size=gt.SIZE_INPUT,
                      key='-C_INPUT-',
                      enable_events=True,
                      disabled=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1])]
        ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_SUNKEN)],
        [sg.Push(), sg.Button('Enter', k='-ENTER-')],
        [sg.Frame('Calculated expression:', [
            [sg.Text("Calculating expression...", pad=(10, 10), k='-EQUATION-'),
             sg.Button("Copy", key="-COPY-", tooltip="Copy to clipboard", pad=((10, 10), (10, 10)), visible=False)],
        ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_RAISED, element_justification='center')],
        [sg.Frame('Voltage Input:', [
            [sg.Text("Type In", pad=(10, 0), k='-TOGGLE_OFF_TXT-', font=gt.FONT_BOLD),
             sg.Button(image_filename=gt.TOGGLE_OFF_PATH,
                       key='-TOGGLE-',
                       button_color=(sg.theme_background_color(), sg.theme_background_color()),
                       border_width=0,
                       metadata=False),
             sg.Text("Measure", k='-TOGGLE_ON_TXT-', font=gt.FONT_DEFAULT)],
            [sg.Text('V =', k='-V_TXT-', pad=(10, 10)),
             sg.Input(size=gt.SIZE_INPUT,
                      key='-V_INPUT-',
                      enable_events=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1]),
             sg.Text('[V]')]
        ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_SUNKEN)],
        [sg.Push(), sg.Button('Calculate', k='-CALCULATE-', disabled=True)]
    ])

    second_column = sg.Column(
        [
            [sg.Canvas(k='-CANVAS-', size=(200, 200))],
            [sg.Table(values=[],
                      headings=['Voltage (V)', 'Temperature (ºC)'],
                      k='-TABLE-',
                      num_rows=5,
                      enable_click_events=True,
                      enable_events=True,
                      expand_x=True)],
            [sg.Button('Clear', k='-CLEAR-', tooltip=" Clear table ", disabled=True),
             sg.Button('Delete', k='-DELETE-', tooltip=" Delete last row ", disabled=True)],
            [sg.Push(), sg.Button('Choose', k='-CHOOSE-', disabled=True)]
        ]
    )

    # Define the layout
    layout = [
        [sg.VPush()],
        [first_column, second_column],
        [sg.VPush()]
    ]

    return gt.gui_window_with_graph('Input Sensor Calibration Equation', layout,
                                    gt.FIG_SIZE_WIDTH, gt.FIG_SIZE_HEIGHT, False)


def expression_input_calibrate_window_behavior(niDAQ, window, fig, figure_canvas_agg):
    """
    Behaviour for direct expression input calibration window
    :param niDAQ: object
    :param window: pysimplegui window
    :param fig: calibration plot
    :param figure_canvas_agg: canvas for calibration plot
    :return: calibration object
    """
    calibration = ct.LinearCalibration()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == '-LINEAR_EQ-':
            gt.set_disabled(window, False, '-M_INPUT-', '-N_INPUT-')
            window['-A_INPUT-'].update('', disabled=True)
            window['-B_INPUT-'].update('', disabled=True)
            window['-C_INPUT-'].update('', disabled=True)

        if event == '-NON_LINEAR_EQ-':
            window['-M_INPUT-'].update('', disabled=True)
            window['-N_INPUT-'].update('', disabled=True)
            gt.set_disabled(window, False, '-A_INPUT-', '-B_INPUT-', '-C_INPUT-')

        if event == '-CHOOSE-':
            window.close()
            return calibration

        # only accepts digits, decimal point '.' and '-'
        if event in text_input_keys:
            gt.filter_numeric_characters(window, values, event, text_input_keys)

        if event == '-ENTER-':
            try:
                if values['-LINEAR_EQ-']:
                    # checks if any input value is empty
                    if any(values[key] == '' for key in ['-M_INPUT-', '-N_INPUT-']):
                        raise ValueError("Values must be assigned")
                    # checks if the input is a valid number
                    if any(not gt.is_number(values[key]) for key in ['-M_INPUT-', '-N_INPUT-']):
                        raise ValueError("Values must be a numeric value.")
                    # checks if equation type has changed
                    if calibration.is_type('LINEAR_EQUATION'):
                        # updates parameters
                        calibration.set_parameters(values['-M_INPUT-'], values['-N_INPUT-'])
                    else:
                        # changes object from nonlinear to linear calibration
                        calibration = calibration.to_linear_calibration(values['-M_INPUT-'], values['-N_INPUT-'])

                elif values['-NON_LINEAR_EQ-']:
                    # checks if any input is empty
                    if any(values[key] == '' for key in ['-A_INPUT-', '-B_INPUT-', '-C_INPUT-']):
                        raise ValueError("Values must be assigned")
                    # checks if the input is a valid number
                    if not any(gt.is_number(values[key]) for key in ['-A_INPUT-', '-B_INPUT-', '-C_INPUT-']):
                        raise ValueError("Values must be a numeric value.")
                    # checks if equation type has changed
                    if calibration.is_type('NON_LINEAR_EQUATION'):
                        # updates parameters
                        a, b, c = gt.to_number_n_dec(gt.N_DECIMALS,
                                                     values['-A_INPUT-'], values['-B_INPUT-'], values['-C_INPUT-'])
                        calibration.set_parameters(a, b, c)
                    else:
                        # changes object from nonlinear to linear calibration
                        calibration = calibration.to_nonlinear_calibration(values['-A_INPUT-'], values['-B_INPUT-'],
                                                                           values['-C_INPUT-'])

                window['-EQUATION-'].update(value=repr(calibration))
                gt.set_disabled(window, False, '-CHOOSE-', '-CALCULATE-')
                gt.set_visible(window, True, '-COPY-')
                # empties text inputs
                for key in text_input_keys:
                    window[key].update('')
                calibration.update_data()
                window['-TABLE-'].update(values=calibration.data)
                calibration.update_figure(fig, figure_canvas_agg, known_expression=True)
            except ValueError as e:
                sg.popup_error(str(e), title="Error")

        if isinstance(event, tuple):
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            # You can also call Table.get_last_clicked_position to get the cell clicked
            if event[0] == '-TABLE-':
                if event[2][0] not in [-1, None]:  # If an actual row was clicked
                    calibration.update_figure(fig, figure_canvas_agg,
                                              known_expression=True,
                                              is_point_selected=True,
                                              x_sel_point=calibration[event[2][0]][0],
                                              y_sel_point=calibration[event[2][0]][1])

        if event == '-DELETE-':
            del calibration[-1]
            calibration.change_in_data(window, fig, figure_canvas_agg, known_expression=True)
            calibration.update_figure(fig, figure_canvas_agg, known_expression=True)

        if event == '-CLEAR-':
            calibration.clear_data()
            calibration.change_in_data(window, fig, figure_canvas_agg, known_expression=True)
            calibration.update_figure(fig, figure_canvas_agg, known_expression=True)

        if event == '-COPY-':
            window['-COPY-'].update('Text Copied!', disabled=True)
            sg.clipboard_set(repr(calibration))  # Copy the text to clipboard
            time.sleep(1)
            window['-COPY-'].update('Copy', disabled=False)

        if event == '-TOGGLE-':
            gt.gui_toggle_behaviour(window)

        if event == '-CALCULATE-':
            try:
                if not window['-TOGGLE-'].metadata:
                    if values['-V_INPUT-'] == "":
                        raise ValueError("Values must be assigned")
                    elif not gt.is_number(values['-V_INPUT-']):
                        raise ValueError("Values must be a numeric value.")
                    inputVoltage = float(values['-V_INPUT-'])
                    if inputVoltage in calibration.data:
                        raise ValueError("Data input is repeated.")
                else:
                    inputVoltage = niDAQ.read_voltage()

                calibration.add_voltage(inputVoltage)

            except ValueError as e:
                sg.popup_error(str(e), title="Error")

            calibration.update_figure(fig, figure_canvas_agg, known_expression=True)
            window['-TABLE-'].update(values=calibration.data)
            window['-V_INPUT-'].update('')

        if len(calibration) > 0:
            gt.set_disabled(window, False, '-CLEAR-', '-DELETE-')
        else:
            gt.set_disabled(window, True, '-CLEAR-', '-DELETE-')

    window.close()
