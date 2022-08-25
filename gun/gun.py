import json

# 1d10 + 1d10 for each 5 above AC

AC_VALUES = [15, 16, 17, 18, 19, 20, 21]
GUN_EXTRA_DIE_THRESHOLD = 5
AVG_GUN_DIE_RESULT = 5.5
OTHER_NUM_DICE = 3
AVG_OTHER_DIE_RESULT = 4.5


def gunLevelDamageVersusAC(atkmod, statmod, ac, lvl):
	dmg = 0
	for roll in range(1, 20):
		to_hit = roll + atkmod
		if to_hit >= ac:
			num_dice = 1 + ((to_hit - ac)//GUN_EXTRA_DIE_THRESHOLD)
			dmg += num_dice * AVG_GUN_DIE_RESULT + statmod

	# crits
	to_hit = 20 + atkmod
	num_dice = 2 * (1 + ((to_hit - ac)//GUN_EXTRA_DIE_THRESHOLD))
	dmg += num_dice * AVG_GUN_DIE_RESULT + statmod
	return dmg / 20


def gunExpectedDamage(lvl_stats):
	expected_damage = {}
	for lvl in lvl_stats.keys():
		level_damage = {}
		for ac in AC_VALUES:
			level_damage[str(ac)] = gunLevelDamageVersusAC(lvl_stats[lvl]["attack mod"], lvl_stats[lvl]["stat mod"], ac, int(lvl))
		expected_damage[lvl] = level_damage
	return expected_damage


def cantripDice(lvl):
	lvl = lvl % 100
	if lvl < 5:
		return 1
	elif lvl < 11:
		return 2
	elif lvl < 17:
		return 3
	else:
		return 4


def otherLevelDamageVersusAC(atkmod, statmod, ac, lvl):
	dmg = 0
	for roll in range(1, 20):
		to_hit = roll + atkmod
		if to_hit >= ac:
			dmg += OTHER_NUM_DICE * AVG_OTHER_DIE_RESULT

	# crits
	dmg += 2 * OTHER_NUM_DICE * AVG_OTHER_DIE_RESULT
	return dmg / 20


def otherExpectedDamage(lvl_stats):
	expected_damage = {}
	for lvl in lvl_stats.keys():
		level_damage = {}
		for ac in AC_VALUES:
			level_damage[str(ac)] = otherLevelDamageVersusAC(lvl_stats[lvl]["attack mod"], lvl_stats[lvl]["stat mod"], ac, int(lvl))
		expected_damage[lvl] = level_damage
	return expected_damage



stat_data = open('statdata.json', 'r')
lvl_stats = json.loads(stat_data.read())
stat_data.close()

gun_dmg = gunExpectedDamage(lvl_stats)
for lvl in gun_dmg.keys():
	print('{}\t{}'.format(lvl, gun_dmg[lvl]))

print('\n\n')

other_dmg = otherExpectedDamage(lvl_stats)
for lvl in other_dmg.keys():
	print('{}\t{}'.format(lvl, other_dmg[lvl]))