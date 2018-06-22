import math
from Internal.qol_functions import kwarget


# EmbeddedObject Class helps organize and localize the types of objects inside a stimuli used (i.e.: ImageStimuli)
class EmbeddedObject(object):
    # This class consists of any kind of object inside a stimuli (for now thinking of an image presentation)
    # This is a root-class: objects can have many forms and many ways they can be localized (rectangular, radial, etc)
    # Each class must specify what self.coordinates contains and assure it's used as it's intended!

    def __init__(self, **kwargs):
        self.imageid = kwarget('imageid', None, **kwargs)
        self.coordinates = kwarget('coords', None, **kwargs)
        self.objectid = kwarget('objectid', None, **kwargs)

    # Check if this object belongs to a certain image using image-id
    def belongs_to(self, imageid):
        return self.imageid == imageid

    # Check if this object is being gazed at a certain gaze coordinates
    # IMPORTANT: "coords" is a tuple, can be a rectangle (two 2D points) or radial (center and radius) or even a mask,
    # this depends on the object-type, which is why this function must be defined in each class!
    def is_gazed(self, coordinates):
        raise ValueError("Using is_gazed method on root-class object which is not meant to be used")


# This class uses two 2D <<pixel>> coordinates to form a rectangular area as object location, using top-left and
# bottom-right corners as reference, important to note that pixel coords' (0,0) are in the top-left corner
class RectangularObject(EmbeddedObject):
    # You can pass directly a 'coords=' like it's father or also give x0, y0, x1, y1
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        x0 = kwarget('x0', None, **kwargs)
        x1 = kwarget('x1', None, **kwargs)
        y0 = kwarget('y0', None, **kwargs)
        y1 = kwarget('y1', None, **kwargs)

        if all([x0, y0, x1, y1]):  # they're all not None
            self.coordinates = [(x0, y0), (x1, y1)]

    def is_gazed(self, coordinates):
        top_left_x, top_left_y = self.coordinates[0]  # self.coordinates contain two 2D points
        bottom_right_x, bottom_right_y = self.coordinates[1]
        x, y = coordinates
        return top_left_x <= x <= bottom_right_x and top_left_y <= y <= bottom_right_y


# This class uses a center coordinate and a radial pixel threshold as object location
class RadialObject(EmbeddedObject):
    # You can pass directly a 'coords=' or x,y and radius variable
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        radius = kwarget('radius', None, **kwargs)
        centerx = kwarget('x', None, **kwargs)
        centery = kwarget('y', None, **kwargs)

        if all([radius, centerx, centery]):  # radius and center are not None
            self.coordinates = (centerx, centery, radius)

    def is_gazed(self, coordinates):
        object_x, object_y, object_radius = self.coordinates  # self.coordinates contains (x,y,r) center and radius
        x, y = coordinates

        # Calculate distance (using math module)
        distance = math.hypot(object_x - x, object_y - y)
        return distance <= object_radius


class MaskObject(EmbeddedObject):
    # This class is for more complex and precise objects: a mask of the image size is used with logical data for each
    # pixel that belongs to the object
    def is_gazed(self, _coordinates):
        # TODO: Finish this function in the future, still unfinished because it's not being used.
        pass
