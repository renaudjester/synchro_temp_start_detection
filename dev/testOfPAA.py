from pyAudioAnalysis import ShortTermFeatures as aFs
from pyAudioAnalysis import MidTermFeatures as aFm
from pyAudioAnalysis import audioBasicIO as aIO
import numpy as np
import plotly.graph_objs as go
import plotly
import IPython

fs, s = aIO.read_audio_file("wav/ref_bip.wav")
s = s[:18000, 0]
# fs, s = aIO.read_audio_file("wav/200_4n_dames_finaleA_f122020_gauche_lowered.wav")
# s = s[:, 0]
print(fs, s.shape)


# # play the initial and the generated files in notebook:
# IPython.display.display(IPython.display.Audio("wav/ref_bip.wav"))

# print duration in seconds:
duration = len(s) / float(fs)
print(f'duration = {duration} seconds')

# extract short-term features using a 50msec non-overlapping windows
win, step = 0.050, 0.050
[f, fn] = aFs.feature_extraction(s, fs, int(fs * win),
                                int(fs * step))
print(f'{f.shape[1]} frames, {f.shape[0]} short-term features')
print('Feature names:')
for i, nam in enumerate(fn):
    print(f'{i}:{nam}')
# plot short-term energy
# create time axis in seconds
time = np.arange(0, duration - step, win)
# get the feature whose name is 'energy'
energy = f[fn.index('energy'), :]
mylayout = go.Layout(yaxis=dict(title="frame energy value"),
                     xaxis=dict(title="time (sec)"))
plotly.offline.iplot(go.Figure(data=[go.Scatter(x=time,
                                                y=energy)],
                               layout=mylayout))


# get mid-term (segment) feature statistics
# and respective short-term features:
mt, st, mt_n = aFm.mid_feature_extraction(s, fs, 1 * fs, 1 * fs,
                                         0.05 * fs, 0.05 * fs)
print(f'signal duration {len(s)/fs} seconds')
print(f'{st.shape[1]} {st.shape[0]}-D short-term feature vectors extracted')
print(f'{mt.shape[1]} {mt.shape[0]}-D segment feature statistic vectors extracted')
print('mid-term feature names')
for i, mi in enumerate(mt_n):
    print(f'{i}:{mi}')
