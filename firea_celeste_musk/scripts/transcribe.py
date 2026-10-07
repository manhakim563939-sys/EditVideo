import sys, numpy as np, soundfile as sf, sherpa_onnx
d="sherpa-onnx-whisper-turbo/"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=d+"turbo-encoder.int8.onnx", decoder=d+"turbo-decoder.int8.onnx", tokens=d+"turbo-tokens.txt", language="ms", task="transcribe", num_threads=8)
a, sr = sf.read("a16.wav", dtype="float32")
def run(x):
    s = rec.create_stream(); s.accept_waveform(sr, x); rec.decode_stream(s); return s.result.text
print("FULL:", run(a))
# energy envelope to find pauses
hop=160; e=np.array([np.sqrt(np.mean(a[i:i+400]**2)) for i in range(0,len(a)-400,hop)])
db=20*np.log10(e+1e-6)
np.save("env.npy", db)
# choose cut points: local minima in windows every ~2.5-4s
cuts=[0]; t=0
while True:
    lo, hi = cuts[-1]+int(2.2*100), cuts[-1]+int(4.0*100)
    if hi>=len(db): break
    m = lo+int(np.argmin(db[lo:hi])); cuts.append(m)
cuts.append(len(db))
for i in range(len(cuts)-1):
    s0, s1 = cuts[i]*hop, cuts[i+1]*hop
    print(f"[{s0/sr:.2f}-{s1/sr:.2f}] min={db[cuts[i]]:.1f}dB :", run(a[s0:s1]))
