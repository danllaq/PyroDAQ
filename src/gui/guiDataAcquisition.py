import src.guiTools as gt
from src.guiTools import sg

alarm_input_keys = ['-MIN_TEMP_INPUT-', '-MAX_TEMP_INPUT-']
alarm_icon_keys = ['-MIN_ALARM_ICON-', '-MAX_ALARM_ICON-']
parameters_input_keys = ['-N_SAMPLES_INPUT-', '-SAMPLE_RATE_INPUT-']


def data_acquisition_window(calibration_expression):
    """
    Pysimplegui layout and window for data acquisition
    :param calibration_expression: string with current calibration expression
    :return: pysimplegui window with relevant layout
    """
    sg.theme(gt.DEFAULT_THEME)

    first_column = sg.Column([
        [sg.Button('Recalibrate', k='-RECALIBRATE-')],
        [sg.VPush()],
        [sg.Frame('Calibration', [
            [sg.Text(calibration_expression, pad=(10, 10))]
        ], element_justification='center', expand_x=True, pad=(10, 10), relief=sg.RELIEF_RAISED)],
        [sg.Frame('Temperature Alarms', [
            [sg.Column([
                [sg.Text('Min ='),
                 sg.Input(size=gt.SIZE_INPUT, key='-MIN_TEMP_INPUT-', enable_events=True),
                 sg.Text(' [ºC]')],
                [sg.Image(gt.ALARM_UNSET_PATH, key='-MIN_ALARM_ICON-', metadata=False)],
                [sg.Text('Unset', key='-MIN_TEMP_TXT-')]
            ], element_justification='center'),
                sg.Column([
                    [sg.Text('Max ='),
                     sg.Input(size=gt.SIZE_INPUT, key='-MAX_TEMP_INPUT-', enable_events=True),
                     sg.Text(' [ºC]')],
                    [sg.Image(gt.ALARM_UNSET_PATH, key='-MAX_ALARM_ICON-', metadata=False)],
                    [sg.Text('Unset', key='-MAX_TEMP_TXT-')]
                ], element_justification='center'),
                sg.Column([
                    [sg.Push()]
                ]),
                sg.Column([
                    [sg.VPush()],
                    [sg.Push(), sg.Button('Set', k='-SET-')],
                    [sg.Push(), sg.Button('Disable', k='-DISABLE-', visible=False)]
                ], element_justification='right')
            ]
        ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_SUNKEN)],
        [sg.Frame('Choose Data Acquisition Type:', [
            [sg.Radio(gt.DATA_ON_DEMAND,
                      group_id='acq_type',
                      default=True,
                      k='-ON_DEMAND-',
                      enable_events=True,
                      pad=((10, 0), (10, 0)))],
            [sg.Radio(gt.DATA_CUSTOM, group_id='acq_type', k='-FINITE_SAMPLING-', enable_events=True,
                      pad=((10, 0), (10, 0)))],
            [sg.Text('No. Samples:', pad=((40, 0), 0)),
             sg.Input(size=gt.SIZE_INPUT, key='-N_SAMPLES_INPUT-', disabled=True, enable_events=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1])],
            [sg.Text('Sample Rate:', pad=((40, 0), (0, 10))),
             sg.Input(size=gt.SIZE_INPUT, key='-SAMPLE_RATE_INPUT-', disabled=True, enable_events=True,
                      disabled_readonly_background_color=sg.theme_button_color()[1], pad=(0, (0, 10))),
             sg.Text('Sa/s', pad=((0, 10), (0, 10)))]
        ], expand_x=True, pad=(10, 10), relief=sg.RELIEF_SUNKEN)],
        [sg.Push(), sg.Button('Acquire Data', k='-ACQUIRE-', metadata=False)],
        [sg.Frame('Time Interval [ms]', [
            [sg.Slider(range=(gt.MIN_TIME_UPDATE_MS, gt.MAX_TIME_INTERVAL_MS), default_value=500, resolution=10,
                       orientation='h', key='-SLIDER-', size=(40, 15), tick_interval=1000)]
        ], key='-TIME_INTERVAL-', visible=False, expand_x=True, pad=(10, 10), element_justification='center',
                  relief=sg.RELIEF_SUNKEN)],
        [sg.VPush()]

    ], expand_x=True, expand_y=True)

    second_column = sg.Column([
        [sg.Push(),
         sg.Text("Samples Collected: ", key='-SAMPLES_COLLECTED_TXT-', visible=False),
         sg.Text("", key='-SAMPLES_COLLECTED_VALUE-', size=gt.SIZE_INPUT, visible=False)],
        [sg.Canvas(k='-CANVAS-', size=(200, 200))],
        [sg.Button('Stop', k='-STOP-', visible=False, pad=(10, 10)),
         sg.Button('Reset', k='-RESET-', visible=False, pad=(10, 10))],
        [sg.Push(), sg.Button('Save Data', k='-SAVE-', visible=False)]
    ], expand_x=True, element_justification='center')

    layout = [
        [sg.VPush()],
        [first_column, second_column],
        [sg.VPush()]
    ]
    return gt.gui_window_with_graph('Data Acquisition', layout, gt.FIG_SIZE_WIDTH, gt.FIG_SIZE_HEIGHT, False)


