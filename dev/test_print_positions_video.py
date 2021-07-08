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


def display_positions(video, start_time, positions, save_path, start_side_vid):
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    time_shift = round(start_time * fps)
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
        elif compt >= len(positions):
            pass
        else:
            # transformation of the frame
            x = positions[compt]
            if x != -1:
                if start_side_vid == 'right':
                    x = int((50 - x) * 1920 / 50)
                else:
                    x = int(x * 1920 / 50)
                width_line = 10

                y = int(frame.shape[0]*3/8)
                h = int(frame.shape[0]/8)

                frame[y :y + h, x:x + width_line] = 255

            # write the new image
            out.write(frame)

        compt += 1

    cap.release()


if __name__ == "__main__":

    json_path = "videos/2021_Marseille_freestyle_hommes_50_serie6.json"
    video = "videos/2021_Marseille_freestyle_hommes_50_serie6_positions.mp4"
    csv = "videos/florent_finale_espadon.csv"
    save_path = "videos/test_espadon_finale_minus_one.mp4"

    with open(json_path) as json_file:
        json_course = json.load(json_file)

    name_of_video = video.split('/')[-1]
    index_vid = get_index(json_course['videos'], name_of_video)
    start_time = json_course['videos'][index_vid]['start_moment']
    start_side = json_course['videos'][index_vid]['start_side']
    fps = json_course['videos'][index_vid]['fps']

    # data formatting
    data = pd.read_csv(csv)  # id, frame_number, swimmer, x1, x2, y1, y2, event, cycles
    data['frame_number'] = (data['temps'] * fps).round(decimals=0)
    data['frame_number'] = data['frame_number'].astype(int)
    # clean_data = pd.DataFrame({'frame_number': range(0, max(data.index))})
    # data = clean_data.merge(data, on="frame_number", how='outer')
    # data = data.set_index('frame_number').loc[range(0, max(data.index))].reset_index()
    data = data.set_index('frame_number')
    data = data.reindex(range(0, max(data.index)+1))
    data.loc[0] = 0
    # print(max(data.index))
    print(data)
    data_to_print = data['distance'].interpolate(method='index').to_numpy()
    print(data_to_print)
    # data = data.to_numpy()


    # all_swimmers = [[] for i in range(8)]
    # for i in range(8):
    #     all_swimmers[i] = np.squeeze(data[np.argwhere(data[:, 2] == i)])[:, (1, 3)]
    # all_swimmers = np.array(all_swimmers)
    display_positions(video, start_time, data_to_print, save_path, start_side)

