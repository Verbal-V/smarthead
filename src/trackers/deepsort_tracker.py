import cv2
import numpy as np
from typing import List, Dict, Optional
from src.utils.config import Settings

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False

class PersonTracker:
    def __init__(self):
        self.tracks = {}
        self.kelesi_id = 1   # kelesi_id (следующий ID)
        
        if DEEPSORT_AVAILABLE:
            self.tracker = self._init_tracker()
        else:
            self.tracker = None
    
    def _init_tracker(self):
        try:
            return DeepSort(
                max_age=60,
                n_init=3,
                nms_max_overlap=0.3
            )
        except Exception as qate:
            print(f"Tracker init error: {qate}")
            return None
    
    def update(self, adamdar, frame=None):
        if not adamdar:
            if self.tracker and DEEPSORT_AVAILABLE:
                self.tracker.update_tracks([], frame=frame)
            return []
        
        if self.tracker and DEEPSORT_AVAILABLE:
            return self._update_with_deepsort(adamdar, frame)
        else:
            return self._update_simple(adamdar)
    
    def _update_with_deepsort(self, adamdar, frame):
        baykau = []  # baykau (наблюдения)
        
        for adam in adamdar:
            bbox = adam['bbox']
            senim = adam['confidence']
            klass = adam['class_id']
            
            baykau.append([bbox[0], bbox[1], bbox[2], bbox[3], senim, klass])
        
        try:
            tracks = self.tracker.update_tracks(baykau, frame=frame)
            baykau_adamdar = []
            
            for iz in tracks:
                if not iz.is_confirmed() or iz.time_since_update > 1:
                    continue
                
                iz_id = iz.track_id
                bbox = iz.to_tlbr()
                
                kelgen_adam = self._find_match(adamdar, bbox)
                
                baqylangan = {
                    'bbox': (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])),
                    'confidence': kelgen_adam['confidence'] if kelgen_adam else iz.get_det_conf(),
                    'class_id': kelgen_adam['class_id'] if kelgen_adam else 0,
                    'center': kelgen_adam['center'] if kelgen_adam else (
                        int((bbox[0] + bbox[2]) // 2), 
                        int((bbox[1] + bbox[3]) // 2)
                    ),
                    'track_id': iz_id
                }
                
                baykau_adamdar.append(baqylangan)
            
            return baykau_adamdar
            
        except Exception:
            return self._update_simple(adamdar)
    
    def _update_simple(self, adamdar):
        baykau_adamdar = []
        
        for adam in adamdar:
            bar_id = self._find_best_match(adam)
            
            if bar_id is None:
                track_id = self.kelesi_id
                self.kelesi_id += 1
            else:
                track_id = bar_id
            
            self.tracks[track_id] = {
                'last_position': adam['center'],
                'bbox': adam['bbox']
            }
            
            baqylangan = adam.copy()
            baqylangan['track_id'] = track_id
            baykau_adamdar.append(baqylangan)
        
        self._cleanup_old()
        return baykau_adamdar
    
    def _find_best_match(self, adam):
        if not self.tracks:
            return None
        
        center = adam['center']
        azarak = float('inf')   
        en_jakyn = None         
        max_qashyktyk = 150     # расстояние
        
        for tid, info in self.tracks.items():
            last_center = info['last_position']
            dist = np.sqrt((center[0] - last_center[0])**2 + (center[1] - last_center[1])**2)
            
            if dist < azarak and dist < max_qashyktyk:
                azarak = dist
                en_jakyn = tid
        
        return en_jakyn
    
    def _find_match(self, adamdar, bbox):
        ortalyk = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
        azarak = float('inf')
        en_jakyn = None
        
        for adam in adamdar:
            center = adam['center']
            dist = np.sqrt((ortalyk[0] - center[0])**2 + (ortalyk[1] - center[1])**2)
            
            if dist < azarak:
                azarak = dist
                en_jakyn = adam
        
        return en_jakyn or {}
    
    def _cleanup_old(self):
        oshiru = []
        for tid, info in self.tracks.items():
            if info.get('frames_since_update', 0) > 30:
                oshiru.append(tid)
        
        for tid in oshiru:
            del self.tracks[tid]
    
    def get_active_count(self):
        return len(self.tracks)
