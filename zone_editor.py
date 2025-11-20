import cv2
import numpy as np
from src.zones.zone_manager import ZoneGuard

class ZoneMaker:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = None
        self.qorghan = ZoneGuard()      # zones → qorghan (типа "охрана")
        self.current_frame = None
        self.tyshqan_x, self.tyshqan_y = 0, 0   # mouse_x, mouse_y
        
        self.qorghan._load_zones()
        
        print("Aumaq Redaktory")
        print("Nusqaular:")
        print("  1: Aumaq tuzetu rejimi on/off")
        print("  Left click: Nuqte qosu")
        print("  Right click: Agyndagy aumaqty ayaqtau")
        print("  d: Songy aumaqty oshiru")
        print("  s: Saqtap shygu")
        print("  q: Shygu (saqtamaisyz)")
        print("  Space: Paıza/Resume video")
    
    def load_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {self.video_path}")
    
    def mouse_click(self, event, x, y, flags, param):
        self.tyshqan_x, self.tyshqan_y = x, y
        
        if event == cv2.EVENT_LBUTTONDOWN and self.qorghan.tuzetu_rejim:
            self.qorghan.add_point((x, y))
            
        elif event == cv2.EVENT_RBUTTONDOWN and self.qorghan.tuzetu_rejim:
            if len(self.qorghan.agymdy_nukteler) >= 3:
                self.qorghan.finish_current_zone()
                self.qorghan.start_editing()
    
    def draw_current_zone(self, frame):
        if self.qorghan.tuzetu_rejim and len(self.qorghan.agymdy_nukteler) > 0:
            nukteler = self.qorghan.agymdy_nukteler.copy()
            nukteler.append((self.tyshqan_x, self.tyshqan_y))
            
            for i in range(len(nukteler) - 1):
                cv2.line(frame, nukteler[i], nukteler[i + 1], (0, 255, 255), 2)
            
            for nuqte in nukteler[:-1]:
                cv2.circle(frame, nuqte, 5, (0, 255, 0), -1)
            
            cv2.circle(frame, (self.tyshqan_x, self.tyshqan_y), 5, (0, 0, 255), -1)
    
    def run(self):
        try:
            self.load_video()
            
            cv2.namedWindow('Aumaq Redaktory')
            cv2.setMouseCallback('Aumaq Redaktory', self.mouse_click)
            
            pause = False
            
            while True:
                if not pause:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    self.current_frame = frame.copy()
                else:
                    frame = self.current_frame.copy()
                
                frame = self.qorghan.draw_zones(frame)
                self.draw_current_zone(frame)
                
                mode = "TUZETU" if self.qorghan.tuzetu_rejim else "KARAU"
                cv2.putText(frame, f"Rejim: {mode}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv_san = self.qorghan.get_count()
                cv2.putText(frame, f"Aumaqtar: {cv_san}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Aumaq Redaktory', frame)
                
                key = cv2.waitKey(30) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.qorghan._save_zones()
                    break
                elif key == ord('1'):
                    if self.qorghan.tuzetu_rejim:
                        self.qorghan.stop_editing()
                    else:
                        self.qorghan.start_editing()
                elif key == ord('d'):
                    if len(self.qorghan.aumaqtar) > 0:
                        del self.qorghan.aumaqtar[-1]
                elif key == ord(' '):
                    pause = not pause
                elif key == 27:  # Esc
                    if self.qorghan.tuzetu_rejim:
                        self.qorghan.stop_editing()
                    else:
                        break
                        
        except Exception as qate:
            print(f"Qate: {qate}")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Paydalanу: python zone_editor.py <video_path>")
        return
    
    beyne_joly = sys.argv[1]
    redaktor = ZoneMaker(beyne_joly)
    redaktor.run()

if __name__ == "__main__":
    main()
