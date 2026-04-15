from scripts.engine.difficulty import Difficulty

DIFFICULTY_SHIP_SETTINGS = {
    Difficulty.TOURIST: {
        "damage_taken_multiplier": 0.85,
        "damage_multiplier": 1.3,
        "shield_multiplier": 1.4,
        "hp_multiplier": 1.3,
        "heat_per_shot": 0,
        "cooldown_multiplier": 0.85,
        "evasion_bonus": 0.05,
        "crit_bonus": 0.05,
        "shield_regen_multiplier": 0.08,
        "ammo_multiplier": 1.5,
        "xp_growth": 2.0,
        "credits_multiplier": 1.0
    },
    Difficulty.EXPLORER: {
        "damage_taken_multiplier": 1.0,
        "damage_multiplier": 1.5,
        "shield_multiplier": 1.15,
        "hp_multiplier": 1.1,
        "heat_per_shot": 100,
        "cooldown_multiplier": 1.0,
        "evasion_bonus": 0.02,
        "crit_bonus": 0.02,
        "shield_regen_multiplier": 0.05,
        "ammo_multiplier": 1.2,
        "xp_growth": 1.8,
        "credits_multiplier": 1.2
    },
    Difficulty.PILOT: {
        "damage_taken_multiplier": 1.8,
        "damage_multiplier": 2.0,
        "shield_multiplier": 1.0,
        "hp_multiplier": 1.0,
        "heat_per_shot": 200,
        "cooldown_multiplier": 1.15,
        "evasion_bonus": 0.0,
        "crit_bonus": 0.0,
        "shield_regen_multiplier": 0.04,
        "ammo_multiplier": 1.0,
        "xp_growth": 1.5,
        "credits_multiplier": 1.5
    },
    Difficulty.NIGHTMARE: {
        "damage_taken_multiplier": 2.0,
        "damage_multiplier": 2.25,
        "shield_multiplier": 0.8,
        "hp_multiplier": 0.85,
        "heat_per_shot": 400,
        "cooldown_multiplier": 1.35,
        "evasion_bonus": -0.01,
        "crit_bonus": -0.02,
        "shield_regen_multiplier": 0.02,
        "ammo_multiplier": 0.8,
        "xp_growth": 0.85,
        "credits_multiplier": 2.0
    },
}

DIFFICULTY_ENEMY_SETTINGS = {
    Difficulty.TOURIST: {
        "hp_multiplier": 0.8,
        "damage_multiplier": 0.7,
        "fire_rate_multiplier": 0.8,
        "speed_multiplier": 0.9,
        "elite_chance": 0.03,
    },
    Difficulty.EXPLORER: {
        "hp_multiplier": 1.0,
        "damage_multiplier": 1.0,
        "fire_rate_multiplier": 1.0,
        "speed_multiplier": 1.0,
        "elite_chance": 0.05,
    },
    Difficulty.PILOT: {
        "hp_multiplier": 1.25,
        "damage_multiplier": 1.15,
        "fire_rate_multiplier": 1.2,
        "speed_multiplier": 1.2,
        "elite_chance": 0.08,
    },
    Difficulty.NIGHTMARE: {
        "hp_multiplier": 1.6,
        "damage_multiplier": 1.4,
        "fire_rate_multiplier": 1.5,
        "speed_multiplier": 1.4,
        "elite_chance": 0.12,
    },
}