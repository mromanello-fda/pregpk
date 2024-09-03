import os
import tiktoken
import warnings
from tqdm import tqdm
from openai import OpenAI
from pregpk import gen_utils


def num_tokens_from_string(string: str, gpt_model: str="gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(gpt_model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_list(obj, gpt_model:str):
    # TODO: maybe add functionality for nested lists through recursion
    return [num_tokens_from_string(i, gpt_model) for i in obj]


def cost_per_token(gpt_version:str, output:bool=False) -> float:

    if gpt_version == 'gpt-4':
        if output:
            return 60./1e6
        else:
            return 30./1e6

    if gpt_version == 'gpt-4-0125-preview' or gpt_version == 'gpt-4-1106-preview':
        if output:
            return 30./1e6
        else:
            return 10./1e6

    if gpt_version == 'gpt-3.5-turbo-0125':
        if output:
            return 1.5/1e6
        else:
            return 0.5/1e6

    return float('inf')


def run_gpt_study(prompts, chatgpt_api_key, gpt_params=None, class_key=None, class_error_val=-1):
    """
    prompts: list of inputs for OpenAI's "prompt" field. Inputs themselves must be dicts or list of dicts
    chatgpt_api_key: string with ChatGPT API key
    gpt_params: dictionary with any ChatGPT parameters to change from default values
    (GPT-3.5, temperature=0.1, max_tokens=50)
    class_key: dict. If telling GPT to start message with a set of characters to define classifications, dict
    defining key for these classes (eg. '0': False, '1': True, '2': 'Maybe').
    class_error_val: any, returned class for when first character is not found in keys to class_key
    """

    # Set default values for hyperparameters if not given
    gpt_params_def = {"version": "gpt-3.5-turbo-0125",
                      "temperature": 0.1,
                      "max_tokens": 50,}
    if gpt_params is None:
        gpt_params = {}
    gpt_params = gen_utils.set_default_dict(gpt_params, gpt_params_def)

    # Check whether keys are allowed (can't share anything that .startswith() would return true for more than one key)
    if class_key is not None:
        keys = list(class_key.keys())
        for ik1, key1 in enumerate(keys):
            for ik2, key2 in enumerate(keys):
                if ik1 != ik2 and class_key is not None:
                    if key1.startswith(key2) or key2.startswith(key1):
                        warnings.warn(f'Keys "{key1}" and "{key2}" are not allowed as keys cannot be '
                                      f'prefixes of one another. Class conversion to "gpt_pred" will be skipped.')
                        class_key = None

    results = []
    client = OpenAI(api_key=chatgpt_api_key)
    for prompt in tqdm(prompts):
        completion = client.chat.completions.create(
            model=gpt_params["version"],
            temperature=gpt_params["temperature"],
            max_tokens=gpt_params["max_tokens"],
            messages=prompt,
        )

        result = {}
        ret = completion.choices[0].message.content

        if class_key is not None:
            for key, val in class_key.items():
                if ret.startswith(key):
                    result["gpt_pred"] = val
                    break
            result.setdefault("gpt_pred", class_error_val)

        result["gpt_response"] = ret  # Adding last just to maintain cleaner order in json if created

        results.append(result)
    return results

