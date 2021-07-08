# code from
# https://medium.com/behavioral-signals-ai/intro-to-audio-analysis-recognizing-sounds-using-machine-learning-20fd646a0ec5

from pyAudioAnalysis import ShortTermFeatures as aFs
from pyAudioAnalysis import MidTermFeatures as aFm
from pyAudioAnalysis import audioBasicIO as aIO
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly
import wavio


# extraction on the ref
fs, s = aIO.read_audio_file("wav/ref_bip.wav")
s_ref = s[3000:18000, 0]
print(fs, s_ref.shape)
duration = len(s_ref) / float(fs)
print(f'duration = {duration} seconds')

# extract short-term features using a 50msec non-overlapping windows
win, step = 0.05, 0.05
win_mid, step_mid = duration, 0.5
mt_ref, st_ref, mt_n_ref = aFm.mid_feature_extraction(s_ref, fs, win_mid * fs, step_mid * fs,
                                         win * fs, step * fs)
# print(f'signal duration {len(s)/fs} seconds')
# print(f'{st.shape[1]} {st.shape[0]}-D short-term feature vectors extracted')
# print(f'{mt.shape[1]} {mt.shape[0]}-D segment feature statistic vectors extracted')
# print('mid-term feature names')
# for i, mi in enumerate(mt_n):
#     print(f'{i}:{mi}')

# extraction on the long signal
audio_to_analyse = "50_brasse_stevens.wav"
# fs, s_long = aIO.read_audio_file("wav/200_4n_dames_finaleA_f122020_gauche_lowered.wav") # 1.9
# fs, s_long = aIO.read_audio_file("wav/50_dos_dames_finaleA_f122020_gauche_lowered.wav") # 6
fs, s_long = aIO.read_audio_file("wav/" + audio_to_analyse)
s = s_long[:, 0]
print(fs, s.shape)
duration_long = len(s) / float(fs)
print(f'duration = {duration_long} seconds')

# extract short-term features using a 50msec non-overlapping windows
win, step = 0.05, 0.05
win_mid, step_mid = 0.4, 0.05
mt_long, st_long, mt_n_long = aFm.mid_feature_extraction(s, fs, win_mid * fs, step_mid * fs,
                                         win * fs, step * fs)

distances = np.linalg.norm(mt_long - mt_ref, axis=0)
tps_bip = np.argmin(distances)*duration_long / mt_long.shape[1]
print(np.argmin(distances))
print(tps_bip)
plt.plot(distances)
plt.show()


wavio.write("resultats/ref_bip.wav", s_ref, fs)
index_start_fen = round((tps_bip - 0.5) * fs)
index_end_fen = round((tps_bip + 0.5) * fs)
index_start = round(tps_bip * fs)
index_end = round((tps_bip + win_mid) * fs)
resultats_around = s[index_start_fen:index_end_fen]
resultats_exact = s[index_start:index_end]
wavio.write("resultats/" + 'around_' + audio_to_analyse, resultats_around, fs, sampwidth=1)
wavio.write("resultats/" + 'exact_' + audio_to_analyse, resultats_exact, fs, sampwidth=1)