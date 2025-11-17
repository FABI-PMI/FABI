import sys, time, queue, warnings
from collections import deque
import numpy as np
import sounddevice as sd

warnings.filterwarnings("ignore")

# ===== Configuración =====
OUTPUT_DEVICE_INDEX = 18   # índice de 'Mezcla estéreo'
SR = 48000
PRINT_INTERVAL = 1.0
WINDOW_SEC = 10.0
WARMUP_SEC = 2.0
ENV_WIN_SEC = 0.06
PROC_FS = 200
BPM_MIN, BPM_MAX = 40, 300
SMOOTH_N = 3

# Puerta de silencio (último segundo)
SILENCE_RMS  = 0.0010
SILENCE_PEAK = 0.01
SILENCE_LAST_SEC = 1.0
RESET_ON_SILENCE = True
# ==========================

q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    x = indata if indata.ndim == 1 else np.mean(indata, axis=1)
    q.put(x.astype(np.float32, copy=True))

def moving_rms(x, n):
    if n <= 1:
        return np.sqrt(np.maximum(np.mean(x**2), 1e-12)) * np.ones_like(x)
    w = np.ones(n, dtype=np.float32) / n
    y = np.convolve(x.astype(np.float32)**2, w, mode='same')
    return np.sqrt(np.maximum(y, 1e-12))

def downsample(x, src_fs, dst_fs):
    step = max(1, int(round(src_fs / float(dst_fs))))
    return x[::step]

