import os
SRC = "./out"

for f in os.listdir(SRC):
	if os.path.isdir(os.path.join(SRC, f)):
		new_name_arr = f.split("_")
		new_name = "_".join((new_name_arr[1], new_name_arr[0], new_name_arr[2]))
		folder_name = os.path.join(SRC, new_name)
		os.rename(os.path.join(SRC, f), folder_name)