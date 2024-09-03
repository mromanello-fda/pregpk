import os
import json
import random
import numpy as np
import sklearn.metrics


def study_confusion_matrix(results:dict):

    y_true = [i['has_pk_data'] for i in results["results"] if i['gpt_pred'] != -1]  # Remove errors
    y_pred = [i['gpt_pred'] for i in results['results'] if i['gpt_pred'] != -1]

    return np.flip(sklearn.metrics.confusion_matrix(y_true, y_pred), axis=(0, 1))


def conf_mat_string(cm):
    s = list(str(cm))  # Start just with the CM
    s = list('  Pred\n') + s  # Add "predicted" label

    shift1 = len('Actual ')
    s2 = [" "]*shift1
    for c in s:  # If newline, change with newline plus shift to account for "Actual "
        s2.append(c)
        if c == '\n':
            s2 += list(f'{" "*shift1}')
    s = s2

    s[s.index('[')-shift1:s.index('[')] = list('Actual ')  # Add "Actual "
    return "".join(s)


def study_summary(results:dict) -> str:

    n_disp = results['n_articles']
    n_errors_disp = len([i for i in results['results'] if i['gpt_pred'] == -1])
    prompt_disp = results['prompt_file']

    dataset_name = results['dataset']
    dataset_disp = dataset_name
    sec_key = {'t': "Title", 'a': 'Abstract', 'f': 'Full Text'}
    section_disp = ', '.join([sec_key.get(init, '') for init in dataset_name[dataset_name.index("_")+1:dataset_name.index(".")]])

    cm = study_confusion_matrix(results)
    disp_cm = conf_mat_string(cm)
    disp_cm = disp_cm.replace('\n', f'\n{" " * 20}')

    old_np_settings = np.seterr(all='ignore')
    np.seterr(invalid='ignore')
    prec = cm[0, 0] / (cm[0, 0] + cm[1, 0])
    rec = cm[0, 0] / (cm[0, 0] + cm[0, 1])
    f1 = cm[0, 0] / (cm[0, 0] + 0.5 * (cm[1, 0] + cm[0, 1]))
    np.seterr(**old_np_settings)

    summary = f"{'Dataset:':<20}{dataset_disp}\n" \
              f"{'Sections used:':<20}{section_disp}\n" \
              f"{'n/errors:':<20}{n_disp}/{n_errors_disp}\n" \
              f"{'GPT Version:':<20}{results['gpt_params']['version']}\n" \
              f"{'Prompt:':<20}{prompt_disp}\n" \
              f"{'Cost:':<20}${results['estimated_cost']:.3f}\n" \
              f"{'Metrics:':<20}prec: {prec:.3f}\n" \
              f"{' ' * 20}rec:  {rec:.3f}\n" \
              f"{' ' * 20}F1:   {f1:.3f}\n" \
              f"{'Conf. mat.:':<20}{disp_cm}"

    return summary


def all_study_summaries(results_directory: str="results"):

    studies = [i for i in os.listdir(results_directory) if (i.endswith('.json') and i[:-5].isdigit())]  # Only #.json files
    studies = sorted([(int(i[:-5]), i) for i in studies])  # Sort by integer, not alphabetically (10 > 2)
    studies = [i[1] for i in studies]  # Return to file name

    for study in studies:
        study_disp = study[:study.index('.')]
        print(f"Study {study_disp}:")

        with open(os.path.join(results_directory, study), 'r') as jf:
            results = json.loads(jf.read())
            i_summary = '\t' + study_summary(results)
            print(i_summary.replace('\n', '\n\t'), '\n')
