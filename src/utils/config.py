class Settings:
    YOLO_MODEL = "yolov8n.pt"
    CONFIDENCE_THRESHOLD = 0.10
    PERSON_CLASS_ID = 0
    DETECTION_SIZE = 416
    IOU_THRESHOLD = 0.45
    AUGMENT = True
    
    ZONE_COLOR = (255, 0, 0)
    ZONE_THICKNESS = 2
    ZONES_FILE = "restricted_zones.json"
    
    ALARM_TIMEOUT = 3
    ALARM_COLOR = (0, 0, 255)
    
    DETECTION_COLOR = (0, 255, 0)
    DETECTION_THICKNESS = 2