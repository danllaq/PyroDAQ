from abc import ABC, abstractmethod
import src.guiTools as gt
import numpy as np
from scipy.optimize import curve_fit
import warnings


def linear_func(x, m, n):
    """
    Linear function method
    :param x: variable
    :param m: slope
    :param n: y interception
    :return: linear function
    """
    return m * x + n


def non_linear_func(x, a, b, c):
    """
    Non-linear function method
    :param x: variable
    :param a: grade 2 param
    :param b: grade 1 param
    :param c: constant
    :return: non-linear function
    """
    return a * x ** 2 + b * x + c


class Calibration(ABC):
    """
    Calibration parent class, everything related to the calibration when it's being set goes here. Once
    It's set, it goes to the niDAQ class object
    """

    def __init__(self, expression_type):
        """
        Initiates calibration object given the expression type
        :param expression_type: string, types: 'LINEAR_EQUATION', 'NON_LINEAR_EQUATION'
        """
        self.expression_type = expression_type  # types: 'LINEAR_EQUATION', 'NON_LINEAR_EQUATION'
        self.parameters = {}  # dictionary where parameters are stored {'coefficient_g2', 'coefficient_g1', 'constant'}
        self.data = []
        self.interpolation_points = []  # only used for interpolation

    def __len__(self):
        """
        When len(object) is used, returns length of data list
        :return: number of points in data list
        """
        return len(self.data)

    def __getitem__(self, index):
        """
        When object[index] is used, accesses data list to retrieve value
        :param index: index to access
        :return: pair with [voltage, temperature]
        """
        return self.data[index]

    def __setitem__(self, index, voltage_temperature: list):
        """
        When object[index] is used, accesses data list to assign value
        :param index: index to access
        :return:
        """
        check_all_floats(voltage_temperature[0], voltage_temperature[1])
        self.data[index] = voltage_temperature

    def __delitem__(self, index):
        """
        When using del object[index], deletes item in data list
        :param index: index to access
        :return:
        """
        del self.data[index]

    def set_chosen_points(self, chosen_points: list):
        """
        Assign the chosen points pair selected by the user
        :param chosen_points: two pairs in a list
        :return:
        """
        self.interpolation_points = chosen_points

    def set_data_list(self, data):
        """
        Takes a list (data) containing pairs of data points and assigns it to a list in an object.
        :param data: list of data pair points
        :return:
        """
        self.data = data

    def get_parameter(self, parameter_name):
        """
        Accesses equation parameter dictionary and returns desired value
        :param parameter_name: name of the equation parameter ['coefficient_g2', 'coefficient_g1', 'constant']
        :return: equation parameter value
        """
        return self.parameters.get(parameter_name)

    def get_data(self):
        """
        Returns the data points stored by the user
        :return: list of pairs
        """
        return self.data

    def update_parameters(self, parameters_dict):
        """
        Takes a dictionary (parameters_dict) containing the parameter names and their corresponding values.
        The update method of the parameters dictionary is then used to update the parameter values in another object.
        :param parameters_dict: dictionary where equation parameter values are stored
        :return:
        """
        self.parameters.update(parameters_dict)

    def add_voltage(self, voltage):
        """
        Given a voltage value, will add to the data list
        :param voltage: Voltage value, float
        :return:
        """
        [voltage] = gt.to_number_n_dec(gt.N_DECIMALS, voltage)
        temperature = self.calculate_temperature(voltage)
        self.data.append([voltage, temperature])

    def add_data(self, voltage_temperature: list):
        """
        Given a voltage and temperature pair, adds to de data
        :param voltage_temperature: voltage and temperature pair
        :return:
        """
        self.data.append(voltage_temperature)

    def clear_data(self):
        """
        Clears table list
        :return:
        """
        self.data.clear()

    def update_data(self):
        """
        Updates data points
        :return:
        """
        for i, (voltage, temperature) in enumerate(self.data):
            new_temperature = self.calculate_temperature(voltage)
            self[i] = [voltage, new_temperature]

    def sort_x(self):
        """
        Sorts data points by x
        :return: list of x values
        """
        return gt.get_sorted_nth_elements(self.data, n=0)

    def sort_y(self):
        """
        Sorts data points by x
        :return: list of y values
        """
        return gt.get_sorted_nth_elements(self.data, n=1)

    def is_linear(self):
        """
        Checks if object is linear
        :return: boolean, true if it is
        """
        return self.expression_type == 'LINEAR_EQUATION'

    def is_nonlinear(self):
        """
        Checks if object is non-linear
        :return: boolean, True if it is
        """
        return self.expression_type == 'NON_LINEAR_EQUATION'

    def is_type(self, expression_type):
        """
        Checks if the object has the same expression type
        :param expression_type: LINEAR_EQUATION or NON_LINEAR_EQUATION
        :return: True if they are, false if it isn't
        """
        return self.expression_type == expression_type

    def data_exists(self, data_point):
        """
        Checks if voltage is already stored in data
        :param data_point:pair [voltage, temperature]
        :return: True if voltage is already stored
        """
        return any(voltage == data_point[0] for voltage, temperature in self.data)

    def has_enough_points(self):
        """
        Checks if there are at least 2 points to calculate a linear expression, or at least 3 for a nonlinear
        :return:
        """
        return (len(self) > 1 and self.is_linear()) or (len(self) > 2 and self.is_nonlinear())

    def to_linear_calibration(self, m=0, n=0):
        """
        Converts a NonLinearCalibration object to a LinearCalibration one, updating parameters and passing data
        :param n:
        :param m:
        :return: linear_cal, LinearCalibration object with relevant information
        """
        if self.expression_type == "NON_LINEAR_EQUATION":
            # creates LinearCalibration object
            linear_cal = LinearCalibration()
            # converts to floats with 3 decimal points
            m, n = gt.to_number_n_dec(gt.N_DECIMALS, m, n)
            # assigns parameters to new object
            linear_cal.update_parameters(parameters_dictionary(m, n))
            # assigns data list to new object
            linear_cal.set_data_list(self.data)
            return linear_cal
        else:
            raise ValueError("Cannot convert to LinearCalibration. Current equation type is linear.")

    def to_nonlinear_calibration(self, a=0, b=0, c=0):
        """
        Converts a LinearCalibration object to a NonLinearCalibration one, updating parameters and passing data
        :param c:
        :param b:
        :param a:
        :return: non_linear_cal, NonLinearCalibration object with relevant information
        """
        if self.expression_type == "LINEAR_EQUATION":
            # creates NonLinearCalibration object
            non_linear_cal = NonLinearCalibration()
            # converts to floats with 3 decimal points
            a, b, c = gt.to_number_n_dec(gt.N_DECIMALS, a, b, c)
            # assigns parameters to new object
            non_linear_cal.update_parameters(parameters_dictionary(a, b, c))
            # assigns data list to new object
            non_linear_cal.set_data_list(self.data)
            return non_linear_cal
        else:
            raise ValueError("Cannot convert to NonLinearCalibration. Current equation type is not linear.")

    def draw_expression(self, axes, known_expression):
        """
        Draws expression plot
        :param axes: axes where the figure is
        :param known_expression: calibration expression
        :return:
        """
        if known_expression:
            # Generate points for the plot
            if len(self) > 0:
                x_plot = np.linspace(self.sort_x()[0], self.sort_x()[-1], 100)
            else:
                x_plot = np.linspace(0, 10, 100)

            self.plot_expression(axes, known_expression, x_plot)
        else:
            if self.has_enough_points():
                self.plot_expression(axes, known_expression)

    def update_figure(self, fig, figure_canvas_agg, known_expression, is_point_selected=False, x_sel_point=None,
                      y_sel_point=None):
        """
        Updates and draws the plot
        :param fig: calibration plot
        :param figure_canvas_agg: canvas for calibration plot
        :param known_expression: boolean, indicates if the figure is being drawn with a known expression input by user
        :param is_point_selected: boolean if user has selected a point from table
        :param x_sel_point: x for selected point
        :param y_sel_point: y for selected point
        :return:
        """
        axes, x, y = gt.get_axes_for_points(fig, self.data)
        self.draw_expression(axes, known_expression)
        gt.draw_points(axes, x, y, 'bo', "Data Points")
        if is_point_selected:
            gt.draw_points(axes, x_sel_point, y_sel_point, 'ro')
        axes[0].legend()
        gt.pack_canvas(figure_canvas_agg)

    def change_in_data(self, win, fig, figure_canvas_agg, known_expression):
        """
        Updates window when there is a change in the data
        :param win: pysimplegui window
        :param fig: calibration plot
        :param figure_canvas_agg: canvas for the calibration plot
        :param known_expression: calibration expression
        :return:
        """
        win['-TABLE-'].update(values=self.data)
        if not known_expression:
            win['-N_SAMPLES-'].update(len(self))
        # if a point was deleted that was used for interpolation, the interpolation data clears
        if self.is_interpolation_points_in_data():
            self.interpolation_points.clear()
        self.update_figure(fig, figure_canvas_agg, known_expression)

    @abstractmethod
    def calculate_temperature(self, voltage: float):
        """
        Abstract method, given a voltage value it will be overriden by the appropriate subclass method that
        will calculate the temperature
        :param voltage: Voltage value, float
        :return:
        """
        pass

    def plot_expression(self, axes, known_expression, x_plot=None):
        """
        Abstract method, given an x_plot and axes it will be overriden by the appropriate subclass method that will
        plot the expression
        :param known_expression:
        :param x_plot: list of x values for the plot to reference
        :param axes: axes where the graph will be plotted on
        :return:
        """
        pass

    def is_interpolation_points_in_data(self):
        """
        Checks if the set interpolation points are in the data
        :return: boolean, True if they are
        """
        return not all(pair in self.data for pair in self.interpolation_points)


