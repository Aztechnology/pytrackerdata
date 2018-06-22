from Internal.qol_functions import kwarget


# Stimuli image class, helps keeps in order what an image contains, it's name, timestamp in experiment and objects
# embedded in the image
class ExperimentImage(object):
    # imageid: string,
    # timestamp: array of two numbers (start-end)
    # objects: object array of embeddedObject.py
    def __init__(self, **kwargs):
        self.objects = kwarget('objects', [], **kwargs)
        self.imageid = kwarget('imageid', None, **kwargs)
        self.timestamp = kwarget('timestamp', None, **kwargs)

    # Adds a gazeable object to the array
    def add_object(self, newobject):
        # TODO: This function may not append newobject correctly
        self.objects.append(newobject)

    # You can ask if an image is being shown at a certain timestamp
    def shown_in_time(self, time):
        return self.timestamp[0] <= time <= self.timestamp[1]

    # Returns an object class that's being gazed at the coordinates, if no object is there then returns none
    def get_object_on(self, coordinates):
        for an_object in self.objects:
            if an_object.is_gazed(coordinates):
                return an_object
        return None
