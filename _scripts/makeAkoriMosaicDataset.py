from SubjectTypes.eyelinkType import EyelinkType
from StimuliTypes.experimentImage import ExperimentImage
from StimuliTypes.embeddedObject import RectangularObject
from FileOutTypes.basicJSON import eye_extended_json
import os


# Let's create our akori mosaic class to tell the code the unique perks in how to process our data.
# This project works just like akoriWeb, where they have the list of actually watched images in a separate file and tag
# the moment where an image is watched. SO IT'S AN AKORIWEB COPY WITH SOME SMALL DETAILS.
# file: actual_TRIAL_DataSource_Experimento_mosaicos_CALIBRATION_SEQUENCE_DRIFT_SEQUENCETRIAL
# tag: 'Inicio_imagen_mosaico'
class AkoriMosaicSubject(EyelinkType):
    exact_image_info_file = 'actual_TRIAL_DataSource_Experimento_mosaicos_CALIBRATION_SEQUENCE_DRIFT_SEQUENCETRIAL.dat'
    # In this project we have 9 rectangular mosaics, to arrange them as objects we need the starting position of the
    # first and also it's width and height
    # mosaic_start = [200, 0]
    # mosaic_size = [400, 300]
    # with this we can calculate mosaic positions:
    X0 = [200 + (x % 3)*400 for x in range(9)]
    X1 = [200 + ((x % 3) + 1)*400 for x in range(9)]
    Y0 = [int(y/3) * 300 for y in range(9)]
    Y1 = [int((y/3) + 1) * 300 for y in range(9)]

    # We get imageid from separate file and image timestamp from events
    def parse_imageset(self):
        # Let's embark on the adventure of finding image timestamps from the subject file
        images_on = []
        images_off = []
        for i_msg, msg in self.events.dframes['MSG'].iterrows():
            if isinstance(msg.content, str) and ('Inicio_imagen_mosaico' in msg.content):
                images_on.append(msg.name)
                # images end after 12 seconds (12000 miliseconds) at a fixed rate, therefore:
                images_off.append(msg.name + 12000)
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
                # Let's add the 9 mosaic positions as rectangular objects
                for pos in range(9):
                    coords = [self.X0[pos], self.Y0[pos], self.X1[pos], self.Y1[pos]]
                    mosaic = RectangularObject(coords=coords, objectid=pos+1)
                    an_image.add_object(mosaic)
                image_array.append(an_image)
        return image_array


# We use the function basicJSONFile to save fixations and saccades
database_path = "D:/Drive/Database/akori_mosaics/raw/"
out_path = "D:/Drive/Database/akori_mosaics/dataset/"

# Iterate over path's dir list: "pup01,....,etc"
subjects_folder = os.listdir(database_path)
for afolder in subjects_folder:
    # Find ascii files
    ascii_files = [f for f in os.listdir(database_path + afolder) if f.endswith('.asc')]
    # Well, there should be one ascii file only but we iterate just in case
    for afile in ascii_files:
        # Make an AkoriMosaicSubject type
        file_in = "{dir}/{folder}/{file}".format(dir=database_path, folder=afolder, file=afile)
        aSubject = AkoriMosaicSubject(file=file_in)
        # Make a basic json file and save it in out_path
        file_out = "{dir}/{file}.json".format(dir=out_path, file=aSubject.name)
        eye_extended_json(aSubject, file_out, verbose=True)  # Last true statement enables verbose (prints stuff)
