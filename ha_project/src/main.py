#https://likegeeks.com/python-gui-examples-tkinter-tutorial/#Create-your-first-GUI-application
#very easy tutorial
#Author of this file: Aldo Alvarez

import tkinter as tk
from tkinter import *
from tkinter import ttk
from playsound import playsound
import speech_recognition as sr
import winsound
import threading

#Libraries for audio analysis
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
import librosa
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import numpy as np
import librosa.display
from dtw import dtw
from numpy.linalg import norm
import pandas as pd

#Global variables
AUGMENTED_ERROR_FILE = None
ORIGINAL_AUDIO_PATH = 'original.wav'
RECORDED_AUDIO_PATH = 'recorded.wav'
# Global variables to be used
START_RECORDING_LABEL = None
btn_play_augmented = None 
btn_play_recorded = None
PROGRESS_BAR = None
RECORD_AFTER_PLAY = 1
ERROR_LEVEL = ''

# Files variables
path_final_data = 'levels/final_data.csv'
# Error scale csv file name
path_scale_data = 'levels/scale_data.csv'
# Audio files for levels of error  path
path_audio_files = 'levels/'
 


# Data files
SCALE_DATA = None
AUDIO_DATA = None
BASELINE_MFCC = None
BASELINE_DURATION = None
CHECK_BUTTON =  None

# Audio Variables
sample_rate = 44100


#play the original audio of the script
def play_original_audio(self):
	t = threading.Thread(target=play_aux)
	t.start()
	
def play_aux():
	winsound.PlaySound(ORIGINAL_AUDIO_PATH, winsound.SND_FILENAME)
	START_RECORDING_LABEL.grid(column=0, row=6, columnspan = 3)
	if RECORD_AFTER_PLAY == 1:
		record_audio()
	#new_image = PhotoImage(file="play_back_original.png")
	#btn_play_recorded.configure(image = new_image)

def process_function():
	global AUGMENTED_ERROR_FILE
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Processing..."))
	result = process_input_audio()
	PROGRESS_BAR['value'] = 1000
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Finding error level..."))
	level = determine_level(result[0], result[1], result[2])
	print("Level of error is, ",level)
	PROGRESS_BAR['value'] = 2000
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Determining the audio file to choose..."))
	file = get_file_play_back(level, result[0])
	AUGMENTED_ERROR_FILE = file
	print("The file to play is: ", file)
	PROGRESS_BAR['value'] = 3000
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Finished!"))
	PROGRESS_BAR['value'] = 4000
	tk.Tk().after(400, START_RECORDING_LABEL.configure(text="Press the play button to start!"))	
	PROGRESS_BAR['value'] = 0

def button_record():
	t = threading.Thread(target=record_audio)
	t.start()
#record the audio from the user
def record_audio():
	# initialize the recognizer, just to use the microphone
	r = sr.Recognizer()
	# To avoid detecting noise when recording
	r.energy_threshold = 60
	#listen to the micro until the user says something
	with sr.Microphone(device_index=1) as source: # the device index is the index of the microphone to use
		r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
		START_RECORDING_LABEL.configure(text="Recording Started!")
		audio = r.listen(source)

	#save the recorded audio to a file
	with open(path_audio_files+RECORDED_AUDIO_PATH, "wb") as f:
		f.write(audio.get_wav_data())

	START_RECORDING_LABEL.configure(text="Recording finished!")
	process_function()

def play_back_button():
	t = threading.Thread(target=play_back)
	t.start()

def play_back():
	winsound.PlaySound(path_audio_files+RECORDED_AUDIO_PATH, winsound.SND_FILENAME)

def upload_files():
	print('## Uploading csv files')
	global SCALE_DATA
	global AUDIO_DATA
	SCALE_DATA = pd.read_csv(path_scale_data)
	AUDIO_DATA = pd.read_csv(path_final_data)

def load_baseline_info():
	print('## Uploading and processing audio baseline')
	global BASELINE_MFCC 
	global BASELINE_DURATION
	#load baseline audio
	baseline_samples, baseline_sample_rate = librosa.load(ORIGINAL_AUDIO_PATH, sr=sample_rate)
	#extract the mfcc coefficients from the baseline audio
	
	BASELINE_MFCC = librosa.feature.mfcc(baseline_samples, baseline_sample_rate)
	BASELINE_DURATION = len(baseline_samples)/baseline_sample_rate
	print('## MFCC', np.mean(BASELINE_MFCC), ' ## DURATION', BASELINE_DURATION)

def process_input_audio():
	print('BASELINE DURATION', BASELINE_DURATION)
	input_samples, input_sample_rate = librosa.load(path_audio_files+RECORDED_AUDIO_PATH, sr=sample_rate)
	input_mfcc = librosa.feature.mfcc(input_samples, input_sample_rate)
	input_duration = (len(input_samples)/input_sample_rate)-1
	input_diff_duration = input_duration - BASELINE_DURATION
	input_dist, input_cost, input_acc_cos, input_path = dtw(BASELINE_MFCC.T, input_mfcc.T, dist=lambda x, y: norm(x - y, ord=1))
	print(input_dist, input_duration, input_diff_duration)
	return (input_dist, input_duration, input_diff_duration)

