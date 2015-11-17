import os

import Convert.convert as converts
import Keys.apiKey as apiKey


if __name__ == "__main__":
	import argparse
    
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="A tool for converting between file formats")
	file_arg = parser.add_argument("-i", "--input", dest="file_path", default=None, help="Relative or absolute path to input file")
	parser.add_argument("-o", "--output", dest="output_file", default="out.wav", help="Relative or absolute path to output file. Default is in current directory as out.wav")
	parser.add_argument("-k", "--key", dest="key_file", default=None, help="Relative or absolute path to key file")

	args = parser.parse_args()

	if args.file_path == None or args.output_file == None:
		raise argparse.ArgumentError(file_arg, "Remember input file and output file!")

	key = apiKey.getKey(args.key_file)
	converts.mp3_to_wav(args.file_path, args.output_file, key)