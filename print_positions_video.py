import cv2
import numpy as np
import pandas as pd
import argparse
import json


def get_index(list_dict, vid_name):
    """helper to read the json file."""
    index = -1
    for i in range(len(list_dict)):
        if list_dict[i]['name'] == vid_name:
            index = i
    return index


def display_positions(video, start_time, positions, save_path, start_side_vid, one_is_up):
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    time_shift = round((start_time - 1) * fps)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    compt = 0
    # output video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(save_path, fourcc, fps, (int(width), int(height)))


    # we read frames until synchronised
    for _ in range(abs(time_shift)):
        cap.read()

    while cap.isOpened():
        ret, frame = cap.read()

        if ret is not True:
            break
        else:
            # transformation of the frame
            for lane in positions.keys():
                x = positions[lane][compt]
                if x != -1:
                    # check were should the line be on x axis
                    if start_side_vid == 'right':
                        x = int((50 - x) * frame.shape[1] / 50)
                    else:
                        x = int(x * frame.shape[1] / 50)
                    # check were should the line be on y axis
                    if one_is_up == "true":
                        y = int(frame.shape[0]*(lane - 1)/8)
                    else:
                        y = int(frame.shape[0]*(8 - lane)/8)

                    h = int(frame.shape[0]/8)
                    width_line = 10

                    frame[y :y + h, x:x + width_line] = 0

            # write the new image
            out.write(frame)

        compt += 1

    cap.release()


if __name__ == "__main__":
    # print(extract_time_start('videos/50_brasse_stevens.mp4'))
    parser = argparse.ArgumentParser(description='Parser for automatic start detection.')
    parser.add_argument('--json', help='Path of the json of the race')
    parser.add_argument('--video', help='Path of the video')
    parser.add_argument('--csv', help='csv containing the position and with the format outputed in FFN_tool')
    parser.add_argument('--out', help='path to output the resulting video.')
    args = parser.parse_args()

    with open(args.json) as json_file:
        json_course = json.load(json_file)

    name_of_video = args.video.split('/')[-1]
    index_vid = get_index(json_course['videos'], name_of_video)
    start_time = json_course['videos'][index_vid]['start_moment']
    start_side = json_course['videos'][index_vid]['start_side']
    one_is_up = json_course['videos'][index_vid]['one_is_up']

    # formatting the data
    data = pd.read_csv(args.csv)  # id, frame_number, swimmer, x1, x2, y1, y2, event, cycles
    all_swimmers = {}
    for i in pd.unique(data['swimmer']):
        swimmer = data.loc[data['swimmer'] == i]
        all_swimmers[i] = swimmer['xd'].to_numpy()

    display_positions(args.video, start_time, all_swimmers, args.out, start_side, one_is_up)

    # information of the video in the json
    # change and save the json
    posivid_info = {'name': args.out.split('/')[-1],
                       'type_video': 'positions_auto',
                       'start_moment': 1,
                       'one_is_up': json_course['videos'][index_vid]['one_is_up'],
                       'generated_from': [name_of_video, args.csv.split('/')[-1]],
                       'fps': json_course['videos'][index_vid]['fps'],
                       'start_side': start_side
                    }
    index_posivid = get_index(json_course['videos'], args.out.split('/')[-1])
    if index_posivid > -1:
        json_course['videos'][index_posivid] = posivid_info
    else:
        json_course['videos'].append(posivid_info)

    with open(args.json, 'w') as outfile:
        json.dump(json_course, outfile, indent=4)