#MFCC DTW Duration DurationDiff Min-DTW Max-DTW Min-Dur Max-Dur Min-Dur-d Max-Dur-d Level
def determine_level(dtw_distance, duration, diff_against_baseline):
	level_result = None
	for index, row in SCALE_DATA.iterrows():
		# for each row lets ask if the input data information falls in some level
		sum_result = [-1,-1,-1]
		if row['Min-DTW'] <= dtw_distance <= row['Max-DTW']:
			sum_result[0] = 1
		if row['Min-Dur'] <= duration <= row['Max-Dur']:
			sum_result[1] = 1
		if row['Min-Dur-d'] <= diff_against_baseline <= row['Max-Dur-d']:
			sum_result[2] = 1
		if sum(sum_result) >= 1:
			#level found
			level_result = row['Level']
	if level_result is None:
		for index, row in SCALE_DATA.iterrows():
			if dtw_distance <= row['DTW']:
				level_result = row['Level']
	if level_result is None:
		level_result = 'level-4'
	return level_result       


# filter our data table 
def get_file_play_back(level, input_dist):
	if level == 'no-error':
		return ORIGINAL_AUDIO_PATH
	result = ''
	level_number = int(level.split('-')[1])	
	if level_number<4:
		# let's choose the audio that is the next in the level of errors
		possible_audio_files = AUDIO_DATA[AUDIO_DATA['Levels'] == 'Level-'+str(level_number+1)]
		# if the recorded file 
		for index, row in possible_audio_files.iterrows():
			result = row['File name']
	else:
		result = RECORDED_AUDIO_PATH
	return result

def play_augmented_button():
	t = threading.Thread(target=play_agumented)
	t.start()

def play_agumented():
	if AUGMENTED_ERROR_FILE is not None:
		winsound.PlaySound(path_audio_files+AUGMENTED_ERROR_FILE, winsound.SND_FILENAME)

def check_changed():
	print('Changeeeed!')
	global RECORD_AFTER_PLAY
	if RECORD_AFTER_PLAY == 1:
		RECORD_AFTER_PLAY = 0
		CHECK_BUTTON.configure(text='Record after play!')
	else:
		RECORD_AFTER_PLAY = 1
		CHECK_BUTTON.configure(text='Just play, not record!')



"""
def process_audio():
		'''simulate reading 500 bytes; update progress bar'''
		self.bytes += 500
		self.progress["value"] = self.bytes
		if self.bytes < self.maxbytes:
			# read more bytes after 100 ms
			self.after(100, self.read_bytes)
"""

###############################################################################
# Main
###############################################################################
if __name__ == "__main__":
	window = Tk()
	window.title("Speech Error Augmentation")
	window.configure(background='#666666')

	# Load Files to be used for input processing
	upload_files()
	load_baseline_info()

	#tk.Entry(window).pack(fill='x')
	lbl = Label(window, text="Welcome to the Speech Error Augmentation Tool", font=("sans-serif", 14), background='#666666', fg='#eaeaea')
	lbl.grid(column=0, row=0, columnspan=3, sticky='we')
	lbl_instruction = Label(window, text="Please, repeat the following text as you hear it from the example",font=("sans-serif", 14), background='#666666', fg='#eaeaea')
	lbl_instruction.grid(column=0, row=1, columnspan=3, sticky='we')

	lbl_script = Label(window,  text='Thanks, I have been going to the gym!' ,font=("sans-serif", 24), background='#e6e6e6', fg='#2b0000') 
	lbl_script.grid(column=0, row=2, columnspan=3, sticky='wens',rowspan=2, padx=10,pady=10, ipadx=10,ipady=10)

	play_background_img = PhotoImage(file="play.png")
	record_background_img = PhotoImage(file="record.png")
	#playing button
	btn = Button(window, text="Play", image = play_background_img, height = 120, width = 120, background='#666666', borderwidth=0)
	btn.configure(command= lambda: play_original_audio(btn))
	btn.grid(column=0, row=4)

	#recording button
	btn_record =  Button(window, text="Record", command=button_record, image = record_background_img, height = 120, width = 120, background='#666666', borderwidth=0)
	btn_record.grid(column=1, row=4)

	CHECK_BUTTON = Button(window, text="Just play, not record!", command=check_changed, background='#666666', fg='#eaeaea')
	CHECK_BUTTON.grid(column=2, row=4)
	START_RECORDING_LABEL = Label(window,  text='Press the play button to start!' ,font=("sans-serif", 14), background='#ffd42a', fg='#782121') 
	START_RECORDING_LABEL.grid(column=0, row=6, columnspan = 3)

	PROGRESS_BAR = ttk.Progressbar(window, orient="horizontal",length=200, mode="determinate", value=0, maximum=4000)
	PROGRESS_BAR.grid(column=0, row=7, columnspan=3, sticky='we', padx=10,pady=10, ipadx=10,ipady=5)
	#play recorded
	action_buttons_frame = tk.Frame(window)

	play_back_augmented_img = PhotoImage(file="play_back_original.png")
	play_disabled_img = PhotoImage(file="play_back_ready.png")
	
	
	btn_play_recorded =  Button(action_buttons_frame, text="Play recorded", command=play_back_button, image = play_back_augmented_img, height = 50, width = 50, background='#666666', borderwidth=0)
	btn_play_recorded.grid(column=0, row=1, sticky = 'w')

	btn_play_augmented =  Button(action_buttons_frame, text="Play augmented", command=play_augmented_button, image = play_disabled_img, height = 50, width = 50, background='#666666', borderwidth=0)
	btn_play_augmented.grid(column=1, row=1, sticky = 'w')


	action_buttons_frame.grid(column=0, row=8, sticky = 'w')
	#window.state("zoom")
	window.mainloop()