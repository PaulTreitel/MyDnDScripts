import random
import math
import json
import markov
import sys
import click

# some important links
# http://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
# https://github.com/philipperemy/name-dataset
# https://www.quora.com/What-is-the-average-length-of-last-names-in-the-United-States
# https://www.quora.com/What-is-the-average-length-of-first-names-in-the-United-States


LETTERS = "abcdefghijklmnopqrstuvwxyz"
VOWELS = "aeiou"

DEFAULT_NUM_NAMES = 20
DEFAULT_JSON_DATAFILE = "data_names.json"

bad_starts = []
first_name_ordered = []
first_name_freqs = []
last_name_ordered = []
last_name_freqs = []

def loadSettings():
	global bad_starts
	global first_name_ordered
	global first_name_freqs
	global last_name_ordered
	global last_name_freqs
	with open("config.json", "r") as f:
		settings = json.loads(f.read())
		bad_starts = settings["bad_starts"]
		first_name_formats = settings["formats_first"]
		last_name_formats = settings["formats_last"]
		first_name_ordered = sorted(first_name_formats.keys())
		first_name_freqs = [first_name_formats[k] for k in first_name_ordered]
		last_name_ordered = sorted(last_name_formats.keys())
		last_name_freqs = [last_name_formats[k] for k in last_name_ordered]


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
	if ctx.invoked_subcommand is None:
		generateNames(DEFAULT_NUM_NAMES, False, None, DEFAULT_JSON_DATAFILE)

@main.command("prefix")
@click.option("-n", default=DEFAULT_NUM_NAMES, help=f"number of names to generate (default is {DEFAULT_NUM_NAMES})")
@click.option("-last", "-l", is_flag=True, default=False, help="generate last names (default is first names)")
@click.option("-output", "-o", help="filepath to output data into")
@click.option("-datafile", "-d", help=f"path to analyzed JSON data (default is `{DEFAULT_JSON_DATAFILE}`)")
@click.argument("prefix")
def prefix(n, last, output, datafile, prefix):
	'''
	Generate a set of names sharing a prefix
	'''
	generateNames(n, last, output, datafile, prefix)


@main.command("generate")
@click.option("-n", default=DEFAULT_NUM_NAMES, help=f"number of names to generate (default is {DEFAULT_NUM_NAMES})")
@click.option("-last", "-l", is_flag=True, default=False, help="generate last names (default is first names)")
@click.option("-output", "-o", help="filepath to output data into")
@click.option("-datafile", "-d", help=f"path to analyzed JSON data (default is `{DEFAULT_JSON_DATAFILE}`)")
def generate(n, last, output, datafile):
	generateNames(n, last, output, datafile)

def generateNames(n, last, output, datafile, prefix=None):
	'''
	Generate a set of names
	'''
	if datafile is None:
			datafile = DEFAULT_JSON_DATAFILE
	
	mk, freq = configureMarkov(datafile)
	
	printfile = None
	if output is not None:
		printfile = open(output, "w")
	for i in range(n):
		print(createNameRules(mk, freq, last, prefix), file=printfile)
	if printfile is not None:
		printfile.close()


@main.command("random")
@click.option("-n", default=DEFAULT_NUM_NAMES, help=f"number of names to generate (default {DEFAULT_NUM_NAMES})")
@click.option("-output", "-o", help="filepath to output data into")
@click.argument("inputfiles", nargs=-1, required=True)
def randomNames(n, output, inputfiles):
	'''
	Randomly select lines from the set of input file(s)
	'''
	names = []
	for fname in inputfiles:
		with open(fname, "r") as f:
			lines = f.readlines()
			names.extend([l.strip() for l in lines])

	printfile = None
	if output is not None:
		printfile = open(output, "w")
	for i in range(n):
		print(random.choice(names), file=printfile)
	if printfile is not None:
		printfile.close()

@main.command("analyze")
@click.option("-output", "-o", required=True, help="filepath to output data into")
@click.argument("inputfiles", nargs=-1, required=True)
def analyzeFiles(inputfiles, output):
	'''
	Analyze text of input file(s) then export it to a JSON file
	'''
	if output is None:
		print("Error: you must specify an output file")
		exit(1)
	if len(inputfiles) == 0:
		print("Error: you must specify at least one input file")
		exit(1)
	total_seen = {}
	state_table = {}
	start_letters = [0] * 26
	for filename in inputfiles:
		analyzeText(filename, total_seen, state_table, start_letters)
	exportAnalysis(output, total_seen, state_table, inputfiles, start_letters)


def exportAnalysis(filename, total_seen, state_table, text_names, start_letters):
	'''
	Take the probability tables collected from a corpus of text(s) and save it to a JSON file.
	'''
	export = {
		"input_files":text_names, 
		"start_letters":start_letters, 
		"total_seen":total_seen, 
		"state_table":state_table
	}
	with open(filename, "w") as fn:
		fn.write(json.dumps(export))


