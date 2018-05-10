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
#Global variables
ORIGINAL_AUDIO_PATH = 'original.wav'
RECORDED_AUDIO_PATH = 'recorded.wav'

# Global variables to be used
START_RECORDING_LABEL = None
PROGRESS_BAR = None
RECORD_AFTER_PLAY = 0
#play the original audio of the script
def play_original_audio(self):
	t = threading.Thread(target=play_aux)
	t.start()
    
def play_aux():
	winsound.PlaySound(ORIGINAL_AUDIO_PATH, winsound.SND_FILENAME)
	START_RECORDING_LABEL.grid(column=0, row=6, columnspan = 3)
	#if RECORD_AFTER_PLAY == 1:
	record_audio()
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Processing..."))
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Finished!"))
	tk.Tk().after(200, START_RECORDING_LABEL.configure(text="Press the play button to start!"))

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
	with open(RECORDED_AUDIO_PATH, "wb") as f:
		f.write(audio.get_wav_data())
	START_RECORDING_LABEL.configure(text="Recording finished!")

def play_back_button():
	t = threading.Thread(target=play_back)
	t.start()

def play_back():
	winsound.PlaySound(RECORDED_AUDIO_PATH, winsound.SND_FILENAME)
"""
def process_audio():
        '''simulate reading 500 bytes; update progress bar'''
        self.bytes += 500
        self.progress["value"] = self.bytes
        if self.bytes < self.maxbytes:
            # read more bytes after 100 ms
            self.after(100, self.read_bytes)
"""
def btnCallBacks(event):
	event.widget.configure(background='#666666', borderwidth=0)
	return 'Aldo'
###############################################################################
# Main
###############################################################################
if __name__ == "__main__":
	window = Tk()
	window.title("Speech Error Augmentation")
	window.configure(background='#666666')
	#tk.Entry(window).pack(fill='x')
	lbl = Label(window, text="Welcome to the Speech Error Augmentation Tool", font=("sans-serif", 14), background='#666666', fg='#eaeaea')
	lbl.grid(column=0, row=0, columnspan=3, sticky='we')
	lbl_instruction = Label(window, text="Please, repeat the following text as you listen to it from the example",font=("sans-serif", 14), background='#666666', fg='#eaeaea')
	lbl_instruction.grid(column=0, row=1, columnspan=3, sticky='we')

	lbl_script = Label(window,  text='Thanks, I have been going to the gym!' ,font=("sans-serif", 24), background='#e6e6e6', fg='#2b0000') 
	lbl_script.grid(column=0, row=2, columnspan=3, sticky='wens',rowspan=2, padx=10,pady=10, ipadx=10,ipady=10)

	play_background_img = PhotoImage(file="play.png")
	record_background_img = PhotoImage(file="record.png")
	#playing button
	btn = Button(window, text="Play", image = play_background_img, height = 120, width = 120, background='#666666', borderwidth=0)
	btn.configure(command= lambda: play_original_audio(btn))
	btn.bind("<Button-1>", btnCallBacks)
	btn.grid(column=0, row=4)

	#recording button
	btn_record =  Button(window, text="Record", command=button_record, image = record_background_img, height = 120, width = 120, background='#666666', borderwidth=0)
	btn_record.grid(column=1, row=4)

	c = Checkbutton(window, text="Record right after play", variable=RECORD_AFTER_PLAY)
	c.grid(column=2, row=4)
	START_RECORDING_LABEL = Label(window,  text='Press the play button to start!' ,font=("sans-serif", 14), background='#ffd42a', fg='#782121') 
	START_RECORDING_LABEL.grid(column=0, row=6, columnspan = 3)

	PROGRESS_BAR = ttk.Progressbar(window, orient="horizontal",length=200, mode="determinate")
	PROGRESS_BAR.grid(column=0, row=7, columnspan=3, sticky='we', padx=10,pady=10, ipadx=10,ipady=5)
	#play recorded
	play_back_background_img = PhotoImage(file="playback.png")
	btn_play_recorded =  Button(window, text="Play recorded", command=play_back_button, image = play_back_background_img, height = 80, width = 80, background='#666666', borderwidth=0)
	btn_play_recorded.grid(column=0, row=8)
	#window.state("zoom")
	window.mainloop()