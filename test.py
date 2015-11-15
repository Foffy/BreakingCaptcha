import os
import librosa

def run(module, fin, fout, key):
	# print module, fin, fout, key

	if module == "dtw":
		import DTW.dtw

if __name__ == "__main__":
	import argparse
    
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="A tool for testing different modules in the automatic CAPTCHA breaking system")
	parser.add_argument("-m", "--module", dest="module",default=None, 
						help=(	"DTW (-i):\t\tRun DTW with 5 nearest results.\n" 
								"Convert (-i -o -k):\tConvert mp3 file to wav.\n"
								"Split (-i -o):\t\tSplit .wav file into multiple .wav files each containing one word.\n"
								"Google (-i -k):\t\tUse Google's speech recognition on the desired file."))
	file_arg = parser.add_argument("-i", "--input", dest="file_path", default=None, help="Relative or absolute path to input file.")
	parser.add_argument("-o", "--output", dest="output_file", default="./out.wav", help="Relative or absolute path to output file. Default is in current directory as out.wav.")
	parser.add_argument("-k", "--key", dest="key_file", default=None, help="Relative or absolute path to key file")

	args = parser.parse_args()

	if args.module == None:
		raise argparse.ArgumentError(file_arg, "No module selected")

	run(args.module.lower(), args.file_path, args.output_file, args.key_file)