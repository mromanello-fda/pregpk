import warnings
import tokenize
import numpy as np
import pint
import re
from . import app_ureg


class ValueRange:
    def __init__(self, text):
        self.ureg = app_ureg

        self.unit = None
        self.average = None
        self.min = None
        self.max = None
        self.stdev = None
        self.sort_val = None

        self.raw_text = text

        self._process_text()

    def __repr__(self):
        print_dict = {"Average": self.average,
                      "Min": self.min,
                      "Max": self.max,
                      "Standard dev.": self.stdev,
                      "Units": self.unit}

        return f'{self.__class__.__name__}({", ".join([f"{key}: {val}" for key, val in print_dict.items() if val is not None])})'

    def __float__(self):
        if self.sort_val:
            return self.sort_val
        else:
            return np.nan

    def _process_text(self):

        self._build_regexes()
        self._parse_text(self.raw_text)
        self._assign_sort_val()

        return

    def _build_regexes(self):

        # Building blocks
        self._re_any_float = '-?(0|[1-9]\d*)(\.\d+)?'
        self._re_any_spaces = '[ \t]*'
        self._re_any_bracketed = '\(([^()]+)\)|\[([^][]+)\]'
        # self._re_any_unit_string = unit_utils.get_any_units_re()
        self._re_any_ineq_float = '[<>]' + self._re_any_float

        # Bracketed building blocks
        # self._re_brac_float = '[/[]' + self._re_any_spaces + self._re_any_float + self._re_any_spaces + '[\]]'
        # self._re_brac_units = '[/[]' + self._re_any_spaces + self._re_any_unit_string + self._re_any_spaces + '[\]]'
        # self._re_parenth_float = '[/(]' + self._re_any_spaces + self._re_any_float + self._re_any_spaces + '[\)]'
        # self._re_parenth_units = '[/(]' + self._re_any_spaces + self._re_any_unit_string + self._re_any_spaces + '[\)]'

        # Longer formats that might need to be recognized
        self._re_hyphen_range = self._re_any_float + '-' + self._re_any_float
        self._re_pm_range = self._re_any_float + self._re_any_spaces + '\u00B1' + self._re_any_spaces + self._re_any_float

    # def _is_unit_re(self, text):
    #     return re.match(f"^{self._re_any_unit_string}$", text) is not None

    def _is_unit(self, text):
        try:
            u = self.ureg.parse_units(text)
            if isinstance(u, pint.Unit) and not u.dimensionless:
                return True
        except (pint.UndefinedUnitError, ValueError, TypeError):
            return False
        except tokenize.TokenError:  # TODO: Also should not need; review later.
            return False

        return False

    def _is_value(self, text):
        return re.match(f"^{self._re_any_float}$", text) is not None

    def _is_hyphenated_range(self, text):
        return re.match(f"^{self._re_hyphen_range}$", text) is not None

    def _is_pm_range(self, text):
        return re.match(f"^{self._re_pm_range}$", text) is not None

    def _is_range(self, text):
        return self._is_hyphenated_range(text) or self._is_pm_range(text)

    def _split_string(self, text):

        text = re.sub(r'\s*\u00B1\s*', '\u00B1', text)  # Removes all types of spaces surrounding +/-
        text = re.sub(r'\s*-\s*', "-", text)  # Removes all types of spaces surrounding -

        # This will parse the string of text to a list of individual strings, each of which
        # most likely represent a range, value, or units (if formatted anything close to usual)
        split_text = [s for s in re.split(r'[ \[\]\(\)]', text) if s]

        return split_text

    def _parse_text(self, text):

        split_text = self._split_string(text)
        self._parse_split_text_list(split_text)

        return

    def _parse_split_text_list(self, split_text):

        unit = []
        value = []
        hyphen_range = []
        pm_range = []

        for t in split_text:
            matched = False
            if self._is_unit(t):
                unit.append(t)
                matched = True
            if self._is_value(t):
                value.append(t)
                matched = True
            if self._is_hyphenated_range(t):
                hyphen_range.append(t)
                matched = True
            if self._is_pm_range(t):
                pm_range.append(t)
                matched = True

            if not matched:
                raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. Substring {t} not "
                                 f"a recognizable format.")

        self._check_parsed_values_validity(unit, value, hyphen_range, pm_range)
        self._assign_parsed_values(unit, value, hyphen_range, pm_range)

        return

    def _check_parsed_values_validity(self, unit, value, hyphen_range, pm_range):
        if len(unit) > 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. {' ,'.join(unit)} all defined "
                             f"as the unit.")

        if len(value) > 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. {' ,'.join(value)} all defined "
                             f"as the value.")

        if len([hyphen_range+pm_range]) > 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. {' ,'.join([hyphen_range+pm_range])} "
                             f"all defined as the range.")
        if len(value+hyphen_range+pm_range) < 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. No value or range detected.")

        return

    def _assign_parsed_values(self, unit, value, hyphen_range, pm_range):

        try:
            self.unit = self.ureg.parse_units(unit[0])
        except IndexError:
            pass

        try:  # Should be able to convert to float, so no error handling. If there is a ValueError, there's a problem
            self.average = float(value[0])
        except IndexError:
            pass

        try:
            hr_str = hyphen_range[0]
            hr_1 = float(hr_str[:hr_str.index('-')])
            hr_2 = float(hr_str[hr_str.index('-')+1:])
            if hr_1 > hr_2:
                warnings.warn(f"Possible error when parsing hyphenated range {hr_str} to a minimum and maximum:\n"
                              f"first term ({hr_1}) larger than second ({hr_2}).")
            self.min = min([hr_1, hr_2])
            self.max = max([hr_1, hr_2])
        except IndexError:
            pass

        try:
            pm_str = pm_range[0]
            self.average = float(pm_str[:pm_str.index("\u00B1")])
            self.stdev = float(pm_str[pm_str.index("\u00B1")+1:])
        except IndexError:
            pass

        return

    def _assign_sort_val(self):

        if self.average is not None:
            self.sort_val = self.average
            return

        if self.min is not None and self.max is not None:
            self.sort_val = (float(self.min) + float(self.max)) / 2
            return

        return

    def unit_dict(self):

        return self.unit

    # __getstate__ is run before pickling. Pickling a pint.UnitRegistry() is not allowed because it has lambda functions
    # Thus, we remove the "ureg" attribute before serializing (pickling) it
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unit registry from the state to pickle
        del state['ureg']
        return state

    # __setstate__ is run when opening a pickled file. Since self.ureg() was removed during serialization,
    # we must restore it here, or else pickle.load("xx_ValueRange.pkl") will return a ValueRange instance without
    # the ureg attribute.
    def __setstate__(self, state):
        self.__dict__.update(state)
        # Restore the unit registry after unpickling
        self.ureg = app_ureg

    def __lt__(self, other):

        # Check if even sortable
        if self.sort_val is None:
            raise ValueError(f"Unable to compare {self.__class__.__name__} object to int/float when it does not contain average value "
                             "or range.")

        if isinstance(other, (float, int)):  # TODO: consider - is this a good choice? Should it just raise an error?
            return float(self.sort_val) < other

        if isinstance(other, ValueRange):
            return float(self.sort_val) * self.unit < float(other.sort_val) * other.unit

        raise TypeError("Can only compare a ValueRange object to either a float/int or another ValueRange object.")

    def __eq__(self, other):
        if self.sort_val is None:
            raise ValueError("Unable to compare ValueRange object to int/float when it does not contain average value "
                             "or range.")

        if isinstance(other, (float, int)):
            return float(self.sort_val) == other

        if isinstance(other, ValueRange):
            return float(self.sort_val) * self.unit == float(other.sort_val) * other.unit

        raise TypeError("Can only compare a ValueRange object to either a float/int or another ValueRange object.")

    def __gt__(self, other):

        # Check if even sortable
        if self.sort_val is None:
            raise ValueError("Unable to compare ValueRange object to int/float when it does not contain average value "
                             "or range.")

        if isinstance(other, (float, int)):
            return float(self.sort_val) > other

        if isinstance(other, ValueRange):
            return float(self.sort_val) * self.unit > float(other.sort_val) * other.unit

        raise TypeError("Can only compare a ValueRange object to either a float/int or another ValueRange object.")

    def __le__(self, other):

        # Check if even sortable
        if self.sort_val is None:
            raise ValueError("Unable to compare ValueRange object to int/float when it does not contain average value "
                             "or range.")

        if isinstance(other, (float, int)):
            return float(self.sort_val) <= other

        if isinstance(other, ValueRange):
            return float(self.sort_val) * self.unit <= float(other.sort_val) * other.unit

        raise TypeError("Can only compare a ValueRange object to either a float/int or another ValueRange object.")

    def __ge__(self, other):

        # Check if even sortable
        if self.sort_val is None:
            raise ValueError("Unable to compare ValueRange object to int/float when it does not contain average value "
                             "or range.")

        if isinstance(other, (float, int)):
            return float(self.sort_val) >= other

        if isinstance(other, ValueRange):
            return float(self.sort_val) * self.unit >= float(other.sort_val) * other.unit

        raise TypeError("Can only compare a ValueRange object to either a float/int or another ValueRange object.")


