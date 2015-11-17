import sys
import os
import Convert.CloudConvert as CloudConvert

def mp3_to_wav(fin, fout, key):
	input_file = fin
	output_file = fout

	process = CloudConvert.ConversionProcess(key)

	# This should autodetect file extension. if not, you can
	# always set process.fromformat and .toformat to the correct
	# values

	process.init(fin, fout)

	# This step uploads the file and starts the conversion.
	# If you pass `wait=True` the request will block until the
	# conversion is finished.
	process.start()

	print("Start conversion from", process.fromformat, "to", process.toformat)
	
	process.wait_for_completion()

	process.save()