import glob, os
import GoogleWrap as sr


# obtain path to "test.wav" in the same folder as this script
from os import path

def google_speech(api_key, din):

	i = 0
	number_list = {'jack': 4098}
	del number_list['jack']

	values = []

	#for listing all files in directory (could be useful)
	for file in glob.glob(din+"*.wav"):
	    number_list[i] = file
	    i = i + 1

	if 0 in number_list:
		for key, value in number_list.iteritems():
			# use "test.wav" as the audio source
			r = sr.Recognizer()
			with sr.WavFile(value) as source:
			    audio = r.record(source) # read the entire WAV file

			# recognize speech using Google Speech Recognition
			try:
			    # for testing purposes, we're just using the default API key
			    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			    # instead of `r.recognize_google(audio)`
			    value = r.recognize_google(audio, api_key)
			    values.append(str(value))
			    #print "Google Speech Recognition thinks you said " + r.recognize_google(audio) + " for", key
			except sr.UnknownValueError:
				values.append(None)
			    #print "Google Speech Recognition could not understand audio for", key
			except sr.RequestError as e:
			    print "Could not request results from Google Speech Recognition service; {0}".format(e)

	return values

		