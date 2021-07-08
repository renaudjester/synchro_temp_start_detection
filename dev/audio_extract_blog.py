import subprocess
import os
import scipy.io.wavfile as wav
import IPython
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

ffmpeg_path = 'D:/Work/Video/ffmpeg/bin/ffmpeg.exe'
wav_path = 'D:/Work/Video/Wav'
raw_videos_path = 'D:/Work/Video/RAW'
highlight_path = 'D:/Work/Video/Highlights'

file_list = [f for f in os.listdir(raw_videos_path)]

command = [[ffmpeg_path,'-i', file, wav_path+'/'+os.path.splitext(file)[0]+'.wav'] for file in file_list]

for cmd in command:
    # Remove old wav files
    try:
        os.remove(wav_path+'/'+os.path.splitext(cmd[2])[0]+'.wav')  
    except OSError:
        pass
    process = subprocess.run(cmd, cwd=raw_videos_path)

wav_file_list = [w for w in os.listdir(wav_path) if w.endswith('.wav')]


def process_wav_files(wav_file_list):
    wav_array = []
    sample_rates = []
    for index, file in enumerate(wav_file_list):
        #Read wav file
        sample_rate, data = wav.read(wav_path+'/'+file)
        #Convert to mono channel
        data = data.astype(np.int32)
        data_mono = (data[:,0] + data[:,1])/2
        wav_duration = len(data)/sample_rate
        sample_rates.append(sample_rate)
        wav_array.append(data_mono)
    return wav_array, sample_rates

# compute the intensity

def find_energy(moving_average_list):
  energy = []
  for array in moving_average_list:
    energy.append(np.square(array))
  return energy
  
def subsample(array, step):
  ssarray = array[::step].copy()
  return ssarray
  
SAMPLING_FACTOR = 4
WINDOW_LENGTH = 8
sampled_array = []
for array in wav_array:
  sampled_array.append(subsample(array, SAMPLING_FACTOR))
  moving_average = find_moving_average(sampled_array, sample_rates, WINDOW_LENGTH, SAMPLING_FACTOR)
  energy = find_energy(moving_average)
