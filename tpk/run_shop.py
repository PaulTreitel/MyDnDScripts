import click

DC10 = 10
DC15 = 15
DC20 = 20
DC25 = 25
NUM_POSS_ROLLS = 20**3
REWARD_VALUES = [
	[-0.5, 0, 0.5, 1],
	[-2, 0, 1, 2],
	[-4, 0, 2, 4],
	[-10, 0, 5, 10]
]


@click.command()
@click.option('-i', default=0, help='Int/Lore skill modifier')
@click.option('-s', default=0, help='shop skill modifier')
@click.option('-d', default=0, help='Diplomacy modifier')
@click.option('-pv', default=10, help='Profit Value')
def calculate(i, s, d, pv):
	dc10_expected = get_expected_value(DC10, i, s, d, pv)
	dc15_expected = get_expected_value(DC15, i, s, d, pv)
	dc20_expected = get_expected_value(DC20, i, s, d, pv)
	dc25_expected = get_expected_value(DC25, i, s, d, pv)
	print(f'DC10: {dc10_expected}\nDC15: {dc15_expected}\nDC20: {dc20_expected}\nDC25: {dc25_expected}')


def get_expected_value(dc, int_lore, skill, diplomacy, pv):
	total_value = 0
	for i in range(1, 21):
		for s in range(1, 21):
			for d in range(1, 21):
				successes = 0
				if i + int_lore >= dc:
					successes += 1
				if s + skill >= dc:
					successes += 1
				if d + diplomacy >= dc:
					successes += 1
				reward_level = (dc - 10) // 5
				total_value += REWARD_VALUES[reward_level][successes] * pv
	return total_value / NUM_POSS_ROLLS

if __name__ == '__main__':
	calculate()