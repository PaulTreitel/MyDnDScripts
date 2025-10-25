import click

LETTERS = "abcdefghijklmnopqrstuvwxyz"
VOWELS = "aeiou"
INVALID_CHARS = "![]}{()@#$%^&*_+=\\|<>/?`0123456789;:~,'\""

# Number determined to be the maximum needed by trial and error (setting the min occurences quite low)
NAME_LENGTH_LIMIT = 12


@click.group()
def main():
	pass


@main.command("split")
@click.argument("inputCSV")
@click.argument("outputfile")
def split_csv(inputcsv, outputfile):
	'''
	Convert input CSV to text file of all ascii names
	'''
	lines = []
	with open(inputcsv, "rb") as f:
		print("Reading from " + inputcsv)
		lines = f.readlines()
	with open(outputfile, "wb") as f2:
		print("Writing to " + outputfile)
		for line in lines:
			try:
				out = line.decode("ascii").split(",")[0] + "\n"
				f2.write(out.encode("ascii"))
			except:
				pass

@main.command("remove")
@click.argument("inputfiles", nargs=-1)
def removeChars(inputfiles):
	'''
	Strip out lines containing undesirable characters
	'''
	for filename in inputfiles:
		input_lines = []
		output_lines = []
		with open(filename, "r") as f:
			print("Reading from " + filename)
			input_lines = f.readlines()
		for line in input_lines:
			if not contains_invalid_char(line):
				output_lines.append(line)
		with open(filename + ".new", "w") as f2:
			print("Writing to " + filename + ".new")
			f2.write("\n".join(output_lines))

@main.command("formats")
@click.option("-output", "-o", help="filepath to output data into")
@click.option("-minoccurences", "-mo", required=True, type=int, help="Required. Minimum number of occurences for a name format to count.")
@click.argument("inputfiles", nargs=-1, required=True)
def getFormats(minoccurences, inputfiles, output):
	'''
	outputs the frequency of consonant-vowel forms in input files
	'''
	# Converts each word in the input files to its CVF and records how many times it occurs across all files.
	# Formats which do not occur enough times or are too long (>12 characters) are excluded.
	# The results are converted into probabilities for each format, then written out, optionally to the output file.
	formats = {}
	for filename in inputfiles:
		print("Reading from " + filename)
		lines = []
		with open(filename, "r") as f:
			lines = f.readlines()
		addLineForms(formats, lines)

	# strip out any names that do not appear enough times or are too long (shouldn't really happen anyway).
	remove = []
	for k in formats.keys():
		if formats[k] < minoccurences or len(k) > NAME_LENGTH_LIMIT:
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
	if output is not None:
		printfile = open(output, "w")
	print(formats, file=printfile)
	if printfile is not None:
		printfile.close()

def contains_invalid_char(s):
	contains_char = False
	for ch in INVALID_CHARS:
		if ch in s:
			return True
	return False

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


if __name__ == "__main__":
	main()