def check_all_floats(*args):
    """
    Given a list of values, checks if they all are float. If any isn't raises an error.
    Used when values are inputted by user.
    :param args: equation parameters
    :return:
    """
    for arg in args:
        if not isinstance(arg, float):
            raise ValueError(f"Invalid value: '{arg}' is not float. Type: {type(arg).__name__}")


def get_sign(number):
    """
    Return '+' if number is positive
    :param number:
    :return:
    """
    return ' ' if number < 0 else ' + '


def parameters_dictionary(*args):
    """
    Given the expression parameters, creates a dictionary format in order to save to the object
    :param args: calibration parameters, 2 for linear, 3 for non-linear
    :return: dictionary with the format set by the programmer
    """
    if len(args) == 3:
        return {'coefficient_g2': args[0], 'coefficient_g1': args[1], 'constant': args[2]}
    elif len(args) == 2:
        return {'coefficient_g2': None, 'coefficient_g1': args[0], 'constant': args[1]}
    else:
        raise ValueError(f"There must be 2 or 3 parameters, {len(args)} were provided")


class LinearCalibration(Calibration):
    """
    Child class of calibration for the linear expression, here everything related to linear calibration
    is managed and can convert to non-linear class if needed
    """
    def __init__(self, calculation_method=""):
        """
        Creates a child class of Calibration that if assigned has a type of calculation method
        :param calculation_method: methods: ['LEAST_SQUARES', 'LINEAR_INTERPOLATION']
        """
        super().__init__("LINEAR_EQUATION")
        self.calculation_method = calculation_method

    def __repr__(self):
        """
        String representation method
        :return: calibration equation in string form
        """
        return f"y = {self.get_parameter('coefficient_g1'):.3f}x{get_sign(self.get_parameter('constant'))}" \
               f"{self.get_parameter('constant'):.3f}"

    def update_method(self, calculation_method):
        """
        Updates calculation method
        :param calculation_method: methods: ['LEAST_SQUARES', 'LINEAR_INTERPOLATION']
        :return:
        """
        self.calculation_method = calculation_method

    def set_parameters(self, m, n):
        """
        Sets equation parameters
        :param m: grade 1 coefficient value in a linear equation
        :param n: constant coefficient value in a linear equation
        :return:
        """
        m, n = gt.to_number_n_dec(gt.N_DECIMALS, m, n)
        self.update_parameters(parameters_dictionary(m, n))

    def calculate_expression(self, point_1: list = None, point_2: list = None):
        """
        Given at least 2 point, calculates the coefficients for a linear expression
        :param point_1: first point
        :param point_2: second point
        :return:
        """
        match self.calculation_method:
            case 'LEAST_SQUARES':
                coefficients = np.polyfit(self.sort_x(), self.sort_y(), deg=1)
            case 'LINEAR_INTERPOLATION':
                coefficients = np.polyfit([point_1[0], point_2[0]], [point_1[1], point_2[1]], deg=1)
            case _:
                raise ValueError('Calibration calculation method not accepted')
        self.set_parameters(coefficients[0], coefficients[1])

    def calculate_temperature(self, voltage: float):
        """
        Calculates the temperature with calibration equation rounded to 3 decimal points.
        :param voltage: Voltage value
        :return: Temperature value rounded to 3 decimal points
        """
        check_all_floats(voltage)
        return round(linear_func(voltage, self.get_parameter('coefficient_g1'), self.get_parameter('constant')), 3)

    def plot_expression(self, axes, known_expression, x_plot=None):
        """
        Plots linear calibration graph on axes
        :param known_expression:
        :param x_plot:
        :param axes:
        :return:
        """
        x_list = x_plot if known_expression else self.sort_x()
        axes[0].plot(x_list, np.polyval([self.get_parameter('coefficient_g1'), self.get_parameter('constant')],
                                        x_list), 'y-', label='Linear Regression')


