import cv2
import torch
from ultralytics import YOLO
from typing import List, Dict
import time
from src.utils.config import Settings

class PersonFinder:
    def __init__(self):
        self.model = None
        self.device = self._pick_device()
        self._load_model()
    
    def _pick_device(self):
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def _load_model(self):
        try:
            self.model = YOLO(Settings.YOLO_MODEL)
            self.model.to(self.device)
        except Exception as qate:
            print(f"Model load failed: {qate}")
            raise
    
    def find_people(self, frame) -> List[Dict]:
        if self.model is None:
            return []
        
        adamdar = []
        
        try:
            natizheler = self.model(
                frame, 
                conf=Settings.CONFIDENCE_THRESHOLD,
                iou=Settings.IOU_THRESHOLD,
                imgsz=Settings.DETECTION_SIZE,
                augment=Settings.AUGMENT,
                verbose=False
            )
            
            for natizhe in natizheler:
                if natizhe.boxes is None:
                    continue
                
                for qorap in natizhe.boxes:
                    if int(qorap.cls) != Settings.PERSON_CLASS_ID:
                        continue
                    
                    bbox = qorap.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, bbox)
                    senim = float(qorap.conf[0])
                    
                    adam = {
                        'bbox': (x1, y1, x2, y2),
                        'confidence': senim,
                        'class_id': int(qorap.cls),
                        'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                    }
                    
                    adamdar.append(adam)
                    
        except Exception as qate:
            print(f"Detection error: {qate}")
            return []
        
        return adamdar
    
    def draw_people(self, frame, adamdar):
        natizhe = frame.copy()
        
        for adam in adamdar:
            x1, y1, x2, y2 = adam['bbox']
            senim = adam['confidence']
            
            tus = (0, 255, 0) if senim > 0.5 else (0, 255, 255)
            cv2.rectangle(natizhe, (x1, y1), (x2, y2), tus, Settings.DETECTION_THICKNESS)
            
            belgi = f"Adam {senim:.2f}"
            cv2.putText(
                natizhe,
                belgi,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                tus,
                2
            )
        
        return natizhe
    
    def get_stats(self):
        return {
            'model': Settings.YOLO_MODEL,
            'device': self.device,
            'threshold': Settings.CONFIDENCE_THRESHOLD
        }
