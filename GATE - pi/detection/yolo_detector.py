from ultralytics import YOLO

def load_model(model_path):
    model = YOLO(model_path)
    return model


def detect(model, frame, conf_thres=0.5):
    """
    Runs YOLO on a frame and returns:
    [(bbox, confidence), ...]
    """

    results = model(frame, verbose=False)

    detections = []

    for r in results:
        for box in r.boxes:

            conf = float(box.conf[0])

            if conf < conf_thres:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append(((x1, y1, x2, y2), conf))

    return detections