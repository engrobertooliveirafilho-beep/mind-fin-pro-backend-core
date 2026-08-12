from app.mind.p5_6b2_real_cv_pipeline import run_p56b2_healthcheck
from app.mind.p5_6b2_real_cv_pipeline.pipeline import analyze_video_file, composite
import cv2, numpy as np

def test_p56b2_healthcheck():
    assert run_p56b2_healthcheck()["status"]=="P5.6B2_READY"

def test_real_cv_on_synthetic_video(tmp_path):
    p=tmp_path/"synthetic.mp4"
    out=cv2.VideoWriter(str(p),cv2.VideoWriter_fourcc(*"mp4v"),20,(320,240))
    for i in range(40):
        frame=np.zeros((240,320,3),dtype=np.uint8)
        cv2.rectangle(frame,(30+i*4,100+(i%10)*3),(90+i*4,150+(i%10)*3),(255,255,255),-1)
        out.write(frame)
    out.release()
    m=analyze_video_file(p); s=composite(m)
    assert m["frames"]>0
    assert s["biomechanics_score"]>=0
