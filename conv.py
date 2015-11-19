import Convert.convert as convert
import Keys.apiKey as apiKey


convert_key = apiKey.getKey("Keys/cc.key")
convert.mp3_to_wav("audio.mp3", "out.wav", convert_key)