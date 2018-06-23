from FileOutTypes.basicJSON import eye_extended_json
from SubjectTypes.akoriSubject import AkoriSubject
import os


# We use the function basicCsvFile to save fixations and saccades
database_path = "D:/Drive/Database/akori_web2/raw/"
out_path = "D:/Drive/Database/akori_web2/dataset/"

# Iterate over path's dir list: "sujeto1,....,sujeto80"
subjects_folder = os.listdir(database_path)
for afolder in subjects_folder:
    # Find ascii files
    ascii_files = [f for f in os.listdir(database_path + afolder) if f.endswith('.asc')]
    # Well, there should be one ascii file only but we iterate just in case
    for afile in ascii_files:
        # Make an AkoriSubject type
        file_in = "{dir}/{folder}/{file}".format(dir=database_path, folder=afolder, file=afile)
        aSubject = AkoriSubject(file=file_in)
        # Make a basic csv file and save it in out_path
        file_out = "{dir}/{file}.json".format(dir=out_path, file=aSubject.name)
        eye_extended_json(aSubject, file_out, verbose=True)  # Last true statement enables verbose (prints stuff)