def importAnalysis(filename):
	'''
	Given a JSON file created by exporting analysis, load it into a set of data structures.
	'''
	try:
		with open(filename, "r") as imp:
			obj = json.loads(imp.read())	
			return obj["total_seen"], obj["state_table"], obj["start_letters"]
	except FileNotFoundError:
		print("failure! bad file!")
		exit(1)


def tableInsert(state_table, total_seen, old, new):
	'''
	Insert a new entry into the text analysis tables
	'''
	if old in state_table:
		state_table[old][new] = state_table[old].get(new, 0) + 1
	else:
		state_table[old] = {new : 1}
	total_seen[old] = total_seen.get(old, 0) + 1


def analyzeLetterSequence(state_table, total_seen, start_letters, line, k):
	'''
	Counts letter-sequence occurences in a single line of text
	'''
	old_state = ""
	for idx in range(len(line)):
		if len(old_state) < k and line[idx] in LETTERS:
			old_state += line[idx]
			if k == 1:
				start_letters[LETTERS.index(line[idx])] += 1
		elif line[idx] in LETTERS:
			tableInsert(state_table, total_seen, old_state, line[idx])
			if k == 1:
				break
			old_state = old_state[1:] + line[idx]


def analyzeText(filename, total_seen, state_table, start_letters):
	'''
	Takes a path to a text file, opens it, and analyzes the letter sequences of the words in it.
	Returns nothing, the state table and total seen list are updated.
	'''
	print(filename)
	lines = []
	with open(filename, "r") as f:
		lines = f.readlines()
	lines = [l.strip().lower() for l in lines]

	for line in lines:
		# analyze 1 and 2 letter states
		for k in range(1, 3):
			analyzeLetterSequence(state_table, total_seen, start_letters, line, k)
	f.close()


def getRandLetter(freq):
	'''
	Generate a random letter with the first letter probability distribution from the JSON start data.
	'''
	val = random.random()
	s = 0
	for i in range(len(freq)):
		s += freq[i]
		if val <= s:
			return LETTERS[i]


def getRandFormat(formats, format_freqs):
	'''
	Generate a random name format using the probabilities in the config JSON file
	'''
	val = random.random()
	s = 0
	for i in range(len(format_freqs)):
		s += format_freqs[i]
		if val <= s:
			return formats[i]


def formatsMatch(name, form):
	'''
	Checks if the form of a name is the first substring of the given form.
	All forms are constonants (C) and vowels (V), ex "CCVVCV".
	'''
	name_form = ""
	for ch in name:
		if ch in VOWELS:
			name_form += "V"
		elif ch in LETTERS:
			name_form += "C"
		else:
			name_form += "?"
	return name_form == form[0:len(name_form)]


def createNameRules(mk, freq, use_last, prefix=None):
	'''
	Generate a name using the Markov chain.
	The name will follow a consonant-vowel form randomly chosen among some that appear in the dataset.
	Certain 2-letter sequences are banned at the start of names for the sake of English pronouncability.
	Those sequences will be avoided.
	'''
	formats_list = first_name_ordered
	format_freqs = first_name_freqs
	if use_last:
		formats_list = last_name_ordered
		format_freqs = last_name_freqs

	form = ''
	name = ''
	if prefix is None:
		name = getRandLetter(freq)
		form = getRandFormat(formats_list, format_freqs)
	else:
		name = prefix
		form = getRandFormat(formats_list, format_freqs)

	# rule enforced on first char
	while not formatsMatch(name, form):
		if prefix is None:
			name = getRandLetter(freq)
		else:
			form = getRandFormat(formats_list, format_freqs)
	
	mk.setState(name)
	for i in range(len(form) - len(name)):
		mk.step()
		while mk.state[:2] in bad_starts or not formatsMatch(mk.state, form):
			mk.setState(mk.state[:-1])
			mk.step()
	return mk.state


def configureMarkov(datafile):
	'''
	Create the Markov chain and the necessary configuration structures.
	Information is read in from the provided pre-analyzed JSON file.
	'''
	total_seen, state_table, start_letters = importAnalysis(datafile)

	for k in state_table.keys():
		for k2 in state_table[k].keys():
			state_table[k][k2] /= total_seen[k]
	mk = markov.Markov(state_table, "")

	total = sum(start_letters)
	freq = [(1.0 * start_letters[i]) / (1.0 * total) for i in range(len(start_letters))]
	return mk, freq

#3 char sequences to block?
#hp, brn, bdn, wsh, nsj, chb, dhr, mrk, zdk, wch, dzh, nzd, lrh, trh

if __name__ == "__main__":
	loadSettings()
	main()