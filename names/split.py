import click

LETTERS = "abcdefghijklmnopqrstuvwxyz"
VOWELS = "aeiou"
INVALID_CHARS = "![]}{()@#$%^&*_+=\\|<>/?`0123456789;:~,'\""

# Number determined to be the maximum needed by trial and error (setting the min occurences quite low)
NAME_LENGTH_LIMIT = 12
DEFAULT_FORMAT_FILENAMES = ["Texts/first_names_edited.txt", "Texts/last_names_edited.txt"]


def split_csv(infile, outfile):
	'''
	The original name data files are CSVs of the form [name],[number].
	This function strips out the numbers as well as any non-ascii names and writes them out to a new file.
	'''
	lines = []
	with open(infile, "rb") as f:
		print("Reading from " + filename)
		lines = f.readlines()
	with open(outfile, "wb") as f2:
		print("Writing to " + filename)
		for line in lines:
			try:
				out = line.decode("ascii").split(",")[0] + "\n"
				f2.write(out.encode("ascii"))
			except:
				pass

def contains_invalid_char(s):
	contains_char = False
	for ch in INVALID_CHARS:
		if ch in s:
			return True
	return False

def removeChars(filenames):
	'''
	One-time use function (per text file) to strip out lines containing undesirable characters, overwriting the old data.
	'''
	for filename in filenames:
		print("Reading and overwriting " + filename)
		input_lines = []
		output_lines = []
		with open(filename, "r") as f:
			input_lines = f.readlines()
		for line in input_lines:
			if not contains_invalid_char(line):
				output_lines.append(line)
		with open(filename, "w") as f2:
			f2.write("\n".join(output_lines))

def getFormat(s):
	'''
	Converts an ascii string into vowel-consonant form (VCF), with ? indicating non-alphabetic characters.
	'''
	f = ""
	for i, ch in enumerate(s):
		if ch == 'y':
			# Y is complicated. This is a first approximation of how to categorize it. I'm not a linguist.
			if i == 0:
				f += "C"
			elif s[i-1] in VOWELS or (i != len(s) - 1 and s[i+1] in VOWELS):
				f += "C"
			else:
				f += "V"
		elif ch in VOWELS:
			f += "V"
		elif ch in LETTERS:
			f += "C"
		else:
			f += "?"
	return f

def addForm(formats, s):
	'''
	Adds to the counter for the VCF in `formats` if the string `s` is alphabetic
	'''
	form = getFormat(s)
	if "?" not in form:
		formats[form] = formats.get(form, 0) + 1

def addLineForms(formats, lines):
	'''
	Breaks each line into its words and increments their VCF counters
	'''
	for line in lines:
		line = line.lower().strip()
		if " " in line:
			for s in line.split(" "):
				addForm(formats, s)
		else:
			addForm(formats, line)

def getFormats(name_freq_min, infiles, outfile):
	'''
	Converts each word in the input files to its CVF and records how many times it occurs across all files.
	Formats which do not occur enough times or are too long (>12 characters) are excluded.
	The results are converted into probabilities for each format, then written out, optionally to the outfile
	'''
	formats = {}
	for filename in infiles:
		print("Reading from " + filename)
		lines = []
		with open(filename, "r") as f:
			lines = f.readlines()
		addLineForms(formats, lines)

	# strip out any names that do not appear enough times or are too long (shouldn't really happen anyway).
	remove = []
	for k in formats.keys():
		if formats[k] < name_freq_min or len(k) > NAME_LENGTH_LIMIT:
			remove.append(k)
	for r in remove:
		del formats[r]

	# turn counts of occurences into probabilities
	total = sum(formats.values())
	for k in formats:
		formats[k] /= total
	
	lengths = [0] * (NAME_LENGTH_LIMIT + 1)
	for k in formats.keys():
		lengths[len(k)] += 1

	printfile = None
	if outfile is not None:
		printfile = open(outfile, "w")
	print(formats, file=printfile)
	if printfile is not None:
		printfile.close()


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-split", "-s", is_flag=True, default=False, help="Split input CSV file")
@click.option("-formats", "-f", is_flag=True, default=False, help="get the CVFs in the input file and show the most common ones")
@click.option("-removechars", "-rc", is_flag=True, default=False, help="Remove undesirable characters from input text and overwrites the old text files.")
@click.option("-output", "-o", help="filepath to output data into")
@click.option("-minocc", "-mo", default=-1, help="Minimum number of name occurences to count")
@click.argument("inputfiles", nargs=-1)
def main(split, formats, removechars, output, minocc, inputfiles):
	modes = [split, formats, removechars]
	ct = sum([1 if m else 0 for m in modes])
	if ct > 1:
		print("Error: you can only pick one mode")
		exit(1)

	if formats:
		if minocc == -1:
			print("Error: You must specify a minimum number of name occurences.")
			exit(1)
		if len(inputfiles) == 0:
			print("Using default files " + str(DEFAULT_FORMAT_FILENAMES))
			inputfiles = DEFAULT_FORMAT_FILENAMES
		getFormats(minocc, inputfiles, output)
	elif removechars:
		if len(inputfiles) == 0:
			print("Error: give at least one input file.")
			exit(1)
		removeChars(inputfiles)
	elif split:
		if len(inputfiles) != 1:
			print("Error: missing CSV file or too many input files.")
			exit(1)
		if output is None:
			print("Error: missing output file.")
			exit(1)
		split_csv(inputfiles[0])


if __name__ == "__main__":
	main()