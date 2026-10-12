import subprocess
# name, image, duration, zoom start, zoom end, pan (x frac, y frac targets)
S=[('s03',  'kf/s03_1.png', 4.0, 1.00,1.10,(0.55,0.45)),
   ('s05a', 'kf/s05_2.png', 4.1, 1.12,1.02,(0.5,0.4)),
   ('s05b', 'kf/s05_1.png', 4.4, 1.00,1.10,(0.5,0.35)),
   ('s09',  'kf/s09_1.png', 5.0, 1.00,1.12,(0.5,0.4)),
   ('s10',  'kf/s10_2.png', 6.4, 1.00,1.08,(0.5,0.42)),
   ('s11',  'kf/s11_2.png', 1.7, 1.04,1.10,(0.5,0.4)),
   ('s15',  'kf/s15_2.png', 4.2, 1.00,1.10,(0.5,0.35)),
   ('end',  'kf/hook_frame0.png', 5.6, 1.00,1.00,(0.5,0.4)),]
fps=30
for name,img,dur,z0,z1,(px,py) in S:
    n=round(dur*fps)
    z=f"{z0}+({z1}-{z0})*on/{n-1}"
    vf=(f"scale=2160:3840,zoompan=z='{z}':x='(iw-iw/zoom)*{px}':y='(ih-ih/zoom)*{py}':d={n}:s=1080x1920:fps={fps},"
        f"format=yuv420p")
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',img,'-vf',vf,'-frames:v',str(n),'-c:v','libx264','-crf','16','-preset','medium',f'build/seg/{name}.mp4'],check=True)
    print('done',name,n)
