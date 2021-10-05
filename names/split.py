

letters = "abcdefghijklmnopqrstuvwxyz"
vowels = "aeiou"
filename = "Texts/last_names_edited.txt"

def split():
	with open("Texts/first_names.all.csv", "rb") as f:
		with open("Texts/first_names.txt", "wb") as f2:
			lns = f.readlines()
			for line in lns:
				try:
					out = line.decode("ascii").split(",")[0] + "\n"
					f2.write(out.encode("ascii"))
				except:
					pass

def removeChars(chars):
	lines = []
	with open(filename, "r") as f:
		lines = f.readlines()
	with open(filename, "w") as f2:
		for line in lines:
			contains_char = False
			for ch in chars:
				if ch in line:
					contains_char = True
			if not contains_char:
				f2.write(line)

def getFormat(s):
	f = ""
	for ch in s:
		if ch in vowels:
			f += "V"
		elif ch in letters:
			f += "C"
		else:
			f += "?"
	return f

def addForm(formats, s):
	form = getFormat(s)
	if "?" not in form:
		if form in formats:
			formats[form] += 1
		else:
			formats[form] = 1

def Formats():
	formats = {}
	with open(filename, "r") as f:
		lines = f.readlines()
		for line in lines:
			line = line.lower()
			if " " in line:
				for s in line[:-1].split(" "):
					addForm(formats, s)
			else:
				addForm(formats, line[:-1])

	remove = []
	for k in formats.keys():
		if formats[k] <= 4500 or len(k) > 13 or len(k) < 5:
			remove.append(k)
	for r in remove:
		del formats[r]
	
	lengths = [0] * 14
	for k in formats.keys():
		lengths[len(k)] += 1
	print(lengths)
	print(sum(lengths))
	print(formats.keys())

#removeChars("![]}{()@#$%^&*_+=\\|<>/?`0123456789;:~,'\"")
#split()
Formats()