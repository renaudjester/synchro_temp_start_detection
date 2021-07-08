from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import moviepy.editor as mp

# idée: faire la meme chose mais comparer les deux videos à un signe de début de course pour savoir quand
# est le début de la course

if __name__ == "__main__":
    # video1 = "50_Brasse_F_S3_gauche_lowered.mp4"  # environ 8 sec
    video1 = "200_4n_dames_finaleA_f122020_gauche_lowered.mp4"  # environ 2.27 sec
    video2 = "ref_bip.mp4"
    my_clip1 = mp.VideoFileClip("videos/"+ video1)
    my_clip2 = mp.VideoFileClip("videos/"+ video2)

    # my_clip1.audio.write_audiofile(r"wav/" + video1.split('.')[0] + ".wav")
    # # my_clip2.audio.write_audiofile(r"wav/" + video2.split('.')[0] + ".wav")

    # samplerate1, y1 = wavfile.read("wav/" + video1.split('.')[0] + ".wav")
    # samplerate2, y2 = wavfile.read("wav/" + video2.split('.')[0] + ".wav")

    samplerate1 = 44100
    samplerate2 = 44100
    y1 = my_clip1.audio.to_soundarray(fps=samplerate1)
    y2 = my_clip2.audio.to_soundarray(fps=samplerate2)
    print(y1.shape)

    print(samplerate2 == samplerate1)
    size_analysed = max(len(y1), len(y2))
    y1 = y1[:size_analysed, 0]
    y2 = y2[0:16000, 0]

    # for noisy data and with a lot of points
    y1 = y1 - y1.mean()
    y2 = y2 - y2.mean()
    y1 = y1 / y1.std()
    y2 = y2 / y2.std()

    # Calculation of the cross-correlation
    ones = np.ones(y2.shape)
    corr_with_one = signal.correlate(y1, ones, mode="same")
    squared = np.square(corr_with_one)
    # mettre au carré
    # diviser corr_normaliser par corr
    corr = signal.correlate(y1, y2, mode="same")
    time = np.arange(1 - size_analysed, size_analysed)
    shift_calculated = time[corr.argmax()] * 1.0 * (1/samplerate1)

    corr2 = np.divide(corr, squared)
    shift_calculated2 = time[corr2.argmax()] * 1.0 * (1 / samplerate1)

    # -2.0833333333333335 -2.2713378684807255 108124 99833
    # -45.521519274376416 -45.147619047619045 108124 124613
    # -141.4681859410431 -97.93848072562359 108124 2027784




    # if shifted negative then y2 is late of |shifted| otherwise y2 is in advance
    print(shift_calculated, shift_calculated2, corr.argmax(), corr2.argmax())
    print(time.shape, corr.shape)
    print(len(y1), len(y2), len(y1)/len(y2))

    # plotting
    x1 = np.linspace(0, len(y1)/samplerate1, len(y1))
    x2 = np.linspace(0, len(y2)/samplerate1, len(y2)) - shift_calculated2
    # plt.plot(x1, y1)
    # plt.plot(x2, y2, '*')
    plt.plot(y2)
    plt.show()
