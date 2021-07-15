from pyAudioAnalysis import MidTermFeatures as aFm
from pyAudioAnalysis import audioBasicIO as aIO
import moviepy.editor as mp
import numpy as np
import argparse
import json


def get_index(list_dict, vid_name):
    """helper to read the json file."""
    for i in range(len(list_dict)):
        if list_dict['videos'][i]['name'] == vid_name:
            return i


def extract_time_start(video_path, bip_ref_path="ref_bip_isolated.wav", references_path="ref_features_bip.npy"):
    mt = np.load(references_path)
    fs, s_ref = aIO.read_audio_file(bip_ref_path)
    duration = len(s_ref) / float(fs)
    win, step = 0.05, 0.05
    win_mid, step_mid = duration, 0.5

    # extraction on the long signal
    my_clip1 = mp.VideoFileClip(video_path)
    fs = 44100
    s_long = my_clip1.audio.to_soundarray(fps=fs)
    s_long = s_long[:, 0]
    duration_long = len(s_long) / float(fs)

    # extract short-term features using a 50msec non-overlapping windows
    win, step = 0.05, 0.05
    win_mid, step_mid = 0.4, 0.05
    mt_long, st_long, mt_n_long = aFm.mid_feature_extraction(s_long, fs, win_mid * fs, step_mid * fs,
                                                             win * fs, step * fs)

    #normalization
    mt_long = mt_long.T            
    for i in range(len(mt_long)):
        mt_long[i] = mt_long[i]/np.linalg.norm(mt_long[i])

    temps_possible = []
    
    for i in range(len(mt)):
        arg_min_dist = 0
        min_dist = 1000
        for j in range(len(mt_long)):
            if np.linalg.norm(mt[i]-mt_long[j]) < min_dist :
                arg_min_dist = j
                min_dist = np.linalg.norm(mt[i]-mt_long[j])
        temps_possible.append(arg_min_dist * duration_long / mt_long.shape[0])
 
    median_time = np.median(temps_possible)
    temps_possible_non_aberrant = []
    aberration = 0.5
    for i in range(len(temps_possible)):
        if median_time - aberration <= temps_possible[i]:
            if temps_possible[i] <= median_time + aberration :
                temps_possible_non_aberrant.append(temps_possible[i])
    
    if temps_possible_non_aberrant != []:
        # 0.11s de silence avant le bip dans les sons de références
        start = np.median(temps_possible_non_aberrant) + 0.11
    
    else :
    # Erreur
        start = -1
    return start



if __name__ == "__main__":
    # print(extract_time_start('videos/50_brasse_stevens.mp4'))
    parser = argparse.ArgumentParser(description='Parser for automatic start detection.')
    parser.add_argument('--json', help='Path of the json of the race')
    parser.add_argument('--video', help='Path of the video')
    parser.add_argument('--ref', help='Reference to use as the noise for the start.', default='ref_bip_isolated.wav')
    parser.add_argument('--ref_feat', help='Reference features of various sounds in vector of len 136', default='ref_features_bip.npy')
    args = parser.parse_args()
    start_time = extract_time_start(args.video, bip_ref_path=args.ref, references_path=args.ref_feat)

    with open(args.json) as json_file:
        json_course = json.load(json_file)

    name_of_video = args.video.split('/')[-1]
    index_vid = get_index(json_course, name_of_video)
    json_course['videos'][index_vid]['start_moment'] = start_time

    with open(args.json, 'w') as outfile:
        json.dump(json_course, outfile, indent=4)
    # Todo reflechir quels arguments on met : plutot race, json path, video path ou folder, race, video
