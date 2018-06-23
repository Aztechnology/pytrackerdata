from SubjectTypes.eyelinkType import EyelinkType
from StimuliTypes.experimentImage import ExperimentImage


class AkoriSubject(EyelinkType):
    # Experimenters are "creative" when finding ways to store experiment data outside the file, like images viewed.
    # In akori's case, information is inside the events already (yay) but exact image seen on a separate file (oh no)
    # All akori subjects have this file on their directory containing imageid info
    exact_image_info_file = 'actual_Record_DataSource_AKORI_Instrucciones_Calibracion_trialRecord.dat'

    # We get imageid from separate file and image timestamp from events
    def parse_imageset(self):
        # Let's embark on the adventure of finding image timestamps from info_file
        images_on = []
        times_out = []
        for i_msg, msg in self.events.dframes['MSG'].iterrows():
            if isinstance(msg.content, str) and ('imagen' in msg.content):
                images_on.append(msg.name)
            if isinstance(msg.content, str) and ('time out' in msg.content):
                times_out.append(msg.name)
        # images_on has two false positives each 5 consecutive values, we need to erase 6th and 7th
        sub_images_on = [item for index, item in enumerate(images_on) if (index+2) % 7 != 0 and (index+1) % 7 != 0]
        images_off = []
        for an_image_on in sub_images_on:
            mask = [(x - an_image_on) > 0 for x in times_out]
            indexes = [i for i, x in enumerate(mask) if x]
            if not indexes:
                raise ValueError("parse_imageset: image_off not found in file " + self.filepath)
            images_off.append(times_out[indexes[0]])

        # Load image array from path without the time-stamps
        image_array = self.load_image_file()
        # Now add time-stamps to image array
        for index, image_on, image_off in zip(range(len(image_array)), images_on, images_off):
            image_array[index].timestamp = [image_on, image_off]
        return image_array

    # This function is a sub-routine of parse_imageset, loads the ugly file containing image id and returns it as array
    def load_image_file(self):
        image_array = []
        # Create info path to load
        slash_index = max(self.filepath.rfind('/'), self.filepath.rfind('\\'))
        complete_path = "{path}/{file}".format(path=self.filepath[:slash_index], file=self.exact_image_info_file)
        with open(complete_path) as f:
            data_lines = f.readlines()
        # Now separate each line into image id's, ignoring the first column
        for a_line in data_lines:
            data = a_line.split('\t')
            data.pop(0)  # Ignore first column
            for an_id in data:
                an_image = ExperimentImage()
                an_image.imageid = an_id.replace('\n', '')  # in case there's trailing newlines
                an_image.imageid = an_image.imageid.replace('"', '')  # ugly redundant " chars eliminated from string
                image_array.append(an_image)
        return image_array
