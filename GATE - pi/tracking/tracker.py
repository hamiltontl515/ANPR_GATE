import numpy as np
from logic.vote_buffer import VoteBuffer

"""track has its unique id, its boundary box, buffer containing the ocr values for its license plate as it changes over time, missed
counts how many times the license plate is not counted(confidence too low) and active which dictacte whether it is in frame or not"""

class Track:
    def __init__(self, track_id, bbox):
        self.id = track_id
        self.bbox = bbox  # (xmin, ymin, xmax, ymax)
        #ocr
        self.current_text = None
        self.final_text = None
        #history
        self.vote_buffer = VoteBuffer()
        self.missed = 0
        self.active = True
        self.closest = False
        self.lane = None
        #event control
        self.triggered = False

"""simpletracker is a track manager which updates information on current tracks (keeps track on tracks-if you pardon the pun), determines
whether the plate is the same plate or different using an iou threshold (overlap threshold) if the overlap is sufficient the plate is the
same plate and track info is updated, if not a new track is made"""

class SimpleTracker:
    def __init__(self, iou_threshold=0.4, max_missed=10):
        self.iou_threshold = iou_threshold
        self.max_missed = max_missed
        self.tracks = []
        self.next_id = 0

    def iou(self, box1, box2):
        x1, y1, x2, y2 = box1
        x1_p, y1_p, x2_p, y2_p = box2

        xi1 = max(x1, x1_p)
        yi1 = max(y1, y1_p)
        xi2 = min(x2, x2_p)
        yi2 = min(y2, y2_p)

        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x2_p - x1_p) * (y2_p - y1_p)

        union = box1_area + box2_area - inter_area

        return inter_area / union if union > 0 else 0

    def update(self, detections):
        """
        detections = list of (bbox, conf)
        """
        updated_tracks = []

        for det_bbox, det_conf in detections:
            matched = False

            for track in self.tracks:
                if self.iou(det_bbox, track.bbox) > self.iou_threshold:
                    track.bbox = det_bbox
                    track.missed = 0
                    updated_tracks.append(track)
                    matched = True
                    break

            if not matched:
                new_track = Track(self.next_id, det_bbox)
                self.next_id += 1
                updated_tracks.append(new_track)

        # handle missed tracks
        for track in self.tracks:
            if track not in updated_tracks:
                track.missed += 1
                if track.missed < self.max_missed:
                    updated_tracks.append(track)

        self.tracks = updated_tracks
        return self.tracks