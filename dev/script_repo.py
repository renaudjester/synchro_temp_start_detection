from scipy.io import wavfile
from scipy import signal
import numpy as np
import moviepy.editor as mp
import json


def get_index(list_dict, vid_name):
    for i in range(len(list_dict)):
        if list_dict[i]['name'] == vid_name:
            return i


def get_video_from_type(list_dict, type_video):
    """type is the type of video: fixeGauche ou fixeDroite"""
    for i in range(len(list_dict)):
        if list_dict[i]['type_video'] == type_video:
            return i


def analyse(course_path, video1, video2,  json_name):
    """Script for the analysis of the time between two videos of the same event."""
    my_clip1 = mp.VideoFileClip(course_path + video1)
    my_clip2 = mp.VideoFileClip(course_path + video2)

    # my_clip1.audio.write_audiofile(course_path + video1.split('.')[0] + ".wav")
    # my_clip2.audio.write_audiofile(course_path + video2.split('.')[0] + ".wav")
    #
    # samplerate1, y1 = wavfile.read(course_path + video1.split('.')[0] + ".wav")
    # samplerate2, y2 = wavfile.read(course_path + video2.split('.')[0] + ".wav")

    samplerate1 = 44100
    samplerate2 = 44100
    y1 = my_clip1.audio.to_soundarray(fps=samplerate1)
    y2 = my_clip2.audio.to_soundarray(fps=samplerate2)

    print("Sample rates are the same :", samplerate2 == samplerate1)
    size_analysed = min(len(y1), len(y2))
    y1 = y1[:size_analysed, 0]
    y2 = y2[:size_analysed, 0]

    # for noisy data and with a lot of points
    y1 = y1 - y1.mean()
    y2 = y2 - y2.mean()
    y1 = y1 / y1.std()
    y2 = y2 / y2.std()

    # Calculation of the cross-correlation
    corr = signal.correlate(y1, y2)  # , mode="same")
    time = np.arange(1 - size_analysed, size_analysed)
    shift_calculated = time[corr.argmax()] * 1.0 * (1/samplerate1)
    print(shift_calculated)

    # modification of the json to add the information
    with open(course_path + json_name) as json_file:
        json_course = json.load(json_file)
    # if shifted negative then y2 is late of |shifted| otherwise y2 is in advance
    json_course['videos'][get_index(json_course['videos'], video1)]['time_shifted'] = - shift_calculated
    json_course['videos'][get_index(json_course['videos'], video2)]['time_shifted'] = shift_calculated

    with open(course_path + json_name, 'w') as outfile:
        json.dump(json_course, outfile)


# if __name__ == "__main__":
#     video1 = "100_nl_dames_finaleA_f122020_gauche_lowered.mp4"
#     video2 = "100_nl_dames_finaleA_f122020_droite_lowered.mp4"
#     analyse("videos/", video1, video2, "")

    # 50 brasse : ~ -7
    # 100nl : ~ -18


