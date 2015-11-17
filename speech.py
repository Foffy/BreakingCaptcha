 import glob, os
import SpeechRecognition.GoogleWrap as sr
import SpeechRecognition.dictionary as dico
import Keys.apiKey as apiKey


# obtain path to "test.wav" in the same folder as this script
from os import path

def google_speech(k):
	key = apiKey.getKey(k)

	dir_path = path.dirname(path.realpath(__file__)) + "/Sounds/"

	i = 0
	number_list = {'jack': 4098}
	del number_list['jack']

	values = []

	#for listing all files in directory (could be useful)
	os.chdir(dir_path)
	for file in glob.glob("*.wav"):
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
			    values.append(r.recognize_google(audio), key)
			    #print "Google Speech Recognition thinks you said " + r.recognize_google(audio) + " for", key
			except sr.UnknownValueError:
			    print "Google Speech Recognition could not understand audio for", key
			except sr.RequestError as e:
			    print "Could not request results from Google Speech Recognition service; {0}".format(e)

def check_dictionary(values):
	#now we check if our list have only digits
	for x in values:
		if RepresentsInt(x):
			print x
		elif x in dico.badaboum:
			print dico.badaboum[x]
		else:
	   		print x

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

google_speech('Keys/google.key')



		