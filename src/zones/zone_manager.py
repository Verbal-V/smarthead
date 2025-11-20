import json
import cv2
import numpy as np
from typing import List, Dict, Tuple
from src.utils.config import Settings

class ZoneGuard:
    def __init__(self):
        self.aumaqtar = []            
        self.tuzetu_rejim = False       
        self.agymdy_nukteler = []       
        self._load_zones()
    
    def _load_zones(self):
        try:
            with open(Settings.ZONES_FILE, 'r') as f:
                data = json.load(f)
                self.aumaqtar = data.get('zones', [])
        except FileNotFoundError:
            self.aumaqtar = []
            self._save_zones()
        except Exception as qate:
            print(f"Zone load error: {qate}")
            self.aumaqtar = []
    
    def _save_zones(self):
        try:
            data = {
                'zones': self.aumaqtar,
                'description': 'Restricted zones'
            }
            
            with open(Settings.ZONES_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as qate:
            print(f"Zone save error: {qate}")
    
    def add_zone(self, nukteler):
        if len(nukteler) < 3:
            return False
        
        aumaq = {
            'id': len(self.aumaqtar) + 1,
            'points': nukteler,
            'name': f'Aumaq_{len(self.aumaqtar) + 1}'
        }
        
        self.aumaqtar.append(aumaq)
        return True
    
    def finish_current_zone(self):
        if len(self.agymdy_nukteler) >= 3:
            self.add_zone(self.agymdy_nukteler)
            self._save_zones()
        self.agymdy_nukteler = []
    
    def is_intrusion(self, adamdar):
        for adam in adamdar:
            if self._is_person_in_zone(adam):
                return True
        return False
    
    def _is_person_in_zone(self, adam):
        ortalyk = adam['center']
        
        for aumaq in self.aumaqtar:
            if self._point_in_polygon(ortalyk, aumaq['points']):
                return True
        
        return False
    
    def _point_in_polygon(self, nuqte, polygon):
        x, y = nuqte
        n = len(polygon)
        ishinde = False   
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            kesu = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= kesu:
                            ishinde = not ishinde
            p1x, p1y = p2x, p2y
        
        return ishinde
    
    def draw_zones(self, frame):
        natizhe = frame.copy()
        
        for aumaq in self.aumaqtar:
            pts = np.array(aumaq['points'], np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            kabat = natizhe.copy()
            cv2.fillPoly(kabat, [pts], (255, 0, 0))
            cv2.addWeighted(kabat, 0.2, natizhe, 0.8, 0, natizhe)
            
            cv2.polylines(natizhe, [pts], True, Settings.ZONE_COLOR, Settings.ZONE_THICKNESS)
            
            if len(aumaq['points']) > 0:
                cx = sum(p[0] for p in aumaq['points']) // len(aumaq['points'])
                cy = sum(p[1] for p in aumaq['points']) // len(aumaq['points'])
                cv2.putText(
                    natizhe, 
                    aumaq['name'], 
                    (cx - 20, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    Settings.ZONE_COLOR, 2
                )
        
        return natizhe
    
    def start_editing(self):
        self.tuzetu_rejim = True
        self.agymdy_nukteler = []
    
    def stop_editing(self):
        self.tuzetu_rejim = False
        self.agymdy_nukteler = []
    
    def add_point(self, n):
        if self.tuzetu_rejim:
            self.agymdy_nukteler.append(n)
    
    def get_count(self):
        return len(self.aumaqtar)
