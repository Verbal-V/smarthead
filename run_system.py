import os
import sys
from pathlib import Path

def tabu_videolar():
    video_qaltasy = Path("data/videos")
    
    if not video_qaltasy.exists():
        print("Video qalta tabylmady")
        return []
    
    keneytu = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    videolar = []
    
    for ext in keneytu:
        videolar.extend(video_qaltasy.glob(f"*{ext}"))
        videolar.extend(video_qaltasy.glob(f"*{ext.upper()}"))
    
    return sorted(videolar)

def main():
    print("Qauipsizdik Zhuyesi")
    print("=" * 30)
    
    videolar = tabu_videolar()
    
    if not videolar:
        print("data/videos/ ishinde video joq")
        print("Video file tasta da qayta jurgiz")
        return
    
    print(f"Tabyldy: {len(videolar)} video:")
    
    for i, vid in enumerate(videolar, 1):
        print(f"  {i}. {vid.name}")
    
    if len(videolar) == 1:
        tandalgany = videolar[0]
        print(f"\nAvto-tandau: {tandalgany.name}")
    else:
        while True:
            try:
                tandau = input(f"\nVideo tandau (1-{len(videolar)}): ")
                idx = int(tandau) - 1
                if 0 <= idx < len(videolar):
                    tandalgany = videolar[idx]
                    break
                else:
                    print("Qate nomer")
            except ValueError:
                print("San engiz")
    
    aumaq_fayl = Path("restricted_zones.json")
    if not aumaq_fayl.exists():
        print("Aumaq fayly tabylmady")
        quramyz_ba = input("Test aumaq qosu? (y/n): ").lower()
        if quramyz_ba == 'y':
            create_test_zone()
        else:
            return
    
    print(f"\nBastalady: {tandalgany.name}")
    
    try:
        from main import WatchDog
        
        juyse = WatchDog()
        juyse.run(str(tandalgany))
        
    except KeyboardInterrupt:
        print("\nQoldan toqtatty")
    except Exception as qate:
        print(f"Qate: {qate}")

def create_test_zone():
    import json
    
    aumaqtar = {
        "zones": [
            {
                "id": 1,
                "name": "Restricted",
                "points": [[400, 200], [800, 200], [800, 500], [400, 500]]
            }
        ]
    }
    
    with open("restricted_zones.json", 'w') as f:
        json.dump(aumaqtar, f, indent=2)
    
    print("Test aumaq qosyldy")

if __name__ == "__main__":
    main()
