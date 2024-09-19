import pint
import importlib.resources as pkg_resources
from . import assets

app_ureg = pint.UnitRegistry()

with pkg_resources.path(assets, "pregpk_pint_system.txt") as app_ureg_file:
    app_ureg.load_definitions(app_ureg_file)
app_ureg.default_system = "pregpk"

pint.set_application_registry(app_ureg)

# __all__ = ["app_ureg", "ValueRange"]
# TODO: edit this __all__ variable; important for publishing.
