import Convert.splitwav as splitwav


if __name__ == "__main__":
	import argparse
    
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="A tool for converting between file formats")
	file_arg = parser.add_argument("-i", "--input", dest="file_path", default=None, help="Relative or absolute path to input file")

	args = parser.parse_args()

	if args.file_path == None:
		raise argparse.ArgumentError(file_arg, "Remember input file!")

	splitwav.run(args.file_path)