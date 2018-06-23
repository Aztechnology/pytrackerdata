from cili.util import load_eyelink_dataset
from Internal.qol_functions import kwarget
import numpy as np


# This is a root-class of a SubjectType, it's not meant to be used directly, your subject is a subclass of an
# Eyelink subject.
# If you need to change how to handle something (like getfix) you can override functions in a subclass.
# TODO: In the future I'll make it possible to get a file from a cloud storage like google or aws
class EyelinkType(object):
    # example:
    # filepath = /dir/myname.asc  (this includes the file name)
    # name = myname  (this doesn't include .asc extension)
    def __init__(self, **kwargs):
        self.filepath = kwarget('file', None, **kwargs)
        self.name = kwarget('name', self.getname(), **kwargs)

        # Subjects have samples and events as data columns and event tags (like FIX, BLINK) respectively
        self.samples, self.events = self.parse_eyetracker_data()

    # As default (or commodity) we assume subject ID is dir/"myname".asc, override this if you want to specify
    def getname(self):
        if self.filepath is None:
            return None

        start = max(self.filepath.rfind('/'), self.filepath.rfind('\\')) + 1  # filepath could use slash or bslash
        end = self.filepath.rfind('.')
        if start == -1 or end == -1:
            raise ValueError("Could not extract a valid name from filepath on file: " + self.filepath)
        return self.filepath[start:end]

    # TODO: For now we use (github) beOn/cili toolbox to parse data, in the future we could streamline this
    def parse_eyetracker_data(self):
        if self.filepath is None:
            return None, None
        samples, events = load_eyelink_dataset(self.filepath)
        return samples, events

    def get_blinks(self):
        if self.events is None:
            raise ValueError("Cannot get_blinks if no parsed events on filepath:" + self.filepath)
        blink_data = []
        for i_blink, a_blink in self.events.dframes['EBLINK'].iterrows():
            blink_on = i_blink
            blink_off = i_blink + a_blink.duration
            blink_data.append((blink_on, blink_off))
        # Blink columns: blink start and end time-stamp
        # TODO: Maybe pandas dataframe is a better structure to use instead, must discuss
        return np.array(blink_data, dtype=[('t_on', int), ('t_off', int)])

    # get_saccades may use blinkdata to clean anidated saccades by a blink, which is a common noise in eyelink data
    def get_saccades(self, _blinkdata=None):
        if self.events is None:
            raise ValueError("Cannot get saccades with no parsed event data on file" + self.filepath)
        saccade_data = []
        for i_sac, a_saccade in self.events.dframes['ESACC'].iterrows():
            saccade_on = i_sac
            saccade_off = i_sac + a_saccade.duration
            # If blink data given reject saccades that contain a blink
            if _blinkdata is not None:
                blink_mask = (saccade_on <= _blinkdata['t_on']) & (_blinkdata['t_off'] <= saccade_off)
            else:
                blink_mask = 0  # A mask with no data to eliminate
            if np.any(blink_mask):  # Then it's a false sacade, we ignore it
                continue
            amplitude = np.hypot(a_saccade.x_end - a_saccade.x_start, a_saccade.y_end - a_saccade.y_start)
            saccade_data.append((saccade_on, saccade_off, a_saccade.x_start, a_saccade.y_start, a_saccade.x_end,
                                 a_saccade.y_end, a_saccade.peak_velocity, amplitude))
        # Saccade columns: timestamps start-end, x-y position start and end, velocity and amplitude in pixels
        return np.array(saccade_data, dtype=[('t_on', int), ('t_off', int), ('x_on', float), ('y_on', float),
                                             ('x_off', float), ('y_off', float), ('vel', float), ('amp', float)])

    def get_fixations(self):
        if self.events is None:
            raise ValueError("Tried to get fixations with no parsed date on file" + self.filepath)
        fixation_data = []
        for i_fix, a_fix in self.events.dframes['EFIX'].iterrows():
            fix_on = i_fix
            fix_off = i_fix + a_fix.duration
            fixation_data.append((fix_on, fix_off, a_fix.x_pos, a_fix.y_pos))
        # Fixation columns: timestamps start-end and x-y position.
        return np.array(fixation_data, dtype=[('t_on', int), ('t_off', int), ('x_on', float), ('y_on', float)])

    # Coming functions are used to extend information of fix-sacc to fix-sacc on background or stimuli
    # It's important for each subjectType to know how to parse image information about images presented in experiment
    # Also we treat imageset id's as strings (even if they're ints), you can override this on your class
    def parse_imageset(self):
        raise ValueError("parse_imageset results in experimentimage array with info, override for each subclass")

    # We add two extra columns to fixdata: the image and the object inside the image being fixated
    def extend_fixations(self, _fixdata=None, _imagearray=None):
        if _fixdata is None:  # I create fixdata myself
            fixdata = self.get_fixations()
        else:
            fixdata = _fixdata

        if _imagearray is None:  # I parse the imageset myself
            imagearray = self.parse_imageset()
        else:
            imagearray = _imagearray

        extended_fixdata = []
        for a_fix in fixdata:
            # First check if inside an image
            fix_imageid = None
            fix_objectid = None
            for an_image in imagearray:
                if an_image.image_in_time(a_fix['t_on']):  # We check if inside an object of that image
                    fix_imageid = an_image.imageid
                    fix_object = an_image.get_object_on([a_fix['x_on'], a_fix['y_on']])
                    if fix_object is not None:
                        fix_objectid = fix_object.objectid
                    break
            extended_fixdata.append(tuple(a_fix) + (fix_imageid, fix_objectid,))
        return np.array(extended_fixdata, dtype=[('t_on', int), ('t_off', int), ('x_on', float), ('y_on', float),
                                                 ('image', 'U24'), ('object', 'U16')])

    # We add three columns: image where saccade occurs, and object it saccades from and to
    def extend_saccades(self, _saccdata=None, _imagearray=None):
        if _saccdata is None:  # I create saccdata
            blinkdata = self.get_blinks()
            saccdata = self.get_saccades(blinkdata)
        else:
            saccdata = _saccdata
        if _imagearray is None:  # I create imageset array
            imagearray = self.parse_imageset()
        else:
            imagearray = _imagearray
        extended_saccdata = []
        for a_sacc in saccdata:
            # First check image
            sacc_imageid = None
            sacc_objectid_on = None
            sacc_objectid_off = None
            for an_image in imagearray:
                if an_image.image_in_time(a_sacc['t_on']):  # we check if it saccades to objects in that image
                    sacc_imageid = an_image.imageid
                    sacc_object_on = an_image.get_object_on([a_sacc['x_on'], a_sacc['y_on']])
                    sacc_object_off = an_image.get_object_on([a_sacc['x_off'], a_sacc['y_off']])
                    if sacc_object_on is not None:
                        sacc_objectid_on = sacc_object_on.objectid
                    if sacc_object_off is not None:
                        sacc_objectid_off = sacc_object_off.objectid
                    break
            extended_saccdata.append(tuple(a_sacc) + (sacc_imageid, sacc_objectid_on, sacc_objectid_off,))
        return np.array(extended_saccdata, dtype=[('t_on', int), ('t_off', int), ('x_on', float), ('y_on', float),
                                                  ('x_off', float), ('y_off', float), ('vel', float), ('amp', float),
                                                  ('image', 'U24'), ('object_on', 'U16'),
                                                  ('object_off', 'U16')])
