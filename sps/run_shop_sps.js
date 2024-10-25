DCS = [15, 20, 30, 40];

NUM_POSS_ROLLS = 20**3;
REWARD_VALUES = [
	[-0.5, 0, 0.5, 1],
	[-2, 0, 1, 2],
	[-4, 0, 2, 4],
	[-10, 0, 5, 10]
];
PROFIT_VALUES = [16, 18, 25, 42, 75, 155, 290, 900, 1775, 3200];
REWARD_DC_15 = 0;
REWARD_DC_20 = 1;
REWARD_DC_30 = 2;
REWARD_DC_40 = 3;


/**
 * Computes the expected return of running a shop at a specific DC
 * @param {number} sr	   The Shop Rank, between 1 and 10.
 * @param {number} dc	   The DC, which must be 15, 20, 30, or 40.
 * @param {number} lore	 Your Lore Modifier.
 * @param {number} skill	Your Chosen Skill Modifier.
 * @param {number} charisma Your Charisma Skill Modifier.
 * @param {boolean} crits   [optional] Whether or not Business Expertise is active. Default false.
 * @param {boolean} haul	[optional] Whether or not Last Week's Haul is active. Default false.
 * @return The expected value of running the shop at that DC
 * @customfunction
*/
function RUNSHOP(sr, dc, lore, skill, charisma, haul=false, crits=false) {
	if (DCS.indexOf(dc) == -1) {
		throw "Invalid DC";
	}
	if (sr < 1 || sr > 10) {
		throw "Invalid Shop Rank";
	}
	return get_expected_value(sr, dc, lore, skill, charisma, haul, crits);
}

function get_expected_value(sr, dc, lore, skill, charisma, haul, crits) {
	let reward_level = DCS.indexOf(dc);
	let total_value = 0;
	for (let i = 1; i < 21; i++) {
		for (let s = 1; s < 21; s++) {
			for (let d = 1; d < 21; d++) {
				let successes = 0;

				if (i + lore >= dc) {
					successes += 1;
				}
				if (s + skill >= dc) {
					successes += 1;
				}
				if (d + charisma >= dc) {
					successes += 1;
				}

				if (crits) {
					let nat20_i = i == 20 && i + lore >= dc;
					let nat20_s = s == 20 && s + skill >= dc;
					let nat20_d = d == 20 && d + charisma >= dc;
					if (i + lore >= dc + 10 || nat20_i) {
						successes += 1;
					}
					if (s + skill >= dc + 10 || nat20_s) {
						successes += 1;
					}
					if (d + charisma >= dc + 10 || nat20_d) {
						successes += 1;
					}
				}
				successes = Math.min(successes, 3);
				
				let new_money = REWARD_VALUES[reward_level][successes] * PROFIT_VALUES[sr - 1];
				if (haul && new_money < 0) {
					new_money = new_money / 2;
				}
				total_value += new_money;
			}
		}
	}
	return total_value / NUM_POSS_ROLLS;
}

/**
 * Computes the expected return of a Passive Income roll given the Shop Rank and upgrades.
 * @param {number} sr	   The Shop Rank, between 1 and 10.
 * @param {number} assurance_level The type of assurance upgrade the shop has
 * * 0 for no assurance.
 * * 1 for Quality Assurance.
 * * 2 for High Quality Assurance.
 * * 3 for Higher Qualityer Assurance.
 * @param {boolean} haul	[optional] Whether or not Last Week's Haul is active. Default false.
 * @param {boolean} sister	[optional] Whether or not Sister Location is active. Default false.
 * @return The expected value of the shop's Passive Income roll.
 * @customfunction
*/
function PASSIVESHOP(sr, assurance_level, haul=false, sister=false) {
	if (sr < 1 || sr > 10) {
		throw "Invalid Shop Rank";
	}
	if (assurance_level < 0 || assurance_level > 3) {
		throw "Invalid Assurance Level";
	}
	let a = assurance_level == 1;
	let high_a = assurance_level == 2;
	let higher_a = assurance_level == 3;
	let total_value = 0;
	for (let roll = 1; roll < 101; roll++) {
		let new_money = get_passive_money(sr, roll, a, high_a, higher_a);
		if (sister && haul && new_money < 0) {
			new_money += PASSIVESHOP(sr, a, high_a, higher_a, haul, false);
		} else if (haul && new_money < 0) {
			new_money = new_money / 2;
		} else if (sister && new_money < 0) {
			new_money += PASSIVESHOP(sr, a, high_a, higher_a, haul, false);
		}
		total_value += new_money;
	}
	expected_value = total_value / 100;
	return expected_value
}

function get_passive_money(sr, d100_roll, a, high_a, higher_a) {
	let new_money = 0;
	if (1 <= d100_roll && d100_roll <= 20) {
		new_money -= 10 * sr;
	} else if (21 <= d100_roll && d100_roll <= 30) {
		new_money -= 5 * sr;
	} else if (31 <= d100_roll && d100_roll <= 40) {
		new_money -= sr;
	} else if (61 <= d100_roll && d100_roll <= 80) {
		if (sr >= 7) {
			new_money += sr * get_expected_roll(4, 8, a, high_a, higher_a, true);
		} else if (sr >= 4) {
			new_money += sr * get_expected_roll(4, 8, a, high_a, higher_a, false);
		} else {
			new_money += sr * get_expected_roll(2, 8, a, high_a, higher_a, false);
		}
	} else if (81 <= d100_roll && d100_roll <= 90) {
		if (sr >= 7) {
			new_money += sr * get_expected_roll(4, 10, a, high_a, higher_a, true);
		} else if (sr >= 4) {
			new_money += sr * get_expected_roll(4, 10, a, high_a, higher_a, false);
		} else {
			new_money += sr * get_expected_roll(2, 10, a, high_a, higher_a, false);
		}
	} else if (91 <= d100_roll && d100_roll <= 100) {
		if (sr >= 7) {
			new_money += sr * get_expected_roll(4, 12, a, high_a, higher_a, true);
		} else if (sr >= 4) {
			new_money += sr * get_expected_roll(4, 12, a, high_a, higher_a, false);
		} else {
			new_money += sr * get_expected_roll(2, 12, a, high_a, higher_a, false);
		}
	}
	return new_money
}

function get_expected_roll(dice, die_size, a, high_a, higher_a, double) {
	let roll = 0;
	let die_ev = (die_size + 1) / 2;
	for (let i = 0; i < dice; i++) {
		let total_poss_die_val = 0;
		for (let j = 1; j < die_size + 1; j++) {
			total_poss_die_val += get_die_effective_value(j, die_size, a, high_a, higher_a);
		}
		roll += total_poss_die_val / die_size;
	}

	if (double) {
		roll = roll * 2;
	}
	return roll;
}

function get_die_effective_value(base_value, die_size, a, high_a, higher_a) {
	// Takes the normal value on the die `base_value` and returns the effective
	// value after assurance upgrades.
	let die_ev = (die_size + 1) / 2;
	if (base_value <= 4 && higher_a) {
		let rerolls_with_keeps = [];
		for (let reroll = 1; reroll < die_size + 1; reroll++) {
			rerolls_with_keeps.push(Math.max(base_value, reroll));
		}
		let poss_keeps_rerolls = rerolls_with_keeps.reduce(
			(partialSum, a) => partialSum + a, 0);
		return poss_keeps_rerolls / die_size;
	} else if (base_value <= 2 && high_a) {
		return die_ev;
	} else if (base_value == 1 && a) {
		return die_ev;
	}
	return base_value;
}