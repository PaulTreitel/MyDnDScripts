import random

stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
totalrolls = 100000

numdice = 4
numkeep = 4
die_sides = 4
flip = True

for i in range(totalrolls):
	rolls = []
	for j in range(numdice):
		rolls.append(random.randint(1, die_sides))

	rolls.sort(reverse=True)
	total = 0
	for k in range(numkeep):
		total += rolls[k]
	if flip:
		if die_sides + 1 - rolls[-1] > rolls[-1]:
			total -= rolls[-1]
			total += die_sides + 1 - rolls[-1]

	stats[total] += 1

with open("out.txt", "w") as fn:
	for i in range(len(stats)):
		fn.write(str(i) +"\t"+ str(stats[i] / totalrolls) +"\n")