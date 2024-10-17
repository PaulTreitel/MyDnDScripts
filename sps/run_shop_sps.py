import click

DCS = [15, 20, 30, 40]

NUM_POSS_ROLLS = 20**3
REWARD_VALUES = [
	[-0.5, 0, 0.5, 1],
	[-2, 0, 1, 2],
	[-4, 0, 2, 4],
	[-10, 0, 5, 10]
]
PROFIT_VALUES = [16, 18, 25, 42, 75, 155, 290, 900, 1775, 3200]
REWARD_DC_15 = 0
REWARD_DC_20 = 1
REWARD_DC_30 = 2
REWARD_DC_40 = 3


def calculate_run_shop(lore, skill, diplomacy, sr, haul, lvl):
	dc_15_ev = run_expected_value(DCS[0], lore, skill, diplomacy, sr, haul, REWARD_DC_15)
	dc_20_ev = run_expected_value(DCS[1], lore, skill, diplomacy, sr, haul, REWARD_DC_20)
	dc_30_ev = run_expected_value(DCS[2], lore, skill, diplomacy, sr, haul, REWARD_DC_30)
	dc_40_ev = run_expected_value(DCS[3], lore, skill, diplomacy, sr, haul, REWARD_DC_40)
	print('DC 15: %f\nDC 20: %f\nDC 30: %f\nDC 40: %f'
		%(dc_15_ev, dc_20_ev, dc_30_ev, dc_40_ev))


def run_expected_value(dc, lore, skill, diplomacy, sr, haul, reward_level, crits):
	total_value = 0
	for i in range(1, 21):
		for s in range(1, 21):
			for d in range(1, 21):
				successes = 0

				if i + lore >= dc:
					successes += 1
				if s + skill >= dc:
					successes += 1
				if d + diplomacy >= dc:
					successes += 1

				if crits:
					if i + lore >= dc + 10:
						successes += 1
					if s + skill >= dc + 10:
						successes += 1
					if d + diplomacy >= dc + 10:
						successes += 1
				successes = min(successes, 3)
				
				new_money = REWARD_VALUES[reward_level][successes] * PROFIT_VALUES[sr - 1]
				if haul and new_money < 0:
					new_money = new_money // 2
				total_value += new_money
	return total_value / NUM_POSS_ROLLS

def calculate_passive(sr, a, high_a, higher_a, haul, sister):
	total_value = 0
	for i in range(1, 101):
		new_money = get_passive_money(sr, i, a, high_a, higher_a)
		if sister and haul and new_money < 0:
			new_money += calculate_passive(sr, a, high_a, higher_a, haul, False)
		elif haul and new_money < 0:
			new_money = new_money // 2
		elif sister and new_money < 0:
			new_money += calculate_passive(sr, a, high_a, higher_a, haul, False)
		total_value += new_money
	expected_value = total_value / 100
	return expected_value

def  get_passive_money(sr, i, a, high_a, higher_a):
	new_money = 0
	if 1 <= i <= 20:
		new_money -= 10 * sr
	elif 21 <= i <= 30:
		new_money -= 5 * sr
	elif 31 <= i <= 40:
		new_money -= sr
	elif 61 <= i <= 80:
		if sr >= 7:
			new_money += sr * get_expected_roll(4, 8, a, high_a, higher_a, True)
		elif sr >= 4:
			new_money += sr * get_expected_roll(4, 8, a, high_a, higher_a, False)
		else:
			new_money += sr * get_expected_roll(2, 8, a, high_a, higher_a, False)
	elif 81 <= i <= 90:
		if sr >= 7:
			new_money += sr * get_expected_roll(4, 10, a, high_a, higher_a, True)
		elif sr >= 4:
			new_money += sr * get_expected_roll(4, 10, a, high_a, higher_a, False)
		else:
			new_money += sr * get_expected_roll(2, 10, a, high_a, higher_a, False)
	elif 91 <= i <= 100:
		if sr >= 7:
			new_money += sr * get_expected_roll(4, 12, a, high_a, higher_a, True)
		elif sr >= 4:
			new_money += sr * get_expected_roll(4, 12, a, high_a, higher_a, False)
		else:
			new_money += sr * get_expected_roll(2, 12, a, high_a, higher_a, False)
	return new_money

def get_expected_roll(dice, die_size, a, high_a, higher_a, double):
	roll = 0
	die_ev = (die_size + 1) / 2
	for i in range(dice):
		total_poss_die_val = 0
		for j in range(1, die_size + 1):
			total_poss_die_val += get_die_effective_value(j, die_size, a, high_a, higher_a)
		roll += total_poss_die_val / die_size

	if double:
		roll = roll * 2
	return roll

def get_die_effective_value(base_value, die_size, a, high_a, higher_a):
	'''
	Takes the normal value on the die `base_value` and returns the effective
	value after assurance upgrades.
	'''
	die_ev = (die_size + 1) / 2
	if base_value <= 4 and higher_a:
		poss_rerolls_with_keeps = sum(
			[max(base_value, reroll) for reroll in range(1, die_size + 1)]
		)
		return poss_rerolls_with_keeps / die_size
	elif base_value <= 2 and high_a:
		return die_ev
	elif base_value == 1 and a:
		return die_ev
	return base_value


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('-mode', required=True, help='`run` to run shop, `passive` to do passive income')
@click.option('-i', default=0, help='Int/Lore skill modifier')
@click.option('-s', default=0, help='Shop skill modifier')
@click.option('-d', default=0, help='Diplomacy modifier')
@click.option('-l', default=1, help='Character level')
@click.option('-sr', default=1, help='Shop Rank')
@click.option('-a', is_flag=True, help="flag for Assurance")
@click.option('-high_a', is_flag=True, help="flag for High Quality Assurance")
@click.option('-higher_a', is_flag=True, help="flag for Higher Qualityer Assurance")
@click.option('-haul', is_flag=True, help="flag for Last Week's Haul")
@click.option('-sister', is_flag=True, help="flag for Sister Location")
@click.option('-crits', is_flag=True, help="flag for Business Expertise")
def handler(mode, i, s, d, l, sr, a, high_a, higher_a, haul, sister, crits):
	if mode == 'run':
		calculate_run_shop(i, s, d, sr, haul, l, crits)
	elif mode == 'passive':
		expected_value = calculate_passive(sr, a, high_a, higher_a, haul, sister)
		print('Expected value: {:.3f}'.format(expected_value))


if __name__ == '__main__':
	handler()
