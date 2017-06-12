import cv2
import numpy as np
from collections import namedtuple


class Tracker:
    """
        This is the base class for any vision based object tracker.
        All object trackers carry a "history" of tracked objects, in an array called trackedHistory.
        This is later searched through to find objects that have been tracked.
    """

    def __init__(self, historyLength):
        self.historyLen = historyLength
        self.targets = []
        self.history = [[] for i in range(self.historyLen)]

        self.fFnt = cv2.FONT_HERSHEY_PLAIN  # Font for filter functions
        self.fColor = (255, 255, 255)  # Default color for filter functions
        self.fThickness = 2  # Thickness of lines

    def _addToHistory(self, trackedArray):
        # Add an array of detected objects to the self.trackedHistory array, and shorten the trackedHistory array
        # so that it always remains self.historyLength long
        self.history.insert(0, trackedArray)

        while len(self.history) > self.historyLen:
            del self.history[-1]

    def clear(self):
        self.history = [[] for i in range(self.historyLen)]
        self.targets = []


class PlaneTracker(Tracker):
    """
    This class tracks objects using ORB feature descriptors.

    PlanarTarget:
        image     - image to track
        rect      - tracked rectangle (x1, y1, x2, y2)
        keypoints - keypoints detected inside rect
        descrs    - their descriptors
        data      - some user-provided data
    TrackedTarget:
        target - reference to PlanarTarget
        p0     - matched points coords in target image
        p1     - matched points coords in input frame
        H      - homography matrix from p0 to p1
        quad   - target bounary quad in input frame
    """

    View = namedtuple('View', ['image', 'rect'])

    PlaneTarget = namedtuple('PlaneTarget', ['view', 'keypoints', 'descrs'])

    # target: the "sample" object of the tracked object. Center: [x,y,z] Rotation[xr, yr, zr], ptCount: matched pts
    TrackedPlane = namedtuple('TrackedPlane', ['view', 'target', 'quad', 'ptCount',
                                               'center', 'rotation', 'p0', 'p1', 'H',
                                               'match_ratio'])

    # Tracker parameters
    FLANN_INDEX_KDTREE = 1
    FLANN_INDEX_LSH = 6
    MIN_MATCH_COUNT = 15


    flanParams = dict(algorithm=FLANN_INDEX_LSH,
                      table_number=6,  # 3,  #  6,  # 12,
                      key_size=12,  # 19,  # 12,  # 20,
                      multi_probe_level=1)  # 1)   #  1)  #  2)

    K = None  # Set in get3DCoordinates
    dist_coeffs = np.zeros(4)

    def __init__(self, focal_length, history_length, max_features_detect=5000):
        super(PlaneTracker, self).__init__(history_length)
        self.focal_length = focal_length
        self.detector = cv2.ORB_create(nfeatures=max_features_detect)

        # For ORB
        self.matcher = cv2.FlannBasedMatcher(self.flanParams, {})  # bug : need to pass empty dict (#1329)

    def create_target(self, view):
        """
        There's a specific function for this so that the GUI can pull the objects information and save it as a file
        using objectManager. Other than that special case, this function is not necessary for normal tracker use
        """

        # Get the PlanarTarget object for any name, image, and rect. These can be added in self.addTarget()
        x0, y0, x1, y1 = view.rect
        points, descs = [], []

        raw_points, raw_descrs = self.__detect_features(view.image)

        for kp, desc in zip(raw_points, raw_descrs):
            x, y = kp.pt
            if x0 <= x <= x1 and y0 <= y <= y1:
                points.append(kp)
                descs.append(desc)

        descs = np.uint8(descs)
        target = self.PlaneTarget(view=view, keypoints=points, descrs=descs)

        # If it was possible to add the target
        return target

    def add_target(self, img, rect):
        # This function checks if a view is currently being tracked, and if not it generates a target and adds it

        for target in self.targets:
            if img == target.view: return
        view = self.View(image=img, rect=rect)
        planar_target = self.create_target(view)

        descrs = planar_target.descrs
        self.matcher.add([descrs])
        self.targets.append(planar_target)

    def clear(self):
        super().clear()

        # Remove all targets
        self.matcher.clear()

    def track(self, frame):
        # updates self.tracked with a list of detected TrackedTarget objects
        frame_points, frame_descrs = self.__detect_features(frame)
        tracked = []

        # If no keypoints were detected, then don't update the self.trackedHistory array
        if len(frame_points) < self.MIN_MATCH_COUNT:
            self._addToHistory(tracked)
            return
        matches = self.matcher.knnMatch(frame_descrs, k=2)

        # try:
        #     matches = self.matcher.knnMatch(frame_descrs, k=2)
        # except Exception as e:
        #     print("OPENCV ERROR!", e)
        #     return

        matches = [m[0] for m in matches if len(m) == 2 and m[0].distance < m[1].distance * 0.75]

        if len(matches) < self.MIN_MATCH_COUNT:
            self._addToHistory(tracked)
            return

        matches_by_id = [[] for _ in range(len(self.targets))]
        for m in matches:
            matches_by_id[m.imgIdx].append(m)

        tracked = []

        for imgIdx, matches in enumerate(matches_by_id):

            if len(matches) < self.MIN_MATCH_COUNT:
                continue

            target = self.targets[imgIdx]

            p0 = [target.keypoints[m.trainIdx].pt for m in matches]
            p1 = [frame_points[m.queryIdx].pt for m in matches]
            p0, p1 = np.float32((p0, p1))
            H, status = cv2.findHomography(p0, p1, cv2.RANSAC, 3.0)

            status = status.ravel() != 0
            if status.sum() < self.MIN_MATCH_COUNT: continue

            p0, p1 = p0[status], p1[status]

            x0, y0, x1, y1 = target.view.rect
            quad = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
            quad = cv2.perspectiveTransform(quad.reshape(1, -1, 2), H).reshape(-1, 2)

            # Calculate the 3d coordinates of the object
            center, rotation = self._get_3D_coordinates(frame, target.view.rect, quad)

            track = self.TrackedPlane(target=target,
                                      view=target.view,
                                      quad=quad,
                                      ptCount=len(matches),
                                      match_ratio=len(matches) / len(target.keypoints),
                                      center=center,
                                      rotation=rotation,
                                      p0=p0, p1=p1, H=H)
            tracked.append(track)

        tracked.sort(key=lambda t: len(t.p0), reverse=True)

        self._addToHistory(tracked)

    def __detect_features(self, frame):
        cv2.ocl.setUseOpenCL(False)  # THIS FIXES A ERROR BUG: "The data should normally be NULL!"

        # detect_features(self, frame) -> keypoints, descrs
        keypoints, descrs = self.detector.detectAndCompute(frame, None)
        if descrs is None:  # detectAndCompute returns descs=None if not keypoints found
            descrs = []
        return keypoints, descrs

    def draw_tracked(self, frame):

        # Sort the objects from lowest (z) to highest Z, so that they can be drawn one on top of the other
        drawObjects = self.history[0]
        drawObjects = sorted(drawObjects, key=lambda obj: obj.center[2], reverse=True)

        mask = np.zeros_like(frame)
        tMask = np.zeros_like(frame)  # Used to show transparent shapes

        for tracked in drawObjects:
            quad = np.int32(tracked.quad)

            # If this object is definitely higher than the other, erase everything beneath it to give the "3D" effect
            cv2.fillConvexPoly(mask, quad, 0)

            # Draw the tracked points
            for (x, y) in np.int32(tracked.p1):
                cv2.circle(tMask, (x, y), 2, (255, 255, 255))

            # Draw the rectangle around the object- in both the normal mask and the transparent one
            cv2.polylines(mask, [quad], True, (255, 255, 255), 3)
            cv2.polylines(tMask, [quad], True, (255, 255, 255), 2)

            # Draw coordinate grids on each object with a red, green, and blue arrow
            rect = tracked.view.rect
            x0, y0, x1, y1 = rect
            width = (x1 - x0) / 2
            height = (y1 - y0) / 2
            x0, y0, x1, y1 = -width, -height, width, height

            #                       Line start  Triangle tip  Triangle vert1   Triangle vert2
            ar_verts = np.float32([[.5, 0, 0], [.5, 1, 0], [.45, .95, 0], [.55, .95, 0],  # Y
                                   [0, .5, 0], [1, .5, 0], [.95, .45, 0], [.95, .55, 0],  # X
                                   [.5, .5, 0], [.5, .5, 1], [.45, .5, .90], [.55, .5, .90]])  # Z axis

            # Color of each arrow
            red = (1, 1, 255)
            green = (1, 255, 1)
            blue = (255, 1, 1)

            # Which elements in ar_verts are to be connected with eachother as a line
            ar_edges = [(0, 1, red),  # ( 2, 1,   red), ( 3, 1,    red),
                        (4, 5, blue),  # ( 6, 5,  blue), ( 7, 5,   blue),
                        (8, 9, green)]  # , (10, 9, green), (11, 9,  green)]

            verts = ar_verts * [(x1 - x0), (y1 - y0), -(x1 - x0) * 0.3] + (x0, y0, 0)

            # Project the arrows in 3D
            center = np.array(tracked.center).reshape(-1, 1)
            rotation = np.array(tracked.rotation).reshape(-1, 1)
            verts = cv2.projectPoints(verts, rotation, center, self.K, self.dist_coeffs)[0].reshape(-1, 2)

            # Draw lines for the arrows
            for i, j, color in ar_edges:
                (x0, y0), (x1, y1) = verts[i], verts[j]
                cv2.line(mask, (int(x0), int(y0)), (int(x1), int(y1)), color, 2)

            # Draw triangles for the arrows
            for i in range(0, 3):
                row = i * 4
                cv2.fillConvexPoly(mask, np.int32([verts[row + 1], verts[row + 2], verts[row + 3]]), ar_edges[i][2])

        # Draw the text seperately, so it's always on top of everything
        for tracked in drawObjects:
            quad = np.int32(tracked.quad)
            rect = tracked.view.rect

            # Create the text that will be drawn
            nameText = tracked.view.name

            coordText = "(" + str(int(tracked.center[0])) + \
                        "," + str(int(tracked.center[1])) + \
                        "," + str(int(tracked.center[2])) + \
                        ") R" + str(int(math.degrees(tracked.rotation[2]) + 180))

            # Figure out how much the text should be scaled (depends on the different in curr side len, and orig len)
            origLength = rect[2] - rect[0] + rect[3] - rect[1]
            currLength = np.linalg.norm(quad[1] - quad[0]) + np.linalg.norm(quad[2] - quad[1])  # avg side len
            scaleFactor = currLength / origLength + .35

            # Find a location on screen to draw the name of the object
            size, _ = cv2.getTextSize(nameText, self.fFnt, scaleFactor, thickness=self.fThickness)
            txtW, txtH = size
            h, w, _ = mask.shape
            validCorners = [c for c in quad if 0 < c[1] < h]
            validCorners = [c for c in validCorners if (0 < c[0] and c[0] + txtW < w)]

            dist = 10 * scaleFactor

            # If a corner was found, draw the name on that corner
            if len(validCorners):
                chosenCorner = tuple(validCorners[0])

                # Draw the name of the object
                mask = drawOutlineText(mask, nameText, chosenCorner,
                                       self.fFnt, scaleFactor, color=self.fColor, thickness=self.fThickness)
                tMask = drawOutlineText(tMask, nameText, chosenCorner,
                                        self.fFnt, scaleFactor, color=self.fColor, thickness=self.fThickness)

                try:
                    # Draw the coordinates of the object
                    chosenCorner = chosenCorner[0], int(chosenCorner[1] + dist)
                    mask = drawOutlineText(mask, coordText, chosenCorner,
                                           self.fFnt, scaleFactor - .6, color=self.fColor, thickness=1)
                    tMask = drawOutlineText(tMask, coordText, chosenCorner,
                                            self.fFnt, scaleFactor - .6, color=self.fColor, thickness=1)
                except ValueError as e:
                    print("Vision| ERROR: Drawing failed because a None was attempted to be turned into int", e)

        # Apply the semi-transparent mask to the frame, with translucency
        frame[tMask > 0] = tMask[tMask > 0] * .7 + frame[tMask > 0] * .3

        # Apply the normal mask to the frame
        frame[mask > 0] = mask[mask > 0]  # *= mask == 0

        return frame

    # Thread safe
    def _get_3D_coordinates(self, frame, rect, quad):
        # Do solvePnP on the tracked object
        x0, y0, x1, y1 = rect
        width = (x1 - x0) / 2
        height = (y1 - y0) / 2
        quad3d = np.float32([[-width, -height, 0],
                             [width, -height, 0],
                             [width, height, 0],
                             [-width, height, 0]])

        if self.K is None:
            fx = 0.5 + self.focal_length / 50.0
            h, w = frame.shape[:2]
            self.K = np.float64([[fx * w, 0, 0.5 * (w - 1)],
                                 [0, fx * w, 0.5 * (h - 1)],
                                 [0.0, 0.0, 1.0]])

        ret, rotation, center = cv2.solvePnP(quad3d, quad, self.K, self.dist_coeffs)
        # print(rotation)
        # Convert every element to floats and return int in List form
        return tuple(map(float, center)), tuple(map(float, rotation))
