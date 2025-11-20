import cv2
import time
from src.detectors.yolo_detector import PersonFinder
from src.zones.zone_manager import ZoneGuard
from src.trackers.deepsort_tracker import PersonTracker

class WatchDog:
    def __init__(self):
        self.tabys = PersonFinder()         
        self.aumaqtar = ZoneGuard()        
        self.qadaq = PersonTracker()         
        self.cap = None
        self.dabyl = False                  
        self.dabyl_time = 0
        
        self.buzghan_tarikh = {}            
        self.min_kadr = 3                   
        
        self.fps_sanau = 0                  
        self.fps_bastau = time.time()       
        self.agi_fps = 0                    
    
    def _update_fps(self):
        self.fps_sanau += 1
        if time.time() - self.fps_bastau >= 1.0:
            self.agi_fps = self.fps_sanau / (time.time() - self.fps_bastau)
            self.fps_sanau = 0
            self.fps_bastau = time.time()
    
    def load_video(self, path):
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")
    
    def process_frame(self, frame):
        adamdar = self.tabys.find_people(frame)
        baqylanatyn = self.qadaq.update(adamdar, frame)
        
        buzylu = self._tekseru_buzylu(baqylanatyn)
        self._dabyl_baskaru(buzylu)
        
        natizhe = self.aumaqtar.draw_zones(frame)
        natizhe = self._suret_baqylau(natizhe, baqylanatyn)
        natizhe = self._statistika_suret(natizhe, baqylanatyn)
        
        if self.dabyl:
            cv2.putText(natizhe, "DABYL!", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
        
        return natizhe
    
    def _tekseru_buzylu(self, adamdar):
        buzghan = set()
        
        for adam in adamdar:
            tid = adam.get('track_id')
            if tid is None:
                continue
            
            if self.aumaqtar._is_person_in_zone(adam):
                buzghan.add(tid)
        
        for tid in buzghan:
            if tid not in self.buzghan_tarikh:
                self.buzghan_tarikh[tid] = 1
            else:
                self.buzghan_tarikh[tid] += 1
        
        ketken = []
        for tid in self.buzghan_tarikh:
            if tid not in buzghan:
                ketken.append(tid)
        
        for tid in ketken:
            del self.buzghan_tarikh[tid]
        
        rast = [tid for tid, san in self.buzghan_tarikh.items() if san >= self.min_kadr]
        
        return len(rast) > 0
    
    def _dabyl_baskaru(self, buzylu):
        qazir = time.time()
        
        if buzylu:
            self.dabyl = True
            self.dabyl_time = qazir
            if not hasattr(self, 'dabyl_berilgen') or not self.dabyl_berilgen:
                print("DABYL! Buzylu anyqtaldy!")
                self.dabyl_berilgen = True
        else:
            if self.dabyl and (qazir - self.dabyl_time) > 3:
                self.dabyl = False
                self.dabyl_berilgen = False
    
    def _suret_baqylau(self, frame, adamdar):
        for adam in adamdar:
            x1, y1, x2, y2 = adam['bbox']
            tid = adam.get('track_id', 'belgisiz')
            senim = adam['confidence']
            
            tid_san = tid if isinstance(tid, int) else hash(str(tid)) % 1000
            tus = (
                (tid_san * 123) % 256,
                (tid_san * 456) % 256,
                (tid_san * 789) % 256
            )
            
            buzylu_ma = self.aumaqtar._is_person_in_zone(adam)
            
            if buzylu_ma:
                tus = (0, 0, 255)
                qalyn = 3
            else:
                qalyn = 2
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), tus, qalyn)
            
            belgi = f"ID:{tid} {senim:.2f}"
            
            if buzylu_ma:
                san = self.buzghan_tarikh.get(tid, 0)
                belgi += f" ESKERTU({san})"
            
            belgi_olch = cv2.getTextSize(belgi, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, 
                         (x1, y1 - belgi_olch[1] - 10),
                         (x1 + belgi_olch[0], y1),
                         tus, -1)
            
            cv2.putText(frame, belgi, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            ortalyk = adam['center']
            cv2.circle(frame, ortalyk, 3, tus, -1)
        
        return frame
    
    def _statistika_suret(self, frame, adamdar):
        self._update_fps()
        
        bar = len(adamdar)
        buzylu = sum(1 for a in adamdar if self.aumaqtar._is_person_in_zone(a))
        izder_sany = self.qadaq.get_active_count()
        
        stats = [
            f"Adamdar: {bar}",
            f"Buzylu: {buzylu}",
            f"Izder: {izder_sany}",
            f"FPS: {self.agi_fps:.1f}"
        ]
        
        cv2.rectangle(frame, (10, 10), (250, 90), (0, 0, 0), -1)
        
        for i, txt in enumerate(stats):
            cv2.putText(frame, txt, (20, 30 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def run(self, video_path):
        try:
            self.load_video(video_path)
            self.aumaqtar._load_zones()
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                processed = self.process_frame(frame)
                cv2.imshow('Qauipsizdik Zhuyesi', processed)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as qate:
            print(f"Qate: {qate}")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()

def main():
    juyse = WatchDog()
    juyse.run("data/videos/test_video.mp4")

if __name__ == "__main__":
    main()
