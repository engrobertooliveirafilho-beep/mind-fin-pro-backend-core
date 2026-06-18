import cv2, numpy as np
from pathlib import Path

VIDEO_DIR = Path("runtime/p56b2_videos")

def analyze_video_file(path):
    cap=cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"video_not_opened: {path}")
    fps=cap.get(cv2.CAP_PROP_FPS) or 30
    prev=None; motions=[]; centers=[]; frames=0
    while True:
        ok,frame=cap.read()
        if not ok: break
        frames+=1
        gray=cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        if prev is not None:
            diff=cv2.absdiff(prev,gray)
            _,th=cv2.threshold(diff,25,255,cv2.THRESH_BINARY)
            cnts,_=cv2.findContours(th,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            if cnts:
                c=max(cnts,key=cv2.contourArea); area=cv2.contourArea(c)
                if area>500:
                    x,y,w,h=cv2.boundingRect(c)
                    centers.append((x+w/2,y+h/2,w,h,area))
                    motions.append(float(np.mean(diff)))
        prev=gray
    cap.release()
    if not centers:
        return {"frames":frames,"fps":fps,"duration_seconds":frames/fps if fps else 0,"jump_height":0,"jump_length":0,"horizontal_velocity":0,"vertical_velocity":0,"acceleration":0,"initial_explosion":0,"air_time":0,"kick_frequency":0,"kick_amplitude":0,"direction_changes":0,"angular_velocity":0,"estimated_torque":0,"estimated_kinetic_energy":0,"estimated_power":0,"unpredictability":0,"sporting_aggressiveness":0,"consistency":0,"difficulty":0}
    xs=np.array([c[0] for c in centers]); ys=np.array([c[1] for c in centers]); hs=np.array([c[3] for c in centers]); areas=np.array([c[4] for c in centers]); motion=np.array(motions) if motions else np.array([0])
    dx=np.diff(xs) if len(xs)>1 else np.array([0]); dy=np.diff(ys) if len(ys)>1 else np.array([0]); speed=np.sqrt(dx*dx+dy*dy)
    direction_changes=int(np.sum(np.abs(np.diff(np.sign(dx)))>0)) if len(dx)>2 else 0
    jump_height=float(max(0,np.percentile(ys,90)-np.percentile(ys,10)))
    jump_length=float(max(0,np.percentile(xs,90)-np.percentile(xs,10)))
    horizontal_velocity=float(np.mean(np.abs(dx))*fps) if len(dx) else 0
    vertical_velocity=float(np.mean(np.abs(dy))*fps) if len(dy) else 0
    acceleration=float(np.std(speed)*fps) if len(speed) else 0
    initial_explosion=float(np.percentile(motion[:max(1,len(motion)//5)],90)) if len(motion) else 0
    air_time=float(np.sum(ys < np.percentile(ys,25))/fps)
    kick_frequency=float(np.std(hs))
    kick_amplitude=float(np.percentile(hs,90)-np.percentile(hs,10))
    angular_velocity=float(direction_changes/max((frames/fps),1))
    estimated_torque=float(np.mean(areas)*angular_velocity/1000)
    estimated_kinetic_energy=float(np.mean(speed*speed) if len(speed) else 0)
    estimated_power=float(estimated_kinetic_energy/max((frames/fps),1))
    unpredictability=float(min(100,direction_changes*8+np.std(speed)))
    sporting_aggressiveness=float(min(100,np.percentile(motion,90)))
    consistency=float(max(0,100-np.std(speed)))
    difficulty=float(min(100,(unpredictability*.35)+(sporting_aggressiveness*.35)+(vertical_velocity/20)+(direction_changes*2)))
    return {"frames":frames,"fps":fps,"duration_seconds":frames/fps if fps else 0,"jump_height":jump_height,"jump_length":jump_length,"horizontal_velocity":horizontal_velocity,"vertical_velocity":vertical_velocity,"acceleration":acceleration,"initial_explosion":initial_explosion,"air_time":air_time,"kick_frequency":kick_frequency,"kick_amplitude":kick_amplitude,"direction_changes":direction_changes,"angular_velocity":angular_velocity,"estimated_torque":estimated_torque,"estimated_kinetic_energy":estimated_kinetic_energy,"estimated_power":estimated_power,"unpredictability":unpredictability,"sporting_aggressiveness":sporting_aggressiveness,"consistency":consistency,"difficulty":difficulty}

def composite(metrics):
    keys=["jump_height","jump_length","horizontal_velocity","vertical_velocity","acceleration","initial_explosion","kick_frequency","kick_amplitude","unpredictability","sporting_aggressiveness","difficulty"]
    vals=[min(100,float(metrics.get(k) or 0)) for k in keys]
    bio=round(sum(vals)/len(vals),4) if vals else 0
    return {"biomechanics_score":bio,"buckoff_pressure_score":round((min(100,metrics["initial_explosion"])+min(100,metrics["unpredictability"])+min(100,metrics["difficulty"]))/3,4),"explosiveness_score":round(min(100,metrics["initial_explosion"]),4),"spin_score":round(min(100,metrics["angular_velocity"]*10),4),"kick_score":round(min(100,(metrics["kick_frequency"]+metrics["kick_amplitude"])/2),4),"difficulty_score":round(min(100,metrics["difficulty"]),4),"consistency_score":round(min(100,metrics["consistency"]),4)}

class RealCVPipeline:
    def run_local_folder(self):
        VIDEO_DIR.mkdir(parents=True,exist_ok=True)
        results=[]
        for p in VIDEO_DIR.glob("*"):
            if p.suffix.lower() not in [".mp4",".mov",".avi",".mkv"]: continue
            m=analyze_video_file(p); s=composite(m)
            results.append({"file":str(p),"metrics":m,"scores":s,"model_version":"P5.6B2.opencv_motion.v1"})
        return {"status":"P5.6B2_REAL_CV_DONE","videos_processed":len(results),"results":results}
