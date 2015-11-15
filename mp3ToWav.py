import sys
import CloudConvert
import os
from os import path
import apiKey


input_file = 'audio.mp3'
output_file = 'out.mp3'
api_key = ''

API_KEY = 'cloudconvertAPI.key'

dir_path = path.dirname(path.realpath(__file__))

process = CloudConvert.ConversionProcess(apiKey.getKey(API_KEY))

# This should autodetect file extension. if not, you can
# always set process.fromformat and .toformat to the correct
# values

process.init(input_file, output_file)

# This step uploads the file and starts the conversion.
# If you pass `wait=True` the request will block until the
# conversion is finished.
process.start()

print("Start conversion from", process.fromformat, "to", process.toformat)

process.start()

process.wait_for_completion()

process.save()

os.remove("audio.mp3")