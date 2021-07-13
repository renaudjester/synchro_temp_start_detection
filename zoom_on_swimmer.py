import cv2
import numpy as np
import pandas as pd
import argparse
import json
import matplotlib.pyplot as plt


def get_index(list_dict, vid_name):
    """helper to read the json file."""
    index = -1
    for i in range(len(list_dict)):
        if list_dict[i]['name'] == vid_name:
            index = i
    return index


def zoom_two_videos(videog, videod, start_timeg, start_timed, swimmer_data, hm_right, hm_left, save_path, size_box,
                    start_side_vid, lane, fps_analyse):
    """Input: right and left video of the race
    start_time gauche, start time droite
    swimmer_data (numpy array) : les positions du nageurs Il doit y avoir autant de lignes qu'il y a de frame dans la vidéo
    hm_right, hm_left : matrice d'homographie qui font le lien entre la vue de côté et la video vue du dessus
    save_path : where to save the video
    size_box : size in pixels/resolution of the output video
    start_side_vid ("right" or "left") : the side where the race starts (where the swimmers dive)
    lane (int) : the lane of the swimmer
    """
    capg = cv2.VideoCapture(videog)
    capd = cv2.VideoCapture(videod)
    fps = capg.get(cv2.CAP_PROP_FPS)

    # output video
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter(save_path, fourcc, fps, size_box)

    # invert the homography matrix
    new_hm_right = np.linalg.inv(hm_right)
    new_hm_left = np.linalg.inv(hm_left)

    time_shiftg = round((start_timeg - 1) * fps)
    time_shiftd = round((start_timed - 1) * fps)
    compt = 0

    # we read frames until synchronised
    for _ in range(abs(time_shiftg)):
        capg.read()
    for _ in range(abs(time_shiftd)):
        capd.read()

    while capd.isOpened() and capg.isOpened():
        retd, framed = capd.read()
        retg, frameg = capg.read()

        # mask = np.zeros((1920, 1080), dtype="uint8")
        # cv2.rectangle(mask, (0, 90), (290, 450), 255, -1)

        if retd is not True or compt >= len(swimmer_data):
            break
        else:
            # zoom
            # we get the position
            x = swimmer_data[compt][0]
            to_save = np.zeros((size_box[1], size_box[0], 3)).astype(np.uint8)

            # to choose the side of the video
            if x != -1 and x < 25:
                # convert x to a position that the homography maps
                if start_side_vid == 'right':
                    x = (50 - x) * 1920 / 50
                else:
                    x = x * 1920 / 50

                w = size_box[0]
                y = 1080 * (lane - 1 + 0.5) / 8
                h = size_box[1]

                # compute coordinates using linear algebra
                coor_maind = np.dot(new_hm_right, np.array([x, y, 1]))
                coor_maind = (coor_maind / coor_maind[-1]).astype(int)
                x_side, y_side = coor_maind[0], coor_maind[1]

                src = np.float32([[x_side - w // 2, y_side - h // 2], [x_side + w // 2, y_side - h // 2],
                                  [x_side - w // 2, y_side + h // 2], [x_side + w // 2, y_side + h // 2]])
                dest = np.float32([[0, 0], [w, 0],
                                   [0, h], [w, h]])
                M = cv2.getPerspectiveTransform(src, dest)
                to_save = cv2.warpPerspective(framed, M, size_box)

            elif x != -1:
                # convert x to a position that the homography maps
                if start_side_vid == 'right':
                    x = (50 - x) * 1920 / 50
                else:
                    x = x * 1920 / 50

                w = size_box[0]
                y = 1080 * (lane - 1 + 0.5) / 8
                h = size_box[1]

                # using the opencv functions
                to_transform = np.float32([[[x, y]]])
                coorg = cv2.perspectiveTransform(to_transform, new_hm_left)
                coorg = np.squeeze(coorg).astype(int)
                x_side, y_side = coorg[0], coorg[1]

                src = np.float32([[x_side - w // 2, y_side - h // 2], [x_side + w // 2, y_side - h // 2],
                                  [x_side - w // 2, y_side + h // 2], [x_side + w // 2, y_side + h // 2]])
                dest = np.float32([[0, 0], [w, 0],
                                   [0, h], [w, h]])
                M = cv2.getPerspectiveTransform(src, dest)
                to_save = cv2.warpPerspective(frameg, M, size_box)

        # write the new image (it will be black if x = -1)
        out.write(to_save)

        compt += 1

    capd.release()
    capg.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parser for zoom on one swimmer.')
    parser.add_argument('--json', help='Path of the json of the race')
    parser.add_argument('--videog', help='Path of the left video')
    parser.add_argument('--videod', help='Path of the right video')
    parser.add_argument('--out', help='path to output the resulting video.')
    parser.add_argument('--lane', help='lane number to extract the zoom from.', default='3')
    parser.add_argument('--csv', help='Csv with the tracking data to use to zoom.')
    parser.add_argument('--type_data', help='To get the type of analysis (values: auto or manuel)', default='auto')
    args = parser.parse_args()

    # get the info from the json
    with open(args.json) as json_file:
        json_course = json.load(json_file)
    name_of_video_to_get_info_gauche = args.json.split('/')[-1].split('.')[0] + '_fixeGauche.mp4'
    name_of_video_to_get_info_droite = args.json.split('/')[-1].split('.')[0] + '_fixeDroite.mp4'
    index_vidg = get_index(json_course['videos'], name_of_video_to_get_info_gauche)
    index_vidd = get_index(json_course['videos'], name_of_video_to_get_info_droite)
    start_side = json_course['videos'][index_vidg]['start_side']
    one_is_up = json_course['videos'][index_vidg]['one_is_up']
    start_timeg = json_course['videos'][index_vidg]['start_moment']
    start_timed = json_course['videos'][index_vidd]['start_moment']
    fps_analyse = int(json_course['videos'][index_vidd]['fps'])

    # get the homography matrices : first the correspondence points
    src_ptsg = np.float32(json_course['videos'][index_vidg]['srcPts'])
    dest_ptsg = np.float32(json_course['videos'][index_vidg]["destPts"])
    src_ptsd = np.float32(json_course['videos'][index_vidd]['srcPts'])
    dest_ptsd = np.float32(json_course['videos'][index_vidd]["destPts"])
    # we need to convert the points of the calibration to make them correspond the destination image size
    shape_output_img = (1920, 1080)
    size_image_ref = (900, 360)
    dest_ptsg[:, 0] = dest_ptsg[:, 0] * shape_output_img[0] / size_image_ref[0]
    dest_ptsg[:, 1] = dest_ptsg[:, 1] * shape_output_img[1] / size_image_ref[1]
    dest_ptsd[:, 0] = dest_ptsd[:, 0] * shape_output_img[0] / size_image_ref[0]
    dest_ptsd[:, 1] = dest_ptsd[:, 1] * shape_output_img[1] / size_image_ref[1]

    # generating the homography matrices
    hm_left = cv2.getPerspectiveTransform(src_ptsg, dest_ptsg)
    hm_right = cv2.getPerspectiveTransform(src_ptsd, dest_ptsd)

    # we need to get the fps of the video we are reading (we suppose that left and right are the same)
    video = cv2.VideoCapture(args.videog)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()


    # selecting a frame to start the zoom
    if start_side == 'right':
        start_frame = round((start_timed - 1) * fps)
    else:
        start_frame = round((start_timeg - 1) * fps)
    synchro_start_time = min(start_timed, start_timeg)

    # converting the data to use them easily in the function with a numpy array and the index is the frame index
    data = pd.read_csv(args.csv)
    # adjust the possible fps difference between the analysis and the video we zoom on

    if args.type_data == 'manuel':
        # also adjust the analysis to start at 1sec
        data['time'] = data['frame_number'] / fps_analyse - synchro_start_time + 1
        data = data[data['time'] > 0]
    else:
        data['time'] = data['frame_number'] / fps_analyse
    data['frame_number'] = (data['time'] * fps).round(decimals=0)
    data['frame_number'] = data['frame_number'].astype('int')

    all_swimmers = {}
    for i in pd.unique(data['swimmer']):
        swimmer = data.loc[data['swimmer'] == i]
        to_interpolate = swimmer.set_index('frame_number')
        to_interpolate = to_interpolate.reindex(range(0, max(to_interpolate.index) + 1))
        to_interpolate = to_interpolate.replace('-1', np.nan)
        to_interpolate = to_interpolate.replace(-1, np.nan)
        to_interpolate.at[0, 'xd'] = 0
        data_to_print = to_interpolate[['xd']].interpolate(method='index')
        data_to_print['xd'] = data_to_print['xd'].astype(float)
        data_to_print = data_to_print.to_numpy()
        all_swimmers[i] = data_to_print


    # let's compute the zoom
    # first we check where is the lane 1
    if one_is_up == "true":
        lane = int(args.lane)
        if len(pd.unique(data['swimmer'])) == 10:
            lane = lane + 1
    else:
        if len(pd.unique(data['swimmer'])) == 10:
            lane = len(pd.unique(data['swimmer'])) - int(args.lane)
        else:
            lane = len(pd.unique(data['swimmer'])) - int(args.lane) + 1
    size_box = (384, 256)

    zoom_two_videos(args.videog, args.videod, start_timeg, start_timed, all_swimmers[int(args.lane)], hm_right, hm_left, args.out,
                    size_box, start_side, lane, fps)

    # information of the video in the json
    # change and save the json
    zoom_info = {'name': args.json.split('/')[-1].split('.')[0] + '_zoom_' + str(args.lane) + '.mp4',
                    'type_video': 'zoom',
                    'start_moment': 1,
                    'one_is_up': json_course['videos'][index_vidg]['one_is_up'],
                    'generated_from': [name_of_video_to_get_info_gauche, name_of_video_to_get_info_droite, args.csv.split('/')[-1]],
                    'fps': fps,
                    'start_side': start_side
                    }
    index_zoom = get_index(json_course['videos'], args.json.split('/')[-1].split('.')[0] + '_zoom_' + str(args.lane) + '.mp4')
    if index_zoom > -1:
        json_course['videos'][index_zoom] = zoom_info
    else:
        json_course['videos'].append(zoom_info)

    with open(args.json, 'w') as outfile:
        json.dump(json_course, outfile, indent=4)

    # command to launch the code (used in the a unix environnement with the necessary python packages)
    # python3 zoom_on_swimmers.py
    # --json /home/amigo/Bureau/data/kazan2015_david/50_Brasse_Women_Final/2015_Kazan_brasse_dames_50_finale.json
    # --videog /home/amigo/Bureau/data/kazan2015_david/50_Brasse_Women_Final/50_B_W_F_lowered.mp4
    # --videod /home/amigo/Bureau/data/kazan2015_david/50_Brasse_Women_Final/50_B_W_F_Cd_lowered.mp4
    # --out /home/amigo/Bureau/data/kazan2015_david/50_Brasse_Women_Final/2015_Kazan_brasse_dames_50_finale_zoom.mp4
    # --csv /home/amigo/Bureau/data/kazan2015_david/50_Brasse_Women_Final/2015_Kazan_brasse_dames_50_finale_automatique.csv

    # todo: generate information on the data to get the start of the analysis (for the moment it's because I know that
    # the start is 1 sec for the auto and the start of the from_above for the manual)