from plane_tracker import PlaneTracker


class CompareImage:
    """
    This lets you compare multiple template images to some arbitrary image, and return True or False if it's a 'match',
    where the match is fairly loosly defined.

    The class doesn't have to be too accurate, as long as there are few false negatives.
    """

    def __init__(self, features_detect=1500):
        self.tracker = PlaneTracker(0.025, 10, max_features_detect=1500)

    def add_template(self, img):
        """
        This will add a template image to compare other images to. It will add the whole image,
        then many other smaller parts of the image, to try to capture more images.
        """
        h, w, _ = img

        # Track the whole image
        self.tracker.add_target(img, (0, 0, w, h))

        # Track the center quarter of the image
        self.tracker.add_target(img, (int(w * .25),
                                      int(h * .25),
                                      int(w * .75),
                                      int(h * .75)))

        # Track the right half of the image
        self.tracker.add_target(img, (int(w * .5),
                                      int(h * .5),
                                      int(w * 1),
                                      int(h * 1)))

        # Track the left half of the image
        self.tracker.add_target(img, (int(w * 0),
                                      int(h * 0),
                                      int(w * .5),
                                      int(h * .5)))


    def is_match(self, img):
        """ This will compare the img to the images that are currently being compared"""
        pass