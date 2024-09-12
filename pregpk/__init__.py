import pint
import importlib.resources as pkg_resources
from . import assets

app_ureg = pint.UnitRegistry()

with pkg_resources.path(assets, "pregpk_pint_system.txt") as app_ureg_file:
    app_ureg.load_definitions(app_ureg_file)
app_ureg.default_system = "pregpk"

__all__ = ["app_ureg", "ValueRange"]
