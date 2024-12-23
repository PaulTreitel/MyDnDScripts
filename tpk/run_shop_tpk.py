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
PROFIT_VALUES = [10, 15, 25, 55, 110, 220, 450, 1600, 3200, 8000]


def calculate_run_shop(int_lore, skill, diplomacy, sl, haul):
	dc10_expected = get_run_expected_value(DC10, int_lore, skill, diplomacy, sl, haul)
	dc15_expected = get_run_expected_value(DC15, int_lore, skill, diplomacy, sl, haul)
	dc20_expected = get_run_expected_value(DC20, int_lore, skill, diplomacy, sl, haul)
	dc25_expected = get_run_expected_value(DC25, int_lore, skill, diplomacy, sl, haul)
	print(f'DC10: {dc10_expected}\nDC15: {dc15_expected}\nDC20: {dc20_expected}\nDC25: {dc25_expected}')


def get_run_expected_value(dc, int_lore, skill, diplomacy, sl, haul):
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
				new_money = REWARD_VALUES[reward_level][successes] * PROFIT_VALUES[sl - 1]
				if haul and new_money < 0:
					new_money = new_money // 2
				total_value += new_money
	return total_value / NUM_POSS_ROLLS

def calculate_passive(sl, a, high_a, higher_a, haul, sister):
	total_value = 0
	for i in range(1, 101):
		new_money = get_passive_money(sl, i, a, high_a, higher_a)
		if sister and haul and new_money < 0:
			new_money += calculate_passive(sl, a, high_a, higher_a, haul, False)
		elif haul and new_money < 0:
			new_money = new_money // 2
		elif sister and new_money < 0:
			new_money += calculate_passive(sl, a, high_a, higher_a, haul, False)
		total_value += new_money
	expected_value = total_value / 100
	return expected_value

def  get_passive_money(sl, i, a, high_a, higher_a):
	new_money = 0
	if 1 <= i <= 20:
		new_money -= 10 * sl
	elif 21 <= i <= 30:
		new_money -= 5 * sl
	elif 31 <= i <= 40:
		new_money -= sl
	elif 61 <= i <= 80:
		if sl >= 7:
			new_money += sl * get_expected_roll(4, 8, a, high_a, higher_a, True)
		elif sl >= 4:
			new_money += sl * get_expected_roll(4, 8, a, high_a, higher_a, False)
		else:
			new_money += sl * get_expected_roll(2, 8, a, high_a, higher_a, False)
	elif 81 <= i <= 90:
		if sl >= 7:
			new_money += sl * get_expected_roll(4, 10, a, high_a, higher_a, True)
		elif sl >= 4:
			new_money += sl * get_expected_roll(4, 10, a, high_a, higher_a, False)
		else:
			new_money += sl * get_expected_roll(2, 10, a, high_a, higher_a, False)
	elif 91 <= i <= 100:
		if sl >= 7:
			new_money += sl * get_expected_roll(4, 12, a, high_a, higher_a, True)
		elif sl >= 4:
			new_money += sl * get_expected_roll(4, 12, a, high_a, higher_a, False)
		else:
			new_money += sl * get_expected_roll(2, 12, a, high_a, higher_a, False)
	return new_money

def get_expected_roll(dice, die_size, a, high_a, higher_a, double):
	roll = 0
	die_ev = (die_size + 1) / 2
	for i in range(dice):
		die_val = 0
		if higher_a:
			die_reroll_ev = sum([r for r in range(3, die_size + 1)]) / (die_size - 2)
			die_val += 2 * die_reroll_ev
		elif high_a:
			die_val += 2 * die_ev
		elif a:
			die_val += die_ev + 2
		else:
			die_val += 3

		for val in range(3, die_size + 1):
			die_val += val
		roll += die_val / die_size

	if double:
		roll = roll * 2
	return roll



@click.command(context_settings={"ignore_unknown_options": True})
@click.option('-mode', required=True, help='`run` to run shop, `passive` to do passive income')
@click.option('-i', default=0, help='Int/Lore skill modifier')
@click.option('-s', default=0, help='shop skill modifier')
@click.option('-d', default=0, help='Diplomacy modifier')
@click.option('-sl', default=1, help='Shop Level')
@click.option('-a', is_flag=True, help="flag for Assurance")
@click.option('-high_a', is_flag=True, help="flag for High Quality Assurance")
@click.option('-higher_a', is_flag=True, help="flag for Higher Qualityer Assurance")
@click.option('-haul', is_flag=True, help="flag for Last Week's Haul")
@click.option('-sister', is_flag=True, help="flag for Sister Location")
def handler(mode, i, s, d, sl, a, high_a, higher_a, haul, sister):
	if mode == 'run':
		calculate_run_shop(i, s, d, sl, haul)
	elif mode == 'passive':
		expected_value = calculate_passive(sl, a, high_a, higher_a, haul, sister)
		print('Expected value: {:.3f}'.format(expected_value))

if __name__ == '__main__':
	handler()
