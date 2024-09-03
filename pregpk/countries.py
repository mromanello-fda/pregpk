import os
import json
import re
import requests
import warnings


class CountryParser:

    def __init__(self, country_json_path="standard_values/country_info.json",
                 us_state_json_path="standard_values/us_states_info.json"):
        self.country_json_path = country_json_path
        self.country_dict = self.get_country_dict()

        self.us_state_json_path = us_state_json_path
        self.us_state_dict = self.get_us_state_dict()
        # Define REs
        self.define_res()

    def get_country_dict(self):
        with open(self.country_json_path, "r") as ctr_file:
            countries = json.load(ctr_file)

        return countries

    def get_us_state_dict(self):
        with open(self.us_state_json_path, "r") as st_file:
            states = json.load(st_file)

        return states

    def define_res(self):

        all_ctr_names = []
        for ctr in self.country_dict.values():
            all_ctr_names.extend(ctr["names"])
        self.re_any_country_name = f"\s({'|'.join(all_ctr_names)})[\s,.;]"

        all_alpha_3s = []
        for ctr in self.country_dict.values():
            all_alpha_3s.append(ctr["alpha_3"])
        self.re_any_alpha_3 = f"\s({'|'.join(all_alpha_3s)})[\s,.;]"

        all_alpha_2s = []
        for ctr in self.country_dict.values():
            all_alpha_2s.append(ctr["alpha_2"])
        self.re_any_alpha_2 = f"\s({'|'.join(all_alpha_2s)})[\s,.;]"

        all_us_state_names = []
        for st in self.us_state_dict.keys():
            all_us_state_names.append(st)
        self.re_any_us_state_name = f"\s({'|'.join(all_us_state_names)})[\s,.;]"

        all_us_state_abbr = []
        for st_abbr in self.us_state_dict.values():
            all_us_state_abbr.append(st_abbr)
        self.re_any_us_state_abbr = f"\s({'|'.join(all_us_state_abbr)})[\s,.;]"

        return

    def country_from_name(self, name):
        for i_ctr, i_val in self.country_dict.items():
            if name in i_val["names"]:
                return i_ctr

        return None

    def country_from_alpha_3(self, a3):
        for i_ctr, i_val in self.country_dict.items():
            if a3 == i_val["alpha_3"]:
                return i_ctr

        return None

    def country_from_alpha_2(self, a2):
        for i_ctr, i_val in self.country_dict.items():
            if a2 == i_val["alpha_2"]:
                return i_ctr

        return None

    def countries_from_affiliation(self, aff):

        ctrs = []

        # Look for country names
        ctr_name_match = re.findall(self.re_any_country_name, aff.lower())
        ctrs.extend([self.country_from_name(i) for i in ctr_name_match])
        if ctrs:  # If identified using country name, stop here
            return ctrs

        # Look for 3-letter country abbreviations
        ctr_alpha_3_match = re.findall(self.re_any_alpha_3, aff)
        ctrs.extend([self.country_from_alpha_3(i) for i in ctr_alpha_3_match])
        if ctrs:
            return ctrs

        # Look for state name
        us_state_name_match = re.findall(self.re_any_us_state_name, aff.lower())
        if us_state_name_match:
            ctrs.append("united states")
        if ctrs:
            return ctrs

        # Look for state abbreviation
        us_state_abbr_match = re.findall(self.re_any_us_state_abbr, aff)
        if us_state_abbr_match:
            ctrs.append("united states")
        if ctrs:
            return ctrs

        # Look for 2-letter country abbreviations:
        # ctr_alpha_2_match = re.findall(self.re_any_alpha_2, aff)
        # ctrs.extend([self.country_from_alpha_2(i) for i in ctr_alpha_2_match])
        # if ctrs:
        #     # Only for testing when it is used; turn off for production
        #     warnings.warn(f"Alpha 2 country designation: {aff} -> {ctrs}")
        #     return ctrs

        # Having tested this and gone through every time it results in a country being selected, it only really works
        # for the UK, which doesn't even use their ISO code (GB). I have changed the alpha_2 and alpha_3 codes in the
        # country_info.json file to more accurately reflect what we see in literature ("UK" or "U.K" instead of "GB" or
        # "GBR") in case we want to actually search for every alpha_2 in the future. However, for now, I think it's
        # better just to catch cases of "UK" and "U.K" specifically and disregard the rest.
        # Look for "UK" or "U.K":
        uk_match = re.findall("\s(UK|U.K)[\s.,;]", aff)
        if uk_match:
            ctrs.append("united kingdom")
        if ctrs:
            return ctrs

        # Remove duplicates, preserve order
        ctrs = list(dict.fromkeys(ctrs).keys())

        return ctrs


def capitalize_name(name):
    split_name = name.split(' ')
    cap_name = []
    for i_split in split_name:
        if i_split == "of" or i_split == "and":
            cap_name.append(i_split)
        else:
            cap_name.append(i_split[0].upper() + i_split[1:])

    return ' '.join(cap_name)
