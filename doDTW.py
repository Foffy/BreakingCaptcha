import DTW.dtw as dtw

fout = open('dtw2', 'w')
fid = open('values', 'r')

values_string = fid.readline()
values = values_string.split(',')

dtw_out = []

for x in range(len(values)):
	try:
		val = int(values[x])
		dtw_out.append(val)
	except ValueError:
		val = values[x]

	if not isinstance(val, int):
		result = dtw.k_nearest("Sounds/{}.wav".format(x), "Sounds/known/")
		dtw_out.append(result)

	

print(dtw_out)

fout.close()
fid.close()