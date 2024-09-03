def get_any_units_re():

    # Plurals automatically included because of "s" for second; however must look out in future if just converting
    # automatically to units that "s" is usually seconds, but may sometimes be plurality

    units = ['pg', 'ng', '\u03BCg', '\u00B5g', 'mg', 'g', 'kg',  # mass
             'lb',  # weight
             'ms', 's', 'sec', 'min', 'hr', 'hour', 'day', 'week', 'month',  # time
             'pm', 'nm', '\u03BCm', '\u00B5m', 'mm', 'cm', 'm', 'km',  # SI length
             'in', 'inch', 'inches', 'ft', 'foot', 'feet',  # Imperial length
             'nL', '\u03BCL', '\u00B5L', 'mL', 'L',  # Volume
             'pM', 'nM', '\u03BCM', '\u00B5M', 'mM', 'M',  # Concentration
             'pmol', 'nmol', '\u03BCmol', '\u00B5mol', 'mmol', 'mol',  # Amount
             'IU', 'IUnits',  # Pharm units
             '%',  # Standard stuff
             ]

    positive_lookahead = f"(?=.*({'|'.join(units)}))"  # Ensures that string HAS to include one unit (or else just a number or "/" would return as true)
    symbols = ['/', '\^', '\*']
    other_additions = ['\s']  # Spaces

    return f"{positive_lookahead}(\d+|{'|'.join(units + symbols + other_additions)})+"
