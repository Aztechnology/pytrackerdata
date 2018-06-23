import json
import codecs
from Internal.qol_functions import kwarget


# Makes a json file that has fixations and saccades
def eye_basic_json(_subject_type, _out_file, **kwargs):

    talkative = kwarget('verbose', False, **kwargs)

    # If subject has no filepath I can't do shit honestly
    if _subject_type.filepath is None:
        raise ValueError("eye_movement csv file can't be done without a subject with pathfile")

    if talkative:
        print("Reading: {file}".format(file=_subject_type.filepath))

    # If it doesn't have events I make them
    if _subject_type.events is None:
        _, _subject_type.events = _subject_type.parse_eyetracker_data()

    # Get fixations and saccades, also serialize to be json dumpable
    fixations = _subject_type.get_fixations().tolist()
    blinks = _subject_type.get_blinks()
    saccades = _subject_type.get_saccades(blinks).tolist()
    # Store data in a dict()
    data = {'fixations': fixations, 'saccades': saccades}

    # dump fixations and blinks into json
    if talkative:
        print("Dumping json to: {file}".format(file=_out_file))
    json.dump(data, codecs.open(_out_file, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)

    return


# Create a file that cleans fix-sac outside the image set and adds image/object id columns
def eye_extended_json(_subject_type, _out_file, **kwargs):

    talkative = kwarget('verbose', False, **kwargs)

    # If subject has no filepath I can't do shit honestly
    if _subject_type.filepath is None:
        raise ValueError("eye_movement csv file can't be done without a subject with pathfile")

    if talkative:
        print("Reading: {file}".format(file=_subject_type.filepath))

    # If it doesn't have events I make them
    if _subject_type.events is None:
        _, _subject_type.events = _subject_type.parse_eyetracker_data()

    # Get fixations and saccades, serialize them to be json dumpable
    fixations = _subject_type.extend_fixations()
    saccades = _subject_type.extend_saccades()
    fixation_header = fixations.dtype.names
    saccade_header = saccades.dtype.names

    # Make a dict() with data to dump
    data = {'fixation_header': fixation_header, 'fixations': fixations.tolist(),
            'saccade_header': saccade_header, 'saccades': saccades.tolist()}

    # Now we write file
    if talkative:
        print("Dumping json to: {file}".format(file=_out_file))
    json.dump(data, codecs.open(_out_file, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)

    return
