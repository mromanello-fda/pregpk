
def input_advanced_gpt_test_params():

    print("Advanced settings (Just press ENTER for default option in any setting):")

    print("Set testing dataset parameters:")
    bc = input("\tBalance the classes [0:no, 1:yes (default)]?\t") or "1"
    try:
        bc = bool(int(bc))
    except:
        print('\tInput invalid. Defaulting to YES.')
        bc = True

    n = input("\tTotal number of articles in dataset [default = 40]:\t") or "40"
    try:
        n = int(n)
    except:
        print('\tInput invalid. Defaulting to 40.')
        n = 40

    print("Set GPT parameters:")
    vers = input('\tGPT Version ["gpt-4", "gpt-4-0125-preview", or "gpt-3.5-turbo-0125" (default)]:\t') or "gpt-3.5-turbo-0125"
    if vers not in ["gpt-4", "gpt-4-0125-preview", "gpt-3.5-turbo-0125"]:
        print('\tInput invalid. Defaulting to "gpt-3.5-turbo-0125".')
        vers = "gpt-3.5-turbo-0125"

    temp = input('\tTemperature [value from 0 to 2, default 0.1]:\t') or "0.1"
    try:
        temp = float(temp)
        if temp < 0 or temp > 2:
            print('\tInput invalid. Defaulting to 0.1.')
            temp = 0.1
    except:
        print('\tInput invalid. Defaulting to 0.1.')
        temp = 0.1

    max_tokens = input("\tMax tokens [default = 50]:\t") or "50"
    try:
        max_tokens = int(max_tokens)
    except:
        print('\tInput invalid. Defaulting to 50.')
        max_tokens = 50
    print('')

    test_set_params = {"balance_classes": bc,
                       "n": n,}
    gpt_params = {"version": vers,
                  "temperature": temp,
                  "max_tokens": max_tokens}

    return test_set_params, gpt_params
