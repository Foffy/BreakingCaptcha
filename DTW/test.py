import dtw

sound = '../Sounds/known/1/1_0.wav'
d = '../Sounds/known'
dd = dtw.k_nearest(sound, d, 5)
print dd
