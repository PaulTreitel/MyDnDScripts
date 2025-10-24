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

start = open("config.json", "r")
configdump = json.loads(start.read())
start.close()


letters = "abcdefghijklmnopqrstuvwxyz"
vowels = "aeiou"
formats_first = configdump["formats_first"]
formats_last = configdump["formats_last"]
bad_starts = configdump["bad_starts"]


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
		if new in state_table[old]:
			state_table[old][new] += 1
		else:
			state_table[old][new] = 1
	else:
		state_table[old] = {new : 1}

	if old in total_seen:
		total_seen[old] += 1
	else:
		total_seen[old] = 1


def analyzeText(filename, total_seen, state_table, start_letters):
	'''
	Takes a path to a text file, opens it, and analyzes the letter sequences of the words in it.
	Returns nothing, the state table and total seen list are updated.
	'''
	print(filename)
	f = open(filename, "r")
	while True:
		line = f.readline().strip().lower()
		if not line:
			break

		for k in range(1, 3): # analyze 1 and 2 letter states
			old_state = ""
			for idx in range(len(line)):
				if len(old_state) < k and line[idx] in letters:
					old_state = old_state + line[idx]
					if k == 1:
						start_letters[letters.index(line[idx])] += 1
				elif line[idx] in letters:
					tableInsert(state_table, total_seen, old_state, line[idx])
					if k == 1:
						break
					old_state = old_state[1:] + line[idx]


def filesToList(filenames):
	'''
	Given a series of filepaths, load each line of text of all of them into a single list.
	'''
	names = []
	for fname in filenames:
		with open(fname, "r") as f:
			while True:
				l = f.readline()
				if not l:
					break
				names.append(l.strip())
	return names


def calculateProbabilities(state_table, total_seen):
	'''
	Converts state table from counts of each letter-sequence occurrence to the probabilities of each occurence.
	This is necessary for it to be used by the Markov chain.
	'''
	for k in state_table.keys():
		for k2 in state_table[k].keys():
			state_table[k][k2] /= total_seen[k]


def getRandLetter(freq):
	'''
	Generate a random letter with the first letter probability distribution from the JSON start data.
	'''
	val = random.random()
	s = 0
	for i in range(len(freq)):
		s += freq[i]
		if val <= s:
			return letters[i]


def formatsMatch(name, form):
	'''
	Checks if the form of a name is the first substring of the given form.
	All forms are constonants (C) and vowels (V), ex "CCVVCV".
	'''
	name_form = ""
	for ch in name:
		if ch in vowels:
			name_form += "V"
		elif ch in letters:
			name_form += "C"
		else:
			name_form += "?"
	return name_form == form[0:len(name_form)]


def getLetterFreq(start_letters):
	'''
	Transform in-place counts of how many names start with each letter into probabilities
	'''
	total = sum(start_letters)
	return [(1.0 * start_letters[i]) / (1.0 * total) for i in range(len(start_letters))]


def createNameRules(mk, freq, forms_used, prefix=''):
	'''
	Generate a name using the Markov chain.
	The name will follow a consonant-vowel form randomly chosen among some that appear in the dataset.
	Certain 2-letter sequences are banned at the start of names for the sake of English pronouncability.
	Those sequences will be avoided.
	'''
	form = ''
	name = ''
	if prefix == '':
		form = random.choice(forms_used)
		name = getRandLetter(freq)
	else:
		name = prefix
		form = random.choice(forms_used)

	while not formatsMatch(name, form): # rule enforced on first char
		if prefix == '':
			name = getRandLetter(freq)
		else:
			form = random.choice(forms_used)
	
	mk.setState(name)
	for i in range(len(form) - len(name)):
		mk.step()
		while mk.state[:2] in bad_starts or not formatsMatch(mk.state, form):
			mk.setState(mk.state[:-1])
			mk.step()
	return mk.state


def configureMarkov(datafile, use_last):
	'''
	Create the Markov chain and the necessary configuration structures.
	Information is read in from the provided pre-analyzed JSON file.
	'''
	total_seen, state_table, start_letters = importAnalysis(datafile)
	calculateProbabilities(state_table, total_seen)
	mk = markov.Markov(state_table, "")
	freq = getLetterFreq(start_letters)
	if use_last:
		return mk, freq, formats_last
	return mk, freq, formats_first


def analyzeFiles(inputfiles, outfile):
	'''
	Analyzes the combined text of a set of input file(s) then exports it into a JSON file.
	'''
	if outfile is None:
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
	exportAnalysis(outfile, total_seen, state_table, inputfiles, start_letters)


def generateNames(inputfiles, outfile, n, prefix=None):
	'''
	Randomly generates a list of names using input JSON data, optionally writing it to a file.
	Optionally, the names can all begin with a shared prefix.
	'''
	if len(inputfiles) == 0:
			inputfiles = ["data_names.json"]
	if len(inputfiles) > 1:
		print("Error: generating names requires a single JSON input file.")
		exit(1)
	mk, freq, forms_used = configureMarkov(inputfiles[0], False)

	printfile = None
	if outfile is not None:
		printfile = open(outfile, "w")
	for i in range(n):
		print(createNameRules(mk, freq, forms_used, prefix), file=printfile)
	if printfile is not None:
		printfile.close()


def randomNames(inputfiles, outfile, n):
	'''
	Randomly select lines from the set of input file(s), optionally writing it to a file.
	'''
	if len(inputfiles) == 0:
		print("Error: you must specify at least one input file")
		exit(1)
	names = filesToList(inputfiles)
	printfile = None
	if outfile is not None:
		printfile = open(outfile, "w")
	for i in range(n):
		print(random.choice(names), file=printfile)
	if printfile is not None:
		printfile.close()


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-generate", is_flag=True, help="(default) generate names. INPUTFILES should be a single JSON file generated by the `analyze` command.")
@click.option("-prefix", nargs=1, help="generate a set of names with a fixed prefix. INPUTFILES should be a single JSON file generated by the `analyze` command.")
@click.option("-analyze", is_flag=True, help="analyze a set of input texts into a JSON dump used to generate names. INPUTFILES should be 1 or more text files.")
@click.option("-random", is_flag=True, help="select random names from input texts. INPUTFILES should be 1 or more text files.")
@click.option("-o", help="filepath to output data into")
@click.option("-n", default=20, help="number of names to generate (default 20)")
@click.argument("inputfiles", nargs=-1)
def main(generate, analyze, prefix, random, o, n, inputfiles):
	outfile = o
	
	# Ensure that the user has only entered one possible mode (zero modes = generate).
	modes = [generate, analyze, prefix, random]
	ct = sum([1 if m else 0 for m in modes])
	if ct > 1:
		print("Error: you can only pick one mode")
		exit(1)
	
	if analyze:
		analyzeFiles(inputfiles, outfile)
	elif prefix is not None:
		generateNames(inputfiles, outfile, n, prefix=prefix)
	elif random:
		randomNames(inputfiles, outfile, n)
	else: # generate
		generateNames(inputfiles, outfile, n)

#3 char sequences to block?
#hp, brn, bdn, wsh, nsj, chb, dhr, mrk, zdk, wch, dzh, nzd, lrh, trh

if __name__ == "__main__":
	main()