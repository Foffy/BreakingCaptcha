import subprocess
import cPickle

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

	# print "Populating registration fields"
	# fillpage.push_information(driver)

	done = False
	while not done:
	    fillpage.open_site(driver)
	    re = fillpage.get_mp3(driver)
	    if re:
	        fillpage.write_mp3(re)
	        done = True

	print "Converting mp3 to wav"
	
	args = ' '.join(
			['ffmpeg',
			'-y', 						# force overwrite if output file exists
			'-loglevel fatal',			# suppress log output unless fatal
			'-i audio.mp3',				# input file
			'out.wav'					# output file
			])

	subprocess.Popen(args, shell=True).wait()

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
				values[x] = str(sd.google_dict[values[x]])

	print "After dictionary lookup, result is: {}".format(values)

	# Store values on disk using cPickle
	with open('values.b', 'wb') as v_file:
		cPickle.dump(values, v_file)

	# DTW
	args = ' '.join(
		['python',
		'doDTW.py',
		'-i values.b',
		 ])

	subprocess.Popen(args, shell=True).wait()
	with open('values.b', 'rb') as v_file:
		values = cPickle.load(v_file)
	print "After DTW, result is {}".format(values)


	# Send answer to web site
	
	done = fillpage.push_response(driver, values)
	if done:
		cleanup()
		driver.quit()
		break_CAPTCHA(url, speech_key, convert_key)
	else:
		#cleanup()
		#driver.quit()
		pass

def cleanup():
	args = ' '.join(
		['rm',
		'out.wav audio.mp3 Sounds/*.wav trash values.b'
		])

	subprocess.Popen(args, shell=True).wait()

url = "http://webinsight.cs.washington.edu/projects/audiocaptchas/"
url2 = "https://www.cybrary.it/register/"

google_key = apiKey.getKey("Keys/google.key")
convert_key = apiKey.getKey("Keys/cc.key")

break_CAPTCHA(url, google_key, convert_key)

