import matplotlib
import time
import re

import PySimpleGUI as sg

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pathlib import Path

# ---------- APPEARANCE ----------
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

FIG_SIZE_WIDTH = 5
FIG_SIZE_HEIGHT = 4

SIZE_INPUT = (7, 1)

DEFAULT_THEME = "GreenMono"
ACCENT_THEME = "LightGreen10"

FONT_DEFAULT = ('Helvetica', 10)
FONT_BOLD = ('Helvetica', 10, 'bold')

# ---------- TEXTS FOR WINDOWS ----------
# Calibration Method
CAL_METHOD_TEMP_VOLT = "Temperature and Voltage Relation"
CAL_METHOD_EXP = "Direct Expression Input"

# Temperature and Voltage Correlation
TEMP_VOLT_LIN_EQ = "Linear Equation"
TEMP_VOLT_LEAST_SQUARES = "Least Squares Method"
TEMP_VOLT_LIN_INTERP = "Linear Interpolation"
TEMP_VOLT_NON_LINEAR_EQ = "Non-linear Equation"

# Direct Expression Input
INP_EXP_LIN_EQ = "Linear Equation",
INP_EXP_NON_LIN = "Non-linear Equation"

# Data Acquisition
DATA_ON_DEMAND = "On Demand"
DATA_CUSTOM = "Finite Sampling"

# -------- IMAGE PATHS ---------
ICON_PATH = '/assets/icon_big.png'
TOGGLE_ON_PATH = '/assets/switch_on.png'
TOGGLE_OFF_PATH = '/assets/switch_off.png'
ALARM_MIN_ON_PATH = '/assets/alarm_min_on.png'
ALARM_MIN_OFF_PATH = '/assets/alarm_min_off.png'
ALARM_MAX_ON_PATH = '/assets/alarm_max_on.png'
ALARM_MAX_OFF_PATH = '/assets/alarm_max_off.png'
ALARM_UNSET_PATH = '/assets/alarm_unset.png'

# -------- PARAMETERS ---------
N_DECIMALS = 3
MIN_TIME_UPDATE_MS = 60  # minimum time that app can update
MAX_TIME_INTERVAL_MS = 5100


def get_desktop_dir():
    """
    Get the user's desktop directory
    :return: user's desktop as a string
    """

    return str(Path.home().joinpath("Desktop")) + "/"


def filter_digits(window, values, event, text_input_keys: list):
    """
    Filters out non-digit text inputs even if the user types letter, numbers or symbols
    :param window: window from gui where text is inputted and shown
    :param values: list of values in gui window
    :param text_input_keys: list with text-input keys
    :param event: event in gui window
    :return:
    """
    k_event = text_input_keys[text_input_keys.index(event)] if len(text_input_keys) > 1 else text_input_keys[0]
    values[k_event] = "".join(c for c in values[k_event] if c.isdigit())
    window[k_event].update(values[k_event])


def filter_numeric_characters(window, values, event, text_input_keys: list):
    """
    Filters out non-numeric text inputs so that even if the user types letters and numbers, only numbers, '.' and '-'
    are shown
    :param window: window from gui where text is inputted and shown
    :param values: list of values in gui window
    :param text_input_keys: list with text-input keys
    :param event: event in gui window
    """
    # assigns text input key where there is an event
    k_event = text_input_keys[text_input_keys.index(event)] if len(text_input_keys) > 1 else text_input_keys[0]
    # empty string where filtered out characters will be added
    filtered_chars = []
    # flag to signal if a '.' has already been typed in
    dot_found = False
    for char in values[k_event]:
        # adds if char is between 0-9
        if char.isdigit():
            filtered_chars.append(char)
        # adds '.' if it's the first one found
        elif char == '.' and not dot_found:
            filtered_chars.append(char)
            dot_found = True
        # adds '-' if it's in the first position
        elif char == '-' and len(filtered_chars) == 0:
            filtered_chars.append(char)

    values[k_event] = ''.join(filtered_chars)
    window[k_event].update(values[k_event])


def _check_if_key(key_input):
    """
    Private method that checks if the value passed is a valid key
    :param key_input:
    :return:
    """
    # Checks if value is a string
    if not isinstance(key_input, str):
        raise TypeError(f"Variable 'key_input' must be a string,\ngot {type(key_input).__name__} instead.")
    # Checks if the value passed has the correct key format
    key_format = r'^-\w+-$'  # defining pattern: '-<key>-'
    if not re.match(key_format, key_input):
        raise ValueError(f"Invalid key format for 'key_input': '{key_input}'.\nKeys must have '-<key>-'")


def check_if_valid_input(values, n_decimals, *args):
    """
    Checks if input value when entered is a valid number and isn't empty
    :param n_decimals: number of decimals desired
    :param values: list of values in gui window
    :param args: input key(s)
    :return: list of valid input(s) as floats with 3 decimals
    """
    # list where valid inputs will be stored
    valid_inputs = []
    for key_input in args:
        # checks if key input is valid
        _check_if_key(key_input)
        # checks if input value isn't empty
        if values[key_input] == "":
            raise ValueError("Values must be assigned")
        # checks if input is a valid number
        elif not is_number(values[key_input]):
            raise ValueError("Values must be a numeric value.")
        # converts input from string to float with 3 decimals and adds it to the valid input list
        valid_inputs += to_number_n_dec(n_decimals, values[key_input])
    return valid_inputs


def set_disabled(window, is_disabled: bool, *args):
    """
    Updates disabled parameter of an element
    :param window: gui window
    :param is_disabled: bool, True: if element should be disabled, False if not
    :param args: element key(s)
    :return:
    """
    for key_input in args:
        _check_if_key(key_input)
        window[key_input].update(disabled=is_disabled)