class NonLinearCalibration(Calibration):
    """
    Child class of calibration for the non-linear expression, here everything related to linear calibration
    is managed and can convert to linear class if needed
    """
    def __init__(self):
        """
        Initiates object with its type
        """
        super().__init__("NON_LINEAR_EQUATION")

    def __repr__(self):
        """
        String representation method
        :return: calibration equation in string form
        """
        return f"y = {self.get_parameter('coefficient_g2'):.3f}x\u00B2" \
               f"{get_sign(self.get_parameter('coefficient_g1'))}" \
               f"{self.get_parameter('coefficient_g1'):.3f}x" \
               f"{get_sign(self.get_parameter('constant'))}" \
               f"{self.get_parameter('constant'):.3f}"

    def set_parameters(self, a: float, b: float, c: float):
        """
        Sets equation parameters
        :param a: grade 2 coefficient value in a non linear equation
        :param b: grade 1 coefficient value in a non linear equation
        :param c: constant coefficient value in a non linear equation
        :return:
        """
        check_all_floats(a, b, c)
        self.update_parameters(parameters_dictionary(a, b, c))

    def calculate_expression(self):
        """
        Calculated non-linear coefficient for the expression
        :return:
        """
        x_array = np.array(self.sort_x())
        y_array = np.array(self.sort_y())

        popt, _ = curve_fit(f=non_linear_func, xdata=x_array, ydata=y_array)

        a, b, c = popt
        self.set_parameters(a, b, c)

    def calculate_temperature(self, voltage: float):
        """
        Calculates the temperature with calibration equation rounded to 3 decimal points.
        :param voltage: Voltage value
        :return: Temperature value rounded to 3 decimal points
        """
        check_all_floats(voltage)
        return round(
            non_linear_func(voltage, self.get_parameter('coefficient_g2'), self.get_parameter('coefficient_g1'),
                            self.get_parameter('constant')), 3)

    def plot_expression(self, axes, known_expression, x_plot=None):
        """
        Plots nonlinear calibration graph on axes
        :param known_expression: calibration expression
        :param x_plot: list of x values if there's an expression
        :param axes: plot information
        :return:
        """
        x_list = x_plot if known_expression else np.linspace(self.sort_x()[0], self.sort_x()[-1], 100)
        y_plot = non_linear_func(x_list, self.get_parameter('coefficient_g2'), self.get_parameter('coefficient_g1'),
                                 self.get_parameter('constant'))
        axes[0].plot(x_list, y_plot, 'y-', label='Fitted Curve')