def autocorr(x):
    x = x.astype(np.float32)
    x = x - np.mean(x)
    s = np.std(x) + 1e-9
    if s <= 1e-8 or len(x) < 32:
        return None
    x = x / s
    ac = np.correlate(x, x, mode='full')
    ac = ac[len(ac)//2:]
    ac[0] = 0.0
    return ac

def lag_from_bpm(bpm, fs_env):
    return int(round(fs_env * 60.0 / float(bpm)))

def bpm_from_lag(L, fs_env):
    return fs_env * 60.0 / float(L)

def comb_score(ac, L, harmonics=(1,2,3,4)):
    if L < 1: return -1.0
    total = 0.0
    for k in harmonics:
        idx = k * L
        if idx <= 1 or idx >= len(ac): break
        a = max(1, idx-2); b = min(len(ac)-1, idx+2)
        total += float(np.max(ac[a:b+1])) / (k**0.5)
    return total

def estimate_bpm_from_audio(y):
    env = moving_rms(y, int(max(1, ENV_WIN_SEC * SR)))
    env = env / (np.max(np.abs(env)) + 1e-9)
    env_ds = downsample(env, SR, PROC_FS)

    ac = autocorr(env_ds)
    if ac is None: return None

    Lmin = max(1, lag_from_bpm(BPM_MAX, PROC_FS))
    Lmax = min(len(ac)-1, lag_from_bpm(BPM_MIN, PROC_FS))
    if Lmax <= Lmin: return None

    L0 = Lmin + int(np.argmax(ac[Lmin:Lmax+1]))
    cands = set(max(1, min(len(ac)-1, L0+d)) for d in (-2,-1,0,1,2))

    best = (-1.0, None)
    for L in sorted(cands):
        for k in (1,2,3,4):
            Lk = max(1, int(round(L / k)))
            bpm = bpm_from_lag(Lk, PROC_FS)
            if not (BPM_MIN <= bpm <= BPM_MAX):
                continue
            sc = comb_score(ac, Lk)
            if sc > best[0]:
                best = (sc, bpm)
    return float(best[1]) if best[1] is not None else None

def main():
    dev = sd.query_devices(OUTPUT_DEVICE_INDEX)
    in_ch = max(1, min(2, dev['max_input_channels']))
    sd.default.device = (OUTPUT_DEVICE_INDEX, None)
    sd.default.samplerate = SR

    window_samples = int(WINDOW_SEC * SR)
    warmup_samples = int(WARMUP_SEC * SR)
    silence_tail = int(SILENCE_LAST_SEC * SR)

    ring = deque(maxlen=window_samples)
    last_bpms = deque(maxlen=SMOOTH_N)
    last_print = None
    next_tick = time.time() + PRINT_INTERVAL

    with sd.InputStream(device=OUTPUT_DEVICE_INDEX, channels=in_ch,
                        samplerate=SR, dtype='float32',
                        blocksize=0, callback=audio_callback):
        while True:
            while time.time() < next_tick:
                try:
                    data = q.get(timeout=0.02)
                    if data.ndim > 1: data = np.mean(data, axis=1)
                    ring.extend(data.astype(np.float32, copy=False))
                except queue.Empty:
                    pass

            bpm_to_print = last_print
            if len(ring) >= warmup_samples:
                y = np.asarray(ring, dtype=np.float32)
                tail = y[-silence_tail:] if len(y) >= silence_tail else y
                rms_tail = float(np.sqrt(np.mean(tail**2))) if len(tail) else 0.0
                peak_tail = float(np.max(np.abs(tail))) if len(tail) else 0.0

                if (rms_tail < SILENCE_RMS) and (peak_tail < SILENCE_PEAK):
                    if RESET_ON_SILENCE:
                        last_bpms.clear()
                        last_print = None
                        ring = deque(tail, maxlen=window_samples)
                    bpm_to_print = 0.0
                else:
                    bpm_new = estimate_bpm_from_audio(y)
                    if bpm_new is not None:
                        last_bpms.append(bpm_new)
                        bpm_to_print = float(np.median(last_bpms))
                        last_print = bpm_to_print
                    elif last_print is None:
                        bpm_to_print = 0.0

            print(f"{0.0:.1f}" if bpm_to_print is None else f"{bpm_to_print:.1f}")
            sys.stdout.flush()
            next_tick += PRINT_INTERVAL
            
# --- NUEVO: medición rápida de BPM (snapshot) ---
def get_bpm_snapshot(duration_sec=4.0):
    """
    Abre una InputStream por unos segundos y devuelve el BPM mediano detectado.
    Si hay silencio o no se logra medir, devuelve 0.0.
    """
    import numpy as np, time
    from collections import deque
    import sounddevice as sd

    dev = sd.query_devices(OUTPUT_DEVICE_INDEX)
    in_ch = max(1, min(2, dev['max_input_channels']))
    sd.default.device = (OUTPUT_DEVICE_INDEX, None)
    sd.default.samplerate = SR

    ring = deque(maxlen=int(WINDOW_SEC * SR))
    last_bpms = deque(maxlen=SMOOTH_N)

    start = time.time()
    def _cb(indata, frames, time_info, status):
        x = indata if indata.ndim == 1 else np.mean(indata, axis=1)
        ring.extend(x.astype(np.float32, copy=False))

    with sd.InputStream(device=OUTPUT_DEVICE_INDEX, channels=in_ch,
                        samplerate=SR, dtype='float32',
                        blocksize=0, callback=_cb):
        while time.time() - start < duration_sec:
            time.sleep(0.05)

    if len(ring) < int(WARMUP_SEC * SR):
        return 0.0

    y = np.asarray(ring, dtype=np.float32)
    ac = autocorr(downsample(moving_rms(y, int(max(1, ENV_WIN_SEC * SR))), SR, PROC_FS))
    if ac is None:
        return 0.0

    Lmin = max(1, lag_from_bpm(BPM_MAX, PROC_FS))
    Lmax = min(len(ac)-1, lag_from_bpm(BPM_MIN, PROC_FS))
    if Lmax <= Lmin:
        return 0.0

    L0 = Lmin + int(np.argmax(ac[Lmin:Lmax+1]))
    cands = set(max(1, min(len(ac)-1, L0+d)) for d in (-2,-1,0,1,2))

    best = (-1.0, None)
    for L in sorted(cands):
        for k in (1,2,3,4):
            Lk = max(1, int(round(L / k)))
            bpm = bpm_from_lag(Lk, PROC_FS)
            if not (BPM_MIN <= bpm <= BPM_MAX):
                continue
            sc = comb_score(ac, Lk)
            if sc > best[0]:
                best = (sc, bpm)
    return float(best[1]) if best[1] is not None else 0.0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
