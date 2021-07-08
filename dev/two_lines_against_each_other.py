import cv2
import numpy as np

def fusion(video1, video2, time_difference, lane1 ,lane2, save_path):
    cap1 = cv2.VideoCapture(video1)
    cap2 = cv2.VideoCapture(video2)
    fps = cap1.get(cv2.CAP_PROP_FPS)
    time_shift = round(time_difference * fps)
    width = cap1.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
    height = cap1.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # output video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(save_path, fourcc, fps, (int(width), int(height)))


    # we read frames until synchronised
    for _ in range(abs(time_shift)):
        if time_shift > 0:
            cap1.read()
        else:
            cap2.read()

    while (cap1.isOpened()) and (cap2.isOpened()):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if ret1 is not True or ret2 is not True:
            break
        else:
            # transformation of the frame
            x = 0
            y1 = int(frame1.shape[0]*(lane1-1)/8)
            y2 = int(frame2.shape[0]*(lane2-1)/8)
            w = frame1.shape[1]
            h = int(frame1.shape[0]/8)
            mask1 = np.zeros(frame1.shape, np.uint8)
            mask1[y1:y1 + h, x:x + w] = frame1[y1:y1 + h, x:x + w]
            mask2 = np.zeros(frame2.shape, np.uint8)
            mask2[y2:y2 + h, x:x + w] = frame2[y2:y2 + h, x:x + w]
            mask2 = cv2.flip(mask2, 1)


            # stitch them together
            out_top = np.where(mask1 != 0, mask1, mask2)
            # out_top = mask1
            out.write(out_top)
    cap1.release()
    cap2.release()


if __name__ == "__main__":
    out = "test_two_lanes/fusioned.mp4"
    video1_path = "test_two_lanes/2021_Marseille_freestyle_hommes_50_serie6_from_above_25ffps.mp4"
    video2_path = "test_two_lanes/2021_Nice_freestyle_50_serie4_hommes_from_above.mp4"
    lane1 = 4
    lane2 = 5
    one_is_up = True
    start_time_1 = 14.356953631553631
    start_time_2 = 25.36151400454201
    time_difference = start_time_1 - start_time_2
    fusion(video1_path, video2_path, time_difference, lane1, lane2, out)

