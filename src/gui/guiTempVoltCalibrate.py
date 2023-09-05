import src.calibrationTools as ct
import time

import src.guiTools as gt

from src.guiTools import sg

text_input_keys = ['-V_INPUT-', '-T_INPUT-']


def select_points_window(data: list):
    """
    Behaviour for window with layout for selecting points in the interpolation method
    :param data: pair list with data points
    :return: list with two data points selected
    """
    sg.theme(gt.ACCENT_THEME)

    data_sorted = gt.sort_pair_list_by_x(list(data))
    available_points = list(data_sorted)

    column_left = sg.Column([
        [sg.Canvas(key='-CANVAS-')]
    ])

    column_right = sg.Column([
        [sg.Table(values=data_sorted,
                  headings=['Voltage (V)', 'Temperature (ºC)'],
                  k='-TABLE-',
                  selected_row_colors='green on white',
                  enable_click_events=True)],
        [sg.Push(), sg.Button('Select', k='-SELECT-')],
        [sg.Frame('Selected Points: ', [
            [sg.Text('list of points...', k='-POINTS-')]
        ], expand_x=True)],
        [sg.Push(), sg.Button("Choose", k='-CHOOSE-', visible=False)]
    ])

    layout = [
        [sg.VPush()],
        [column_left, column_right],
        [sg.VPush()]
    ]

    window, fig, figure_canvas_agg = gt.gui_window_with_graph("Choose Points", layout,
                                                              gt.FIG_SIZE_WIDTH, gt.FIG_SIZE_HEIGHT, True)

    axes, x, y = gt.get_axes_for_points(fig, data_sorted)
    gt.draw_points(axes, x, y, 'bo', "Data Points")
    axes[0].legend()
    gt.pack_canvas(figure_canvas_agg)

    selected_points = []

    while True:
        event, values = window.read()

        axes, x, y = gt.get_axes_for_points(fig, data_sorted)
        gt.draw_points(axes, x, y, 'bo', "Data Points")

        if event == sg.WIN_CLOSED:
            break

        if event == '-CHOOSE-':
            window.close()
            return gt.sort_pair_list_by_x(selected_points)

        if isinstance(event, tuple):
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            if event[0] == '-TABLE-':
                if event[2][0] not in [-1, None]:  # Header was clicked and wasn't the "row" column
                    gt.draw_points(axes, available_points[event[2][0]][0], available_points[event[2][0]][1], 'yo')

        if event == '-SELECT-':
            if values['-TABLE-']:
                selected_row = values['-TABLE-'][0]

                if len(selected_points) >= 2:
                    available_points.append(selected_points[0])
                    selected_points.pop(0)  # Remove the oldest point
                selected_points.append(available_points[selected_row])  # Add the selected point
                available_points.pop(selected_row)
                available_points = gt.sort_pair_list_by_x(available_points)

                window['-TABLE-'].update(values=available_points)  # Clear the table selection
                window['-POINTS-'].update(selected_points)

        if selected_points:
            gt.draw_points(axes, gt.get_sorted_nth_elements(selected_points, 0),
                           gt.get_sorted_nth_elements(selected_points, 1), 'r-o', "Selected Points")
            if len(selected_points) > 1:
                gt.set_visible(window, True, '-CHOOSE-')

        axes[0].legend()
        gt.pack_canvas(figure_canvas_agg)

    window.close()


