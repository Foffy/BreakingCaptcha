import dtw

sound = "../Sounds/unknown/one.wav"
d = "../Sounds/known"
dd = dtw.k_nearest(sound, d, 5)
print(dd)
