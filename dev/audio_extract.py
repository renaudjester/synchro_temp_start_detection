# pip install moviepy ffmpeg
import moviepy.editor as mp

my_clip1 = mp.VideoFileClip(r"videos/fixe1.mp4")
my_clip2 = mp.VideoFileClip(r"videos/fixe2.mp4")

my_clip1.audio.write_audiofile(r"wav/fix1.wav")
my_clip2.audio.write_audiofile(r"wav/fix2.wav")