def temp_volt_calibrate_window():
    """
    Window and layout for temperature-voltage relation
    :return: window with layout
    """
    sg.theme(gt.DEFAULT_THEME)

    column_left = sg.Column([
                [sg.Frame('Choose Expression Type:', [
                    [sg.Radio(gt.TEMP_VOLT_LIN_EQ,
                              group_id='exp_type',
                              default=True,
                              k='-LINEAR_EQ-',
                              enable_events=True,
                              pad=((10, 0), (10, 0)))],
                    [sg.Radio(gt.TEMP_VOLT_LEAST_SQUARES,
                              pad=((40, 0), 0),
                              group_id='lin_eq',
                              default=True,
                              enable_events=True,
                              k='-LEAST_SQUARES-')],
                    [sg.Radio(gt.TEMP_VOLT_LIN_INTERP,
                              pad=((40, 0), 0),
                              group_id='lin_eq',
                              default=False,
                              enable_events=True,
                              k='-LINEAR_INTERPOLATION-'),
                     sg.Button("Choose Points",
                               k='-CHOOSE_POINTS-',
                               visible=False,
                               pad=((10, 0), 0), )],
                    [sg.Radio(gt.TEMP_VOLT_NON_LINEAR_EQ,
                              group_id='exp_type',
                              default=False,
                              k='-NON_LINEAR_EQ-',
                              enable_events=True,
                              pad=((10, 0), (10, 10)))]
                ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_SUNKEN)],
                [sg.Frame('Input Data:', [
                    [sg.Text("Type In", pad=(10, 0), k="-TOGGLE_OFF_TXT-", font=gt.FONT_BOLD),
                     sg.Button(image_filename=gt.TOGGLE_OFF_PATH,
                               key='-TOGGLE-',
                               button_color=(sg.theme_background_color(), sg.theme_background_color()),
                               border_width=0,
                               metadata=False),
                     sg.Text("Measure", k="-TOGGLE_ON_TXT-")],
                    [sg.Text('V =', k='-V_TXT-', pad=(10, 0)),
                     sg.Input(size=gt.SIZE_INPUT,
                              key='-V_INPUT-',
                              enable_events=True,
                              disabled_readonly_background_color=sg.theme_button_color()[1]),
                     sg.Text('T ='),
                     sg.Input(size=gt.SIZE_INPUT, key='-T_INPUT-', enable_events=True),
                     sg.Button('Enter', k='-ENTER-', bind_return_key=True, pad=((10, 0), (10, 10)))]
                ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_SUNKEN)],
                [sg.Table(values=[],
                          headings=['Voltage (V)', 'Temperature (ºC)'],
                          k='-TABLE-',
                          enable_click_events=True,
                          enable_events=True)],
                [sg.Text('Number of Samples: '),
                 sg.Text('0', k='-N_SAMPLES-'),
                 sg.Push(),
                 sg.Button('Clear', k='-CLEAR-', tooltip=" Clear table ", disabled=True),
                 sg.Button('Delete', k='-DELETE-', tooltip=" Delete last row ", disabled=True)]
            ])

    column_right = sg.Column([
                [sg.Frame('Calibration Equation',
                          [[sg.Text('Expression...',
                                    k='-EQ_EXPRESSION-',
                                    enable_events=True,
                                    metadata=False,
                                    pad=(10, 10)),
                            sg.Button("Copy", key="-COPY-", tooltip="Copy to clipboard", pad=(10, 10), visible=False)]
                           ],
                          expand_x=True,
                          expand_y=True,
                          pad=(10, 10),
                          element_justification='center',
                          relief=sg.RELIEF_RAISED)],
                [sg.Canvas(k='-CANVAS-', size=(200, 200))],
                [sg.Push(), sg.Button('Choose', k='-CHOOSE-', disabled=True)]
            ])

    layout = [
        [sg.VPush()],
        [column_left, column_right],
        [sg.VPush()],
    ]

    return gt.gui_window_with_graph('Known Temperature-Voltage Sensor Calibration Equation', layout,
                                    gt.FIG_SIZE_WIDTH, gt.FIG_SIZE_HEIGHT, False)


def temp_volt_calibrate_window_behavior(niDAQ, window, fig, figure_canvas_agg):
    """
    Behaviour for temperature-voltage relation window
    :param niDAQ: object
    :param window: pysimplegui window
    :param fig: calibration plot
    :param figure_canvas_agg: canvas for the calibration plot
    :return: object with set calibration
    """
    calibration = ct.LinearCalibration('LEAST_SQUARES')
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        if event == '-CHOOSE-':
            window.close()
            return calibration

        if event == '-LINEAR_EQ-':
            gt.set_disabled(window, False, '-LEAST_SQUARES-', '-LINEAR_INTERPOLATION-')
            if not calibration.is_type('LINEAR_EQUATION'):
                calibration = calibration.to_linear_calibration()

        if event == '-CHOOSE_POINTS-':
            calibration.set_chosen_points(select_points_window(calibration.get_data()))

        if event == '-NON_LINEAR_EQ-':
            gt.set_disabled(window, True, '-LEAST_SQUARES-', '-LINEAR_INTERPOLATION-')
            gt.set_visible(window, False, '-CHOOSE_POINTS-')
            if not calibration.is_type('NON_LINEAR_EQUATION'):
                calibration = calibration.to_nonlinear_calibration()
            elif window['-EQ_EXPRESSION-'].metadata:
                # To calculate a nonlinear function there must be at least 3 points
                window['-EQ_EXPRESSION-'].update("Waiting for 3 points...")

        # only accepts digits and decimal point '.'
        if event in ['-V_INPUT-', '-T_INPUT-']:
            gt.filter_numeric_characters(window, values, event, text_input_keys)

        if event == '-TOGGLE-':
            gt.gui_toggle_behaviour(window)

        if event == '-ENTER-':
            try:
                if values['-T_INPUT-'] == "":
                    raise ValueError("Values must be assigned")
                elif not gt.is_number(values['-T_INPUT-']):
                    raise ValueError("Values must be a numeric value.")

                if not window['-TOGGLE-'].metadata:
                    if values['-V_INPUT-'] == "":
                        raise ValueError("Values must be assigned")
                    elif not gt.is_number(values['-V_INPUT-']):
                        raise ValueError("Values must be a numeric value.")
                    inputValues = [float(values['-V_INPUT-']), float(values['-T_INPUT-'])]
                else:
                    inputValues = [niDAQ.read_voltage(), float(values['-T_INPUT-'])]

                if calibration.data_exists(inputValues):
                    raise ValueError("Data input is repeated.")

                calibration.add_data(inputValues)

            except ValueError as e:
                sg.popup_error(str(e), title="Error")

            window['-TABLE-'].update(values=calibration.data)
            window['-N_SAMPLES-'].update(len(calibration))
            window['-V_INPUT-'].update('')
            window['-T_INPUT-'].update('')

        if event == '-DELETE-':
            del calibration[-1]
            calibration.change_in_data(window, fig, figure_canvas_agg, known_expression=False)

        if event == '-CLEAR-':
            calibration.clear_data()
            calibration.change_in_data(window, fig, figure_canvas_agg, known_expression=False)

        if event == '-COPY-':
            window['-COPY-'].update('Text Copied!', disabled=True)
            sg.clipboard_set(repr(calibration))  # Copy the text to clipboard
            time.sleep(1)
            window['-COPY-'].update('Copy', disabled=False)

        if len(calibration) > 0:
            gt.set_disabled(window, False, '-CLEAR-', '-DELETE-')
            if values['-LINEAR_EQ-']:
                if len(calibration) > 1:
                    if values['-LEAST_SQUARES-']:
                        calibration.update_method('LEAST_SQUARES')
                        calibration.calculate_expression()
                    else:
                        calibration.update_method('LINEAR_INTERPOLATION')
                        if calibration.interpolation_points:
                            calibration.calculate_expression(calibration.interpolation_points[0],
                                                             calibration.interpolation_points[1])
                        else:
                            calibration.calculate_expression([calibration.sort_x()[0], calibration.sort_y()[0]],
                                                             [calibration.sort_x()[-1], calibration.sort_y()[-1]])

                    window['-EQ_EXPRESSION-'].update(repr(calibration))
                    window['-EQ_EXPRESSION-'].metadata = True
                else:
                    # To calculate a polynomial function there must be at least 2 points
                    window['-EQ_EXPRESSION-'].metadata = False
            elif values['-NON_LINEAR_EQ-']:
                if len(calibration) > 2:
                    calibration.calculate_expression()
                    window['-EQ_EXPRESSION-'].update(repr(calibration))
                    window['-EQ_EXPRESSION-'].metadata = True
                else:
                    window['-EQ_EXPRESSION-'].metadata = False
            calibration.update_figure(fig, figure_canvas_agg, known_expression=False)
        else:
            gt.set_disabled(window, True, '-CLEAR-', '-DELETE-')
            gt.set_visible(window, False, '-COPY-')
            window['-EQ_EXPRESSION-'].metadata = False

        if window['-EQ_EXPRESSION-'].metadata:
            gt.set_disabled(window, False, '-CHOOSE-')
            gt.set_visible(window, True, '-COPY-')
        else:
            gt.set_disabled(window, True, '-CHOOSE-')
            gt.set_visible(window, False, '-COPY-')
            # To calculate a linear function there must be at least 2 points
            window['-EQ_EXPRESSION-'].update(f"Waiting for "
                                             f"{'2' if calibration.is_type('LINEAR_EQUATION') else '3'} points...")

        gt.set_visible(window, values['-LINEAR_INTERPOLATION-'] and values['-LINEAR_EQ-'] and
                       window['-EQ_EXPRESSION-'].metadata, '-CHOOSE_POINTS-')

    window.close()