def data_acquisition_window_behavior(niDAQ, window, fig, figure_canvas_agg):
    """
    Data acquisition window behavior
    :param niDAQ: object where data will be stored
    :param window: pysimplegui window with data acquisition layout
    :param fig: data plot
    :param figure_canvas_agg: canvas for the data plot
    :return:
    """
    time_interval = None
    min_frequency = gt.calculate_frequency(gt.MAX_TIME_INTERVAL_MS) * 1000
    max_frequency = gt.calculate_frequency(gt.MIN_TIME_UPDATE_MS) * 1000

    while True:
        event, values = window.read(timeout=time_interval)
        if event == sg.WIN_CLOSED:
            niDAQ.set_exit_request()
            break

        if event == '-RECALIBRATE-':
            break

        # only accepts digits, decimal point '.' and '-'
        if event in alarm_input_keys:
            gt.filter_numeric_characters(window, values, event, alarm_input_keys)

        # only accepts digits
        if event in parameters_input_keys:
            gt.filter_digits(window, values, event, ['-N_SAMPLES_INPUT-'])
            gt.filter_numeric_characters(window, values, event, ['-SAMPLE_RATE_INPUT-'])

        if event == '-SET-':
            try:
                # checks if both inputs are empty
                if all(values[key] == "" for key in alarm_input_keys):
                    raise ValueError("Values must be assigned")
                elif all(values[key] != "" for key in alarm_input_keys):
                    alarm_min, alarm_max = gt.to_number_n_dec(gt.N_DECIMALS, values['-MIN_TEMP_INPUT-'],
                                                              values['-MAX_TEMP_INPUT-'])
                    if alarm_min >= alarm_max:
                        raise ValueError("Min alarm can't be bigger or equal to max alarm")
                    niDAQ.set_alarm_min(alarm_min)
                    niDAQ.set_alarm_max(alarm_max)
                else:
                    if values['-MIN_TEMP_INPUT-'] != "":
                        [alarm_min] = gt.to_number_n_dec(gt.N_DECIMALS, values['-MIN_TEMP_INPUT-'])
                        if niDAQ.is_alarm_max_set() and (alarm_min >= niDAQ.get_alarm_max()):
                            raise ValueError("Min alarm can't be bigger or equal to already set max alarm")
                        else:
                            niDAQ.set_alarm_min(alarm_min)
                    if values['-MAX_TEMP_INPUT-'] != "":
                        [alarm_max] = gt.to_number_n_dec(gt.N_DECIMALS, values['-MAX_TEMP_INPUT-'])
                        if niDAQ.is_alarm_min_set() and (alarm_max <= niDAQ.get_alarm_min()):
                            raise ValueError("Max alarm can't be bigger or equal to already set min alarm")
                        else:
                            niDAQ.set_alarm_max(alarm_max)
                niDAQ.update_figure(fig, figure_canvas_agg)
                niDAQ.trigger_alarm_icon(window, alarm_icon_keys)
                gt.set_visible(window, True, '-DISABLE-')
            except Exception as e:
                sg.popup_error(str(e), title="Error")

            gt.empty_inputs(window, '-MIN_TEMP_INPUT-', '-MAX_TEMP_INPUT-')

        if event == '-DISABLE-':
            niDAQ.disable_alarms()
            window[alarm_icon_keys[0]].metadata = False
            window[alarm_icon_keys[1]].metadata = False
            niDAQ.trigger_alarm_icon(window, alarm_icon_keys)
            niDAQ.update_figure(fig, figure_canvas_agg)
            gt.set_visible(window, False, '-DISABLE-')

        if event == '-ON_DEMAND-':
            gt.set_disabled(window, True, '-N_SAMPLES_INPUT-', '-SAMPLE_RATE_INPUT-')

        if event == '-FINITE_SAMPLING-':
            gt.set_disabled(window, False, '-N_SAMPLES_INPUT-', '-SAMPLE_RATE_INPUT-')

        if event == '-ACQUIRE-':
            # saves moment in time when acquisition starts
            niDAQ.clear_data_acquisition()
            niDAQ.set_time_log()
            # if on demand data acquisition is selected
            if values['-ON_DEMAND-']:
                # from not reading to on demand
                window['-ACQUIRE-'].metadata = True
                gt.set_visible(window, True, '-STOP-', '-TIME_INTERVAL-')
                gt.set_visible(window, False, '-SAVE-')
                gt.set_disabled(window, True, '-FINITE_SAMPLING-')
            elif values['-FINITE_SAMPLING-']:
                try:
                    [sample_rate] = gt.check_if_valid_input(values, gt.N_DECIMALS, '-SAMPLE_RATE_INPUT-')
                    [n_samples] = gt.check_if_valid_input(values, 0, '-N_SAMPLES_INPUT-')
                    if not min_frequency <= sample_rate <= max_frequency:
                        raise ValueError(f"Sample rate must be between"
                                         f" {min_frequency:.3f} and {max_frequency:.3f} Sa/s."
                                         f"\nGot {sample_rate} instead.")
                    elif not 2 <= n_samples <= 10000:
                        raise ValueError(f"Number of samples must be between  2 and 10k.\n"
                                         f"Got {n_samples} instead.")
                    else:
                        niDAQ.set_sample_rate(sample_rate)
                        niDAQ.set_n_samples(n_samples)
                        # from not reading to finite sampling
                        window['-ACQUIRE-'].metadata = True
                        # sets time_interval
                        time_interval = niDAQ.calculate_time_interval_ms()
                        gt.set_visible(window, True, '-STOP-')
                        gt.set_visible(window, False, '-SAVE-', '-ACQUIRE-')
                except Exception as e:
                    sg.popup_error(str(e), title="Error")
                    gt.empty_inputs(window, '-SAMPLE_RATE_INPUT-', '-N_SAMPLES_INPUT-')

        if event == '-STOP-':
            window['-ACQUIRE-'].metadata = False
            gt.set_visible(window, False, '-STOP-')
            gt.set_visible(window, True, '-RESET-', '-ACQUIRE-')
            if values['-ON_DEMAND-']:
                gt.set_disabled(window, False, '-FINITE_SAMPLING-')
            if values['-FINITE_SAMPLING-']:
                gt.set_visible(window, True, '-SAVE-')

        if event == '-SAVE-':
            try:
                file_name = sg.popup_get_file("Save CSV File", default_path=gt.get_desktop_dir(),
                                              default_extension="*.csv", save_as=True,
                                              file_types=(("CSV Files", "*.csv"),))
                if file_name == '' or file_name[-1] == '/':
                    raise ValueError("File name can't be empty.")
                elif file_name is not None:
                    niDAQ.save_data_acquisition(file_name)
                else:
                    raise ValueError("Couldn't save file.")
                sg.popup("Success", "Data saved to CSV successfully!")
            except Exception as e:
                sg.popup_error(str(e), title="Error")

        if event == '-RESET-':
            niDAQ.clear_data_acquisition()
            niDAQ.update_figure(fig, figure_canvas_agg)
            gt.set_visible(window, False, '-RESET-', '-SAVE-', '-SAMPLES_COLLECTED_TXT-', '-SAMPLES_COLLECTED_VALUE-')

        window['-MIN_TEMP_TXT-'].update(f"{niDAQ.get_alarm_min()} [ºC]" if niDAQ.is_alarm_min_set() else 'Unset')
        window['-MAX_TEMP_TXT-'].update(f"{niDAQ.get_alarm_max()} [ºC]" if niDAQ.is_alarm_max_set() else 'Unset')

        if window['-ACQUIRE-'].metadata:
            gt.set_disabled(window, True, '-N_SAMPLES_INPUT-', '-SAMPLE_RATE_INPUT-')
            gt.set_visible(window, False, '-RESET-', '-ACQUIRE-')
            gt.set_visible(window, True, '-SAMPLES_COLLECTED_TXT-', '-SAMPLES_COLLECTED_VALUE-')
            if values['-ON_DEMAND-']:
                time_interval = values['-SLIDER-']
                niDAQ.perform_data_acquisition(window, fig, figure_canvas_agg,
                                               niDAQ.get_calibration(), time_interval, alarm_icon_keys)
            elif values['-FINITE_SAMPLING-']:
                if niDAQ.is_sampling_underway():
                    niDAQ.perform_data_acquisition(window, fig, figure_canvas_agg,
                                                   niDAQ.get_calibration(), time_interval, alarm_icon_keys)
                else:
                    window['-ACQUIRE-'].metadata = False
                    gt.set_visible(window, True, '-RESET-', '-SAVE-', '-ACQUIRE-')
                    gt.set_visible(window, False, '-STOP-')
            else:
                raise ValueError("Acquiring data incorrectly")
            window['-SAMPLES_COLLECTED_VALUE-'].update(len(niDAQ))
            niDAQ.trigger_alarm_icon(window, alarm_icon_keys)

        else:
            gt.set_disabled(window, False, '-ACQUIRE-')
            time_interval = None
            if values['-ON_DEMAND-']:
                gt.set_visible(window, False, '-TIME_INTERVAL-')
            if values['-FINITE_SAMPLING-']:
                gt.set_disabled(window, False, '-N_SAMPLES_INPUT-', '-SAMPLE_RATE_INPUT-')

    window.close()
