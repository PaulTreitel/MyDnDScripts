import random
import math
import json
import markov
import sys

'''
===Formatting Queries===
CLI call
names.py [datafile.json] -[first|last] -n [num]

analyze call
names.py -analyze -o [datafile.json] [infile.txt] ...

random CLI call
names.py -random -n [num] [infile.txt] ...
'''


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


# take the data collected about a corpus and save it into a JSON file
def exportAnalysis(filename, total_seen, state_table, text_names, start_letters):
	export = {"input_files":text_names, "start_letters":start_letters, "total_seen":total_seen, "state_table":state_table}
	with open(filename, "w") as fn:
		fn.write(json.dumps(export))


# take analysis from a JSON file and return it as a set of structures
def importAnalysis(filename):
	try:
		with open(filename, "r") as imp:
			obj = json.loads(imp.read())	
			return (obj["total_seen"], obj["state_table"], obj["start_letters"])
	except FileNotFoundError:
		print("failure! bad file!")
		exit(1)


# insert a new entry into the analysis tables
def tableInsert(state_table, total_seen, old, new):
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


# takes in the path of a text file, opens it ans analyzes the letters of the words in the file
# results are added to the state_table and total_seen lists
def analyzeText(filename, total_seen, state_table, start_letters):
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


# take line-by-line names and turn them into a list
def filesToList(filenames):
	names = []
	for fname in filenames:
		f = open(fname, "r")
		while True:
			l = f.readline()
			if not l:
				break
			names.append(l.strip())
		f.close()
	return names


# uses stored state table to calculate markov probabilities in-place
def calculateProbabilities(state_table, total_seen):
	for k in state_table.keys():
		for k2 in state_table[k].keys():
			state_table[k][k2] /= total_seen[k]


# generate a random letter with the distribution from the JSON start data
def getRandLetter(freq):
	val = random.random()
	s = 0
	for i in range(len(freq)):
		s += freq[i]
		if val <= s:
			return letters[i]


# checks if the form of a name is the first substring of the given form
# all forms are constonants (C) and vowels (V), ex "CCVVCV"
def formatsMatch(name, form):
	name_form = ""
	for ch in name:
		if ch in vowels:
			name_form += "V"
		elif ch in letters:
			name_form += "C"
		else:
			name_form += "?"
	return name_form == form[0:len(name_form)]


# transform in-place numbers of how many names start with each letter into probabilities
def getLetterFreq(start_letters):
	total = sum(start_letters)
	return [(1.0 * start_letters[i]) / (1.0 * total) for i in range(len(start_letters))]


# generate a name using forbidden start and format rules
def createNameRules(mk, freq, forms_used, prefix=''):
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


# create the configuration structures for the markov chain setup
def configureMarkov(datafile, use_last):
	total_seen, state_table, start_letters = importAnalysis(datafile)
	calculateProbabilities(state_table, total_seen)
	mk = markov.Markov(state_table, "")
	freq = getLetterFreq(start_letters)
	if use_last:
		return mk, freq, formats_last
	return mk, freq, formats_first


# converts command line arguments into a useful dictionary
def argsToDict():
	sys.argv.pop(0)
	args = {}
	if "-analyze" in sys.argv:
		args["call_type"] = "analyze"
		sys.argv.remove("-analyze")
	elif "-random" in sys.argv:
		args["call_type"] = "random"
		sys.argv.remove("-random")
	elif "-prefix" in sys.argv:
		args["call_type"] = "prefix"
		args["prefix"] = sys.argv[sys.argv.index('-prefix') + 1]
		sys.argv.pop(sys.argv.index('-prefix') + 1)
		sys.argv.remove('-prefix')
	else:
		args["call_type"] = "generate"

	if "-o" in sys.argv:
		sign_idx = sys.argv.index("-o")
		args["outfile"] = sys.argv[sign_idx + 1]
		sys.argv.pop(sign_idx + 1)
		sys.argv.pop(sign_idx)

	if "-n" in sys.argv:
		sign_idx = sys.argv.index("-n")
		if sys.argv[sign_idx + 1].isdigit():
			args["num"] = int(sys.argv[sign_idx + 1])
		sys.argv.pop(sign_idx + 1)
		sys.argv.pop(sign_idx)

	if "-first" in sys.argv:
		args["name_type"] = "first"
		sys.argv.remove("-first")
	elif "-last" in sys.argv:
		args["name_type"] = "last"
		sys.argv.remove("-last")

	if args["call_type"] == "generate" and len(sys.argv) > 0:
		args["datafile"] = sys.argv[0]
	elif args["call_type"] == "prefix" and len(sys.argv) > 0:
		args["datafile"] = sys.argv[0]
	else:
		args["input_files"] = sys.argv
	return args


#3 char sequences to block?
#hp, brn, bdn, wsh, nsj, chb, dhr, mrk, zdk, wch, dzh, nzd, lrh, trh
args = argsToDict()
if args["call_type"] == "generate":
	mk, freq, forms_used = configureMarkov(args["datafile"], args["name_type"] == "-last")
	for i in range(args["num"]):
		print(createNameRules(mk, freq, forms_used))

elif args["call_type"] == "analyze":
	total_seen = {}
	state_table = {}
	start_letters = [0] * 26
	for filename in args["input_files"]:
		analyzeText(filename, total_seen, state_table, start_letters)
	exportAnalysis(args["outfile"], total_seen, state_table, args["input_files"], start_letters)

elif args["call_type"] == "random":
	names = filesToList(args["input_files"])
	for i in range(args["num"]):
		print(random.choice(names))

elif args["call_type"] == "prefix":
	mk, freq, forms_used = configureMarkov(args["datafile"], args["name_type"] == "-last")
	for i in range(args["num"]):
		print(createNameRules(mk, freq, forms_used, args['prefix']))