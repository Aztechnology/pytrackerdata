import csv
from Internal.qol_functions import kwarget


# Makes a csv file that has fixations and saccades, fix and sac have different dimensions but are simply recorded
def eye_basic_csv(_subject_type, _out_file, **kwargs):

    talkative = kwarget('verbose', False, **kwargs)

    # If subject has no filepath I can't do shit honestly
    if _subject_type.filepath is None:
        raise ValueError("eye_movement csv file can't be done without a subject with pathfile")

    if talkative:
        print("Reading: {file}".format(file=_subject_type.filepath))

    # If it doesn't have events I make them
    if _subject_type.events is None:
        _, _subject_type.events = _subject_type.parse_eyetracker_data()

    # Get fixations and saccades
    fixations = _subject_type.get_fixations()
    blinks = _subject_type.get_blinks()
    saccades = _subject_type.get_saccades(blinks)

    # The main problem for writing the file is that fixations and saccades have different columns
    # But this file is so basic it doesn't care about it
    out_data = []
    fix_count = 0
    sac_count = 0
    # TODO: Find a cleaner way to do this
    while len(fixations) > fix_count or len(saccades) > sac_count:
        if len(saccades) == sac_count and len(fixations) > fix_count:  # only fix remain, append fix
            out_data.append(('fix',) + tuple(fixations[fix_count]))
            fix_count += 1
            continue
        if len(fixations) == fix_count and len(saccades) > sac_count:  # only sac remain, append sac
            out_data.append(('sac',) + tuple(saccades[sac_count]))
            sac_count += 1
            continue
        if fixations[fix_count]['t_on'] <= saccades[sac_count]['t_on']:  # append fix
            out_data.append(('fix',) + tuple(fixations[fix_count]))
            fix_count += 1
            continue
        if fixations[fix_count]['t_on'] >= saccades[sac_count]['t_on']:  # append sac
            out_data.append(('sac',) + tuple(saccades[sac_count]))
            sac_count += 1
            continue
    # Now we write file
    if talkative:
        print("Writing: {file}".format(file=_out_file))
    with open(_out_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(out_data)
    return


# Create a file that cleans fix-sac outside the image set and adds image/object id columns
def eye_extended_csv(_subject_type, _out_file, **kwargs):

    talkative = kwarget('verbose', False, **kwargs)

    # If subject has no filepath I can't do shit honestly
    if _subject_type.filepath is None:
        raise ValueError("eye_movement csv file can't be done without a subject with pathfile")

    if talkative:
        print("Reading: {file}".format(file=_subject_type.filepath))

    # If it doesn't have events I make them
    if _subject_type.events is None:
        _, _subject_type.events = _subject_type.parse_eyetracker_data()

    # Get fixations and saccades
    fixations = _subject_type.extend_fixations()
    saccades = _subject_type.extend_saccades()

    # The main problem for writing the file is that fixations and saccades have different columns
    # But this file is so basic it doesn't care about it
    out_data = []
    fix_count = 0
    sac_count = 0
    # TODO: Find a cleaner way to do this
    while len(fixations) > fix_count or len(saccades) > sac_count:
        if len(saccades) == sac_count and len(fixations) > fix_count:  # only fix remain, append fix
            if fixations[fix_count]['image'] != 'None':
                out_data.append(('fix',) + tuple(fixations[fix_count]))
            fix_count += 1
            continue
        if len(fixations) == fix_count and len(saccades) > sac_count:  # only sac remain, append sac
            if saccades[sac_count]['image'] != 'None':
                out_data.append(('sac',) + tuple(saccades[sac_count]))
            sac_count += 1
            continue
        if fixations[fix_count]['t_on'] <= saccades[sac_count]['t_on']:  # append fix
            if fixations[fix_count]['image'] != 'None':
                out_data.append(('fix',) + tuple(fixations[fix_count]))
            fix_count += 1
            continue
        if fixations[fix_count]['t_on'] >= saccades[sac_count]['t_on']:  # append sac
            if fixations[fix_count]['image'] != 'None':
                out_data.append(('sac',) + tuple(saccades[sac_count]))
            sac_count += 1
            continue
    # Now we write file
    if talkative:
        print("Writing: {file}".format(file=_out_file))
    with open(_out_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(out_data)
    return
