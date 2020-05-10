import os

def delete_gap_dir(dir):
	if os.path.isdir(dir):
		for d in os.listdir(dir):
			delete_gap_dir(os.path.join(dir, d))
		if not os.listdir(dir):
			os.rmdir(dir)
			print('remove ' + dir)
			
delete_gap_dir(os.getcwd())
print(u'clean finish')