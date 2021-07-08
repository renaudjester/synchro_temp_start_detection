from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import moviepy.editor as mp

# idée: faire la meme chose mais comparer les deux videos à un signe de début de course pour savoir quand
# est le début de la course

if __name__ == "__main__":
    video1 = "200_4n_dames_finaleA_f122020_droite_lowered.mp4"
    video2 = "ref2.mp4"

    my_clip1 = mp.VideoFileClip("videos/" + video1)
    my_clip2 = mp.VideoFileClip("videos/" +video2)

    my_clip1.audio.write_audiofile(r"wav/" + video1.split('.')[0] + ".wav")
    my_clip2.audio.write_audiofile(r"wav/" + video2.split('.')[0] + ".wav")

    samplerate1, y1 = wavfile.read("wav/" + video1.split('.')[0] + ".wav")
    samplerate2, y2 = wavfile.read("wav/" + video2.split('.')[0] + ".wav")

    print(samplerate2 == samplerate1)
    # size_analysed = len(y1)
    size_analysed = max(len(y1), len(y2))
    y1 = y1[:, 0]
    y2 = y2[:, 0]

    # for noisy data and with a lot of points
    # y1 = y1 - y1.mean()
    # y2 = y2 - y2.mean()
    # y1 = y1 / y1.std()
    # y2 = y2 / y2.std()

    # Calculation of the cross-correlation
    corr = signal.correlate(y1, y2)  # , mode="same")
    time = np.arange(1 - size_analysed, size_analysed)
    shift_calculated = time[corr.argmax()] * 1.0 * (1/samplerate1)
    # if shifted negative then y2 is late of |shifted| otherwise y2 is in advance
    print(shift_calculated)

    # plotting
    x = np.linspace(0, size_analysed/samplerate1, size_analysed)
    plt.plot(x, y1)
    x2 = np.linspace(0, len(y2)/samplerate2,  len(y2)) + 10
    plt.plot(x2, y2)
    plt.show()