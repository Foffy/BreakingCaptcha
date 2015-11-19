from subprocess import call
from selenium import webdriver
import fillpage
import Keys.apiKey as apiKey
import Convert.splitwav as splitwav
import SpeechRecognition.speech as sr
import SpeechRecognition.dictionary as sd


def break_CAPTCHA(url, speech_key, convert_key):
	print "Downloading and saving mp3"
	driver = webdriver.Chrome()
	driver.get(url)

	done = False
	while not done:
	    fillpage.open_site(driver)
	    re = fillpage.get_mp3(driver)
	    if re:
	        fillpage.write_mp3(re)
	        done = True

	print "Converting mp3 to wav"
	call(["python", "conv.py"])


	#Split wav to multiple wavs
	info, frames = splitwav.load_file("out.wav")
	chunks = splitwav.get_chunks(info, frames)
	chunks_mod = splitwav.modify_chunks(chunks)
	splitwav.split_wav(info, chunks_mod, "Sounds/")

	# Use Google's speech recognition
	values = sr.google_speech(google_key, "Sounds/")

	print "Google returns: {}".format(values)


	# Use dictionary
	for x in range(len(values)):
		if not isinstance(values[x], int):
			if values[x] in sd.google_dict:
				values[x] = sd.google_dict[values[x]]

	print "After dictionary lookup, result is: {}".format(values)

	# Store values on disk
	fid = open("values", "w")
	for x in range(len(values)):
		if x == 0:
			fid.write("{}".format(values[x]))
		else:
			fid.write(",{}".format(values[x]))
			
	fid.close()

	# DTW
	call(["python", "doDTW.py"])


	# Send answer to web site




url = "http://webinsight.cs.washington.edu/projects/audiocaptchas/"

google_key = apiKey.getKey("Keys/google.key")
convert_key = apiKey.getKey("Keys/cc.key")

break_CAPTCHA(url, google_key, convert_key)

