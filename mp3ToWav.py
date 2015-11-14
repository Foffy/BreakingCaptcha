import CloudConvert
import os
from os import path

dir_path = path.dirname(path.realpath(__file__))

apikey = "etDaoyH4mcong3nlNXZnSUeXUwe0y4_W1VgzW_-aRqufBhVbZPwEh1yA7qbodpVlFWUTJJpHRjeHFFh08ru73g"

process = CloudConvert.ConversionProcess(apikey)

# This should autodetect file extension. if not, you can
# always set process.fromformat and .toformat to the correct
# values

process.init(path.join(dir_path, "audio.mp3"), "out.wav")

# This step uploads the file and starts the conversion.
# If you pass `wait=True` the request will block until the
# conversion is finished.
process.start()

print("Start conversion from", process.fromformat, "to", process.toformat)

process.start()

process.wait_for_completion()

process.save()

os.remove("audio.mp3")