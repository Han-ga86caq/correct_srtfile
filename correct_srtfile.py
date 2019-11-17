import re
import sys

class chunk:
	def __init__(self,idx):
		self.idx = idx # The index of occurance
		self.t1 = 0.0
		self.t2 = 0.0
		self.txt = [] # Original text without original idx
	def __repr__(self):
		if self.txt:
			return ''.join(self.txt)
		else:
			return 'Empty chunk, not yet initialized!'

def time2sec(str):
	m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)",str)
	n = re.match(r"(\d+):(\d+):(\d+)",str)
	if m:
		hour = float(m.group(1))
		minute = float(m.group(2))
		second = float(m.group(3)) + float(m.group(4))*10**(-len(m.group(4)))
		return hour*3600+minute*60+second
	elif n:
		hour = float(n.group(1))
		minute = float(n.group(2))
		second = float(n.group(3))
		return hour*3600+minute*60+second
	else:
		raise Exception('Wrong clock time format, should be h:m:s!')

def process_str(txt):	
	status = 0
	idx = 1
	chunks = []
	txt_out = []
	txt_dict = {}
	
	for s in txt:
		if status == 0:
			m = re.match(r"\d+$",s)
			if m:
				status += 1
				chunks.append(chunk(idx))
			else:
				raise Exception('Srt file format error!')
		elif status == 1:
			m = re.match(r"(\d+:\d+:\d+[,.]\d+) --> (\d+:\d+:\d+[,.]\d+)",s)
			n = re.match(r"(\d+:\d+:\d+) --> (\d+:\d+:\d+)",s)
			if m:
				status += 1
				chunks[-1].t1 = time2sec(m.group(1))
				chunks[-1].t2 = time2sec(m.group(2))
				chunks[-1].txt.append(s)
			elif n:
				status += 1
				chunks[-1].t1 = time2sec(n.group(1))
				chunks[-1].t2 = time2sec(n.group(2))
				chunks[-1].txt.append(s)
			else:
				raise Exception('Srt file format error!')
		elif status == 2:
			m = re.match(r"\s+$",s)
			if not m:
				# First remove "Zero width space"
				_s = re.sub(u"\u200b+",'',s)
				chunks[-1].txt.append(_s)
			else:
				if not ''.join(chunks[-1].txt) in txt_dict:
					txt_dict[''.join(chunks[-1].txt)] = idx 
					txt_out.append(str(idx)+'\n')
					txt_out += chunks[-1].txt
					txt_out.append('\n')
					idx += 1
				status = 0

	# Sort the result by time order
	chunks.sort(key=lambda x:x.t1, reverse=False)

	return txt_out, chunks, txt_dict


def correct_srtfile(filename):

	f=open(filename)
	txt_in=f.readlines()
	txt_out, chunks, txt_dict = process_str(txt_in)  
	f.close()
	with open(filename[:-4]+' new.srt', 'w') as fout:
		fout.writelines(txt_out)


if __name__ == "__main__":
	for file in sys.argv[1:]:
		print("Correcting file\n \""+ file+"\"\n")
		correct_srtfile(file)
		print("Completed! The result has been written to\n \""+file[:-4]+" new.srt\"\n")


