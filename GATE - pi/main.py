from detection.yolo_detector import load_model, detect
from tracking.tracker import SimpleTracker
from ocr.plate_reader import read_plate
from logic.vote_buffer import VoteBuffer
from logic.zones import get_zone
from utils.image_utils import crop_plate
from iot.thingsboard import ThingsBoardClient
from iot.gpio_controller import GateController

import cv2

def get_closest_track(track_list):
    if not track_list:
        return None
    return max(track_list, key=lambda t: (t.bbox[2]-t.bbox[0]) * (t.bbox[3]-t.bbox[1]))


MIN_AREA = 5000   
OCR_EVERY_N_FRAMES = 5

tracker = SimpleTracker()

frame_id = 0

model = load_model("detection/models/best.pt")

#cap = cv2.VideoCapture("test_vid.mp4") test vid
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)



while True:
    ret, frame = cap.read()
    h, w = frame.shape[:2]

    # Draw zones
    cv2.rectangle(frame, (0, 0), (w//2, h), (255,0,0), 2)      # ENTRY
    cv2.rectangle(frame, (w//2, 0), (w, h), (0,0,255), 2)      # EXIT

    cv2.putText(frame, "ENTRY", (50,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    cv2.putText(frame, "EXIT", (w//2 + 50,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    
    if not ret:
        break

    frame_id += 1

    detections = detect(model, frame)

    tracks = tracker.update(detections)

    entry_tracks=[]
    exit_tracks = []

    for track in tracks:
        if track.missed>5:
            continue

        x1, y1, x2, y2 = track.bbox

        #segment into lanes
        lane = get_zone(track.bbox, frame.shape)

        if track.lane is None and lane is not None:
            track.lane = lane

        if track.lane == "ENTRY":
            entry_tracks.append(track)
        elif track.lane == "EXIT":
            exit_tracks.append(track)

        #draw boundry box
        cv2.rectangle(frame, (x1,y1), (x2, y2), (0,255,0), 2)

        #put id on box
        cv2.putText(frame, f"ID{track.id}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)


    closest_entry = get_closest_track(entry_tracks)
    closest_exit = get_closest_track(exit_tracks)

    if closest_entry:
        #crop to send off to ocr
        crop, (x1,y1,x2,y2) = crop_plate(frame, closest_entry.bbox)
        area = (x2-x1)*(y2-y1)

        if (not closest_entry.triggered and area> MIN_AREA and frame_id%OCR_EVERY_N_FRAMES==0):
            text = read_plate(crop)

            if text:
                closest_entry.current_text = text
                closest_entry.vote_buffer.add(text)
            
        if closest_entry.current_text:
            cv2.putText(frame, closest_entry.current_text,(x1, y2+20),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        if (closest_entry.vote_buffer.is_ready() and closest_entry.current_text and not closest_entry.triggered):
            closest_entry.final_text = closest_entry.vote_buffer.get_final()

            closest_entry.triggered=True
            #print(f"PLATE:{closest_entry.final_text}, ENTRY")
            
            ThingsBoardClient.send_event(final_plate, "ENTRY")
            GateController.open_gate("IN")
            
    if closest_exit:
        #crop to send off to ocr
        crop, (x1,x2,y1,y2) = crop_plate(frame, closest_exit.bbox)
        area = (x2-x1)*(y2-y1)

        if (not closest_exit.triggered and area> MIN_AREA and frame_id%OCR_EVERY_N_FRAMES==0):
            text = read_plate(crop)

            if text:
                closest_exit.current_text = text
                closest_exit.vote_buffer.add(text)
            
        if closest_exit.current_text:
            cv2.putText(frame, closest_exit.current_text,(x1, y2+20),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        if (closest_exit.vote_buffer.is_ready() and closest_exit.current_text and not closest_exit.triggered):
            closest_exit.final_text = closest_exit.vote_buffer.get_final()

            closest_exit.triggered=True
            #print(f"PLATE:{closest_exit.final_text}, EXIT")

            ThingsBoardClient.send_event(final_plate, "EXIT")
            GateController.open_gate("OUT")
          

    cv2.imshow("ANPR", frame)

    if cv2.waitKey(1) == ord("q"):
        break