def set_visible(window, is_visible: bool, *args):
    """
    Updates visibility parameter of an element
    :param window: gui window
    :param is_visible: bool, True: if element should be visible, False if not
    :param args: element key(s)
    :return:
    """
    for key_input in args:
        _check_if_key(key_input)
        window[key_input].update(visible=is_visible)


def empty_inputs(window, *args):
    """
    Empties the input in a window
    :param window: gui window
    :param args: input key(s)
    :return:
    """
    for key_input in args:
        _check_if_key(key_input)
        window[key_input].update('')


def is_number(string):
    """
    Same as isnumeric but with floats also
    :param string: number input
    :return: True if it's a number, False if it isn't
    """
    if string[0] == '-':
        string = string[1:]

    return string.replace('.', '', 1).isdigit() or string.isnumeric()


def to_number_n_dec(n_decimals, *args):
    """
    Turns arguments to a float with 3 decimal points
    :param n_decimals: number of decimals desired
    :param args:
    :return:
    """
    if not isinstance(n_decimals, int):
        raise TypeError(f"Number of decimals must be integer,\ngot {type(n_decimals).__name__}")
    result = []
    for number in args:
        if n_decimals > 0:
            result.append(round(float(number), n_decimals))
        else:
            result.append(round(int(number), n_decimals))
    return result


def calculate_frequency(period):
    """
    Calculates frequency value, given period value
    :param period: period value
    :return: frequency value in the same time unit as period value
    """
    if not isinstance(period, (int, float)):
        raise TypeError(f"Expected a number (float or integer), got {type(period).__name__} instead")
    return 1 / period


def gui_toggle_behaviour(window):
    window['-TOGGLE-'].metadata = not window['-TOGGLE-'].metadata
    if window['-TOGGLE-'].metadata:
        set_disabled(window, True, '-V_INPUT-')
        window['-V_INPUT-'].update("")
        window['-V_TXT-'].update(text_color=sg.theme_button_color()[1])
        window['-TOGGLE_OFF_TXT-'].update(font=FONT_DEFAULT)
        window['-TOGGLE_ON_TXT-'].update(font=FONT_BOLD)
    else:
        set_disabled(window, False, '-V_INPUT-')
        window['-V_TXT-'].update(text_color=sg.theme_text_color())
        window['-TOGGLE_ON_TXT-'].update(font=FONT_DEFAULT)
        window['-TOGGLE_OFF_TXT-'].update(font=FONT_BOLD)

    window['-TOGGLE-'].update(image_filename=TOGGLE_ON_PATH if window['-TOGGLE-'].metadata else TOGGLE_OFF_PATH)


def gui_window_with_graph(title, layout, figSizeWidth, figSizeHeight, isModal):
    """
    Initializes a PySimpleGUI window with a matplotlib using a CANVAS with empty graph that can be updated later
    :param title: title of the window
    :param layout: layout designed for the window
    :param figSizeWidth: desired width of the graph
    :param figSizeHeight: desired height of the grap
    :param isModal: bool if window is modal
    :return: window, fig, figure_canvas_agg
    """
    # Create the PySimpleGUI window with the provided title and layout
    window = sg.Window(title, layout, finalize=True, element_justification='center', modal=isModal,
                       size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    # Create a new matplotlib Figure object with the provided size
    fig = matplotlib.figure.Figure(figsize=(figSizeWidth, figSizeHeight))
    # Adjust the position of the axes within the figure
    fig.subplots_adjust(top=0.8, bottom=0.25, left=0.2)  # Move the axes up by adjusting the top and bottom positions
    # Add a subplot (axes) to the figure and plot an empty line
    fig.add_subplot(111).plot([], [])
    # Create a FigureCanvasTkAgg object by associating the figure with the tkinter canvas element
    figure_canvas_agg = FigureCanvasTkAgg(fig, window['-CANVAS-'].TKCanvas)
    # Draw the initial empty plot on the canvas
    figure_canvas_agg.draw()
    # Pack the canvas widget into the window's layout
    figure_canvas_agg.get_tk_widget().pack()

    return window, fig, figure_canvas_agg


def get_axes_for_points(fig, data: list):
    """
    Creates axes for a graph made with data points
    :param fig:
    :param data: list of points
    :return: axes with xlabel, ylabel and a grid and x and y list of separated data
    """
    axes = fig.axes
    x = [i[0] for i in data]
    y = [i[1] for i in data]
    axes[0].clear()
    axes[0].set_xlabel("Voltage (V)")
    axes[0].set_ylabel("Temperature (ºC)")
    axes[0].grid()
    return axes, x, y


def pack_canvas(figure_canvas_agg):
    """
    Packs canvas for later use in graph
    :param figure_canvas_agg:
    :return:
    """
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack()


def draw_points(axes, x_points, y_points, marker, label=None):
    """
    If a user selects a points in table, it will be drawn in table
    :param axes:
    :param x_points: x point or list
    :param y_points: y point or list
    :param marker: desired shape and color for point/s
    :param label: name of label
    :return:
    """
    axes[0].plot(x_points, y_points, marker, label=label)


def sort_pair_list_by_x(data):
    """
    Sorts a list of pairs by x
    :param data: list of data points
    :return: list of pairs sorted
    """
    sorted_points = sorted(data, key=lambda p: p[0])
    return sorted_points


def get_sorted_nth_elements(data, n):
    """
    Extracts elements at any index n from the pairs
    :param data: list of pairs
    :param n: nth element [0] or [1]
    :return: list of nth elements
    """
    return [i[n] for i in sort_pair_list_by_x(data)]
