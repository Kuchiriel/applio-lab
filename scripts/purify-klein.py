import sys, json, os, glob
import numpy as np
sys.path.insert(0, '/tmp/opencode')
os.environ.setdefault('LD_LIBRARY_PATH', '/nix/store/7vafhlh0lmcvi75jfyy09qwr4m3x1ks3-gcc-15.2.0-lib/lib')
import wespeakerruntime as w
spk = w.Speaker(lang='en')
def emb(f):
    e = np.array(spk.extract_embedding(f), dtype=float).ravel()
    return e/(np.linalg.norm(e)+1e-9)
def cent(files):
    E = np.stack([emb(f) for f in files]); c = E.mean(axis=0); return c/(np.linalg.norm(c)+1e-9)
KLEIN_REFS = ['/home/nixos/Audio/lotm/datasets/klein-v3/'+f for f in os.listdir('/home/nixos/Audio/lotm/datasets/klein-v3') if f.startswith('ref-')]
TOLO_REFS = ['/home/nixos/Audio/lotm/ep4/check-09-unknown.wav','/home/nixos/Audio/lotm/ep4/spk-01.wav','/home/nixos/Audio/lotm/ep5/check-06-unknown.wav']
ck, ct = cent(KLEIN_REFS), cent(TOLO_REFS)
rep = {}
for f in sorted(glob.glob('/home/nixos/Audio/lotm/datasets/klein-v3/ep*.wav')+glob.glob('/home/nixos/Audio/lotm/datasets/klein-v3/klein-limite-*.wav')):
    e = emb(f)
    sk, st = float(e@ck), float(e@ct)
    rep[os.path.basename(f)] = {'klein':round(sk,3),'tolo':round(st,3),'margem':round(sk-st,3)}
amb = {k:v for k,v in rep.items() if v['margem']<0.2}
print('total:',len(rep),'ambiguos (margem<0.2):',len(amb))
for k,v in sorted(amb.items(), key=lambda x:x[1]['margem'])[:15]: print(' ',k,v)
json.dump(rep, open('/tmp/opencode/klein-purify.json','w'))
