import random


NUM_STATS = 6


def rollDice(num_dice, die_size):
	return [random.randint(1, die_size) for i in range(num_dice)]

def rollOneStat(num_dice, die_size, num_keep):
	'''
	Generates a stat using the normal "XdY drop lowest Z" format.

	num_dice - number of dice to roll
	die_size - the size of the dice to roll
	num_keep - how many of the rolled dice should be kept
	'''
	rolls = rollDice(die_size, num_dice)
	rolls.sort(reverse=True)
	total = 0
	for k in range(num_keep):
		total += rolls[k]
	return total

def rollNormalStats(num_dice, die_size, num_keep):
	'''Generates stats with a standard "XdY drop lowest Z" format.'''
	stats = []
	for i in range(NUM_STATS):
		statroll = rollOneStat(die_size, num_dice, num_keep)
		stats.append(statroll)
	return stats

def rollMixedDice(num_dice, die_size, num_keep):
	'''Generates stats with multiple die sizes. Unfortunately needs to be hardcoded.'''
	stats = []
	for i in range(NUM_STATS):
		d4 = rollOneStat(4, 2, 1)
		d6 = rollOneStat(6, 1, 1)
		d8 = rollOneStat(8, 2, 1)
		stats.append(d4 + d6 + d8)
	return stats

def rollStephStats(num_dice, die_size, num_keep):
	'''
	Simulates Steph's method of rolling stats for D&D.

	Steph's method is to roll 4d6, reroll at most one 1, and the sum of all
	stats must be between 70 and 80, inclusive.
	num_dice - number of dice to roll
	die_size - the size of the dice to roll
	num_keep - how many of the rolled dice should be kept
	Returns: a list of stat values
	'''
	STEPH_MIN = 70
	STEPH_MAX = 80
	stats = []
	while sum(stats) < STEPH_MIN or sum(stats) > STEPH_MAX:
		stats = []
		for i in range(NUM_STATS):
			rolls = rollDice(die_size, num_dice)
			if 1 in rolls:
				rolls.remove(1)
				rolls.append(rollDice(die_size, 1)[0])
			rolls.sort(reverse=True)
			total = 0
			for k in range(num_keep):
				total += rolls[k]
			stats.append(total)
	return stats

def runDiceTests(num_dice, die_size, num_keep, num_tests, rollfunc):
	'''
	Simulates stat generation multiple times.

	num_dice - number of dice to roll
	die_size - the size of the dice to roll
	num_keep - how many of the rolled dice should be kept
	num_tests - number of stat generations to simulate
	rollfunc - function for stat generation. It must take 3 integers
	as input and return a list of stat values.
	'''
	stat_results = [0 for i in range(21)]
	for i in range(num_tests):
		roll_res = rollfunc(die_size, num_dice, num_keep)
		if type(roll_res) is list:
			for stat in roll_res:
				stat_results[stat] += 1
	return stat_results

def recordResults(filename, stats, num_tests):
	'''Records the frequency of each stat value into a file in CSV format'''
	with open(filename, "w") as fn:
		for i in range(len(stats)):
			fn.write(str(i) +","+ str(stats[i] / (num_tests * NUM_STATS)) +"\n")



if __name__ == "__main__":
	SIZE = 6
	DICECOUNT = 4
	DICEKEEP = 3
	NUMTESTS = 100000
	OUTFILE = "out.csv"
	test_results = runDiceTests(4, 6, 3, NUMTESTS, rollNormalStats)
	recordResults(OUTFILE, test_results, NUMTESTS)
