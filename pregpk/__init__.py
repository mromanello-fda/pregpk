import json
import pint
import importlib.resources as pkg_resources
from . import assets
from .assets import standard_values

app_ureg = pint.UnitRegistry()

with pkg_resources.path(assets, "pregpk_pint_system.txt") as app_ureg_file:
    app_ureg.load_definitions(app_ureg_file)
app_ureg.default_system = "pregpk"

pint.set_application_registry(app_ureg)

with pkg_resources.path(standard_values, "country_info.json") as country_info_path:
    with open(country_info_path, "r") as country_info_file:
        country_dict = json.load(country_info_file)

with pkg_resources.path(standard_values, "us_states_info.json") as us_state_info_path:
    with open(us_state_info_path, "r") as us_state_info_file:
        us_state_dict = json.load(us_state_info_file)

# __all__ = ["app_ureg", "ValueRange"]
# TODO: edit this __all__ variable; important for publishing.