class GestAgeValueRange(ValueRange):
    # TODO: Maybe instead of re-writing this with a lot of logic for non-pregnant, postpartum, etc. you can create
    #  a "non-pregnant" or "postpartum" class that has a string representation of "Non-Pregnant", "Delivery", and
    #  "Postpartum", but a float value of -1, 40, and 41

    def __init__(self, text):
        self.has_non_pregnant = False
        self.has_delivery = False
        self.has_postpartum = False
        self.has_non_numeric = False

        super().__init__(text)

        if self.unit is None:  # Assign unit of weeks if parsed a numerical value and does not have units
            if any(ele is not None for ele in [self.average, self.max, self.min, self.stdev]):
                self.unit = self.ureg.week

    def _build_regexes(self):

        super()._build_regexes()

        self._re_non_pregnant = r"(?i)Non-Pregnant"
        self._re_delivery = r"(?i)Delivery"
        self._re_postpartum = r"(?i)Postpartum"

        self._re_any_non_numeric = "(?i)(non-pregnant|postpartum|delivery)"
        self._re_any_non_numeric_or_float = f"({self._re_any_non_numeric}|{self._re_any_float})"
        self._re_hyphen_or_float_non_numeric_range = f"{self._re_any_non_numeric_or_float}-{self._re_any_non_numeric_or_float}"

        return

    def __repr__(self):
        min_repr = "Non-Pregnant" if self.has_non_pregnant else self.min
        if self.has_postpartum:
            max_repr = "Postpartum"
        elif self.has_delivery:
            max_repr = "Delivery"
        else:
            max_repr = self.max

        print_dict = {"Average": self.average,
                      "Min": min_repr,
                      "Max": max_repr,
                      "Standard dev.": self.stdev,
                      "Units": self.unit}

        return f'{self.__class__.__name__}({", ".join([f"{key}: {val}" for key, val in print_dict.items() if val is not None])})'

    def _is_value(self, text):
        return re.match(f"^{self._re_any_non_numeric_or_float}$", text) is not None

    def _is_hyphenated_range(self, text):
        return re.match(f"^{self._re_hyphen_or_float_non_numeric_range}$", text) is not None

    def _is_non_numeric(self, text):
        return re.match(f"^{self._re_any_non_numeric}$", text) is not None

    def _parse_split_text_list(self, split_text):

        unit = []
        value = []
        hyphen_range = []
        pm_range = []

        for t in split_text:
            matched = False
            if self._is_unit(t):
                unit.append(t)
                matched = True
            if self._is_value(t):
                value.append(t)
                matched = True
            if self._is_hyphenated_range(t):
                hyphen_range.append(t)
                matched = True
            if self._is_pm_range(t):
                pm_range.append(t)
                matched = True

            if not matched:
                raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. Substring {t} not a "
                                 f"recognizable format.")

        self._check_parsed_values_validity(unit, value, hyphen_range, pm_range)
        self._assign_parsed_values(unit, value, hyphen_range, pm_range)

        return

    def _check_parsed_values_validity(self, unit, value, hyphen_range, pm_range):
        if len(unit) > 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. {' ,'.join(unit)} all defined "
                             f"as the unit.")

        if len(value) > 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. {' ,'.join(value)} all defined "
                             f"as the value.")

        if len([hyphen_range+pm_range]) > 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. {' ,'.join([hyphen_range+pm_range])} "
                             f"all defined as the range.")
        if len(value+hyphen_range+pm_range) < 1:
            raise ValueError(f"Unable to parse {self.raw_text} into a {self.__class__.__name__}. No value or range detected.")

        return

    def _assign_parsed_values(self, unit, value, hyphen_range, pm_range):

        try:
            self.unit = self.ureg.parse_units(unit[0])
        except IndexError:
            self.unit = self.ureg.week

        try:
            self.average = self._parse_value_or_non_numeric(value[0])
        except IndexError:  # "value" is an empty list
            pass

        try:
            hr_str = hyphen_range[0]

            range_hyphen_idx = [idx for idx, val in enumerate(hr_str) if
                                 val == "-" and hr_str[idx-3:idx+9].lower() != 'non-pregnant'][0]

            hr_1 = self._parse_value_or_non_numeric(hr_str[:range_hyphen_idx])
            hr_2 = self._parse_value_or_non_numeric(hr_str[range_hyphen_idx+1:])

            if float(hr_1) > float(hr_2):
                warnings.warn(f"Possible error when parsing text {self.raw_text}. Substring {hr_str} identified as "
                              f"hyphenated range but \n"
                              f"first term ({hr_1}) larger than second ({hr_2}).")
            self.min = min([hr_1, hr_2])
            self.max = max([hr_1, hr_2])
        except IndexError:
            pass

        try:
            pm_str = pm_range[0]
            self.average = float(pm_str[:pm_str.index("\u00B1")])
            self.stdev = float(pm_str[pm_str.index("\u00B1")+1:])
        except IndexError:
            pass

        return

    def _parse_value_or_non_numeric(self, text):

        try:
            return float(text)  # If just a float value
        except ValueError as ve:  # If not convertible to float; likely a known non-numeric (eg. "Delivery")
            if self._is_non_numeric(text):
                return self._non_numeric_string_to_obj(text)
            else:
                raise ve

    def _non_numeric_string_to_obj(self, text):

        if re.match(f"^{self._re_non_pregnant}$", text) is not None:
            return NonPregnant()
        if re.match(f"^{self._re_delivery}$", text) is not None:
            return Delivery()
        if re.match(f"^{self._re_postpartum}$", text) is not None:
            return Postpartum()

        raise ValueError(f"String {text} not interpretable/convertible to a non-numeric object "
                         f"(NonPregnant, Delivery, Postpartum)")


class NonNumericGestAge:
    def __init__(self):
        return


class NonPregnant(NonNumericGestAge):
    def __repr__(self):
        return "Non-Pregnant"
    def __float__(self):
        return float(-1)
    def __add__(self, other):
        return self.__float__() + other
    def __sub__(self, other):
        return self.__float__() - other
    def __lt__(self, other):
        return self.__float__() < float(other)
    def __gt__(self, other):
        return self.__float__() > float(other)


class Postpartum(NonNumericGestAge):
    def __repr__(self):
        return "Postpartum"
    def __float__(self):
        return float(41)
    def __add__(self, other):
        return self.__float__() + other
    def __sub__(self, other):
        return self.__float__() - other
    def __lt__(self, other):
        return self.__float__() < float(other)
    def __gt__(self, other):
        return self.__float__() > float(other)


class Delivery(NonNumericGestAge):
    def __repr__(self):
        return "Delivery"
    def __float__(self):
        return float(40)
    def __add__(self, other):
        return self.__float__() + other
    def __sub__(self, other):
        return self.__float__() - other
    def __lt__(self, other):
        return self.__float__() < float(other)
    def __gt__(self, other):
        return self.__float__() > float(other)
