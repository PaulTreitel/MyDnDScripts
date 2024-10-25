import click

# starts at level 0
# standard level-based DCs
LEVEL_DCS = [14, 15, 16, 18, 19, 20, 22, 23, 24, 26, 27, 28, 30, 31, 32, 34,
	35, 36, 38, 39, 40]
# starts at level 1
# optimal bonuses as determined by RPGBOT
OPTIMAL_BONUSES = [7, 8, 12, 13, 14, 15, 18, 19, 22, 23, 24, 25, 26, 27, 30,
	31, 34, 35, 36, 38]
# starts at level 1
# magic item prices
ITEM_PRICES = [(10, 20), (25, 35), (45, 60), (75, 100), (125, 160), (200, 250),
	(300, 360), (415, 500), (575, 700), (825, 1000), (1160, 1400), (1640, 2000),
	(2400, 3000), (3600, 4500), (5300, 6500), (7900, 10_000), (12_000, 15_000),
	(18_600, 24_000), (30_400, 40_000), (52_000, 72_000)]

# DISCOUNTS = [0, 10, 20, 35, 50]
# DISCOUNTS = [0, 15, 30, 45, 60]
DISCOUNTS = [0, 20, 35, 45, 65]
CRAFT_BONUSES = [0, 1, 3, 5]
BELOW_ZERO_LOSS = 10
PARAM_NOT_ENTERED = -10
MAX_INGENUITY = 4

def make_craft(bonus, pc_level):
	print('Item Level\t 1 / 2 / 3 Downtimes\tgp Discounts')
	for item_level in range(min(21, pc_level + 1)):
		discount1_pctge = get_avg_discount(item_level, pc_level, bonus, 1)
		discount2_pctge = get_avg_discount(item_level, pc_level, bonus, 2)
		discount3_pctge = get_avg_discount(item_level, pc_level, bonus, 3)

		if item_level == 0:
			print('{:d}\t\t{:3.0f}% / {:3.0f}% / {:3.0f}%\t- / - / -'.format(
				item_level,
				discount1_pctge, discount2_pctge, discount3_pctge))
		else:
			prices = ITEM_PRICES[item_level - 1]
			discounts_gp = (
				prices[0] * discount1_pctge / 100, 
				prices[1] * discount1_pctge / 100,
				prices[0] * discount2_pctge / 100,
				prices[1] * discount2_pctge / 100,
				prices[0] * discount3_pctge / 100,
				prices[1] * discount3_pctge / 100
			)
			gp_discount_str = '({:.0f}-{:.0f}) / ({:.0f}-{:.0f}) / ({:.0f}-{:.0f})'.format(
				discounts_gp[0], discounts_gp[1], discounts_gp[2],
				discounts_gp[3], discounts_gp[4], discounts_gp[5])
			print('{:d}\t\t{:3.0f}% / {:3.0f}% / {:3.0f}%\t{:s}'.format(
				item_level,
				discount1_pctge, discount2_pctge, discount3_pctge,
				gp_discount_str))
	

def get_avg_discount(item_level, pc_level, bonus, downtimes):
	# create stack for each downtime of (ingenuity, loss)
	# next downtime will pop and run a new round
	if downtimes <= 0:
		return 0
	poss_outcomes = []
	for roll in range(1, 21):
		result = roll + bonus
		ingenuity = get_ingenuity_first_run(item_level, pc_level, roll, bonus)
		loss = 0.0
		if result <= LEVEL_DCS[item_level] - 10:
			loss = BELOW_ZERO_LOSS
		poss_outcomes.append((ingenuity, loss))

	for _ in range(downtimes - 1):
		new_poss_outcomes = []
		while len(poss_outcomes) > 0:
			current_baseline = poss_outcomes.pop()
			if current_baseline[0] == MAX_INGENUITY:
				for _ in range(20):
					new_poss_outcomes.append(current_baseline)
				continue
			new_baselines = extend_previous_craft_attempt(
				item_level, current_baseline, bonus)
			new_poss_outcomes.extend(new_baselines)
		poss_outcomes = new_poss_outcomes
	
	discounts = [DISCOUNTS[x[0]] - x[1] for x in poss_outcomes]
	return sum(discounts) / len(discounts)

def extend_previous_craft_attempt(item_level, baseline, bonus):
	new_attempts = []
	for roll in range(1, 21):
		result = roll + bonus + CRAFT_BONUSES[baseline[0]]
		delta_ingenuity = ingenuity_change_later_runs(item_level, roll, bonus)
		ingenuity = baseline[0]
		loss = baseline[1]
		if ingenuity == 0 and delta_ingenuity == -1:
			loss += BELOW_ZERO_LOSS
		else:
			ingenuity += delta_ingenuity
			ingenuity = min(ingenuity, MAX_INGENUITY)
		new_attempts.append((ingenuity, loss))
	return new_attempts

def get_ingenuity_first_run(item_level, pc_level, roll, bonus):
	check_result = roll + bonus
	nat20_crit = roll == 20 and check_result >= LEVEL_DCS[item_level]
	nat1_crit = roll == 1 and check_result <= LEVEL_DCS[item_level]

	if check_result >= LEVEL_DCS[item_level] + 10 or nat20_crit:
		if item_level <= pc_level / 2:
			return 4
		else:
			return 2
	elif check_result <= LEVEL_DCS[item_level] - 10 or nat1_crit:
		return 0
	elif check_result >= LEVEL_DCS[item_level]:
		if item_level <= pc_level / 4:
			return 4
		elif item_level <= pc_level / 2:
			return 2
		else:
			return 1
	else:
		return 0

def ingenuity_change_later_runs(item_level, roll, bonus):
	check_result = roll + bonus
	nat20_crit = roll == 20 and check_result >= LEVEL_DCS[item_level]
	nat1_crit = roll == 1 and check_result <= LEVEL_DCS[item_level]

	if check_result >= LEVEL_DCS[item_level] + 10 or nat20_crit:
		return 2
	elif check_result <= LEVEL_DCS[item_level] - 10 or nat1_crit:
		return -1
	elif check_result >= LEVEL_DCS[item_level]:
		return 1
	else:
		return 0


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('-lvl', required=True, default=PARAM_NOT_ENTERED, help='Player Character Level.')
@click.option('-craft', default=PARAM_NOT_ENTERED, help='Your Crafting bonus. If unspecified, the optimal bonus will be used.')
def handler(lvl, craft):
	if lvl == PARAM_NOT_ENTERED:
		return -1
	if lvl <= 0 or lvl > 20:
		print("Player character levels are 1-20")
		return -1
	if craft == PARAM_NOT_ENTERED:
		craft = OPTIMAL_BONUSES[lvl - 1]
	make_craft(craft, lvl)
	return 0

if __name__ == "__main__":
	handler()