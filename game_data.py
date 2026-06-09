"""游戏静态数据定义"""

DIFFICULTY_CONFIG = {
    "easy": {
        "name": "简单",
        "health": 120,
        "hunger": 100,
        "thirst": 100,
        "starting_items": {"water": 3, "food": 3, "bandage": 2},
        "event_chance": 0.2,
        "night_attack_chance": 0.15,
        "description": "充足的初始物资，较低的危险概率，适合新手"
    },
    "normal": {
        "name": "普通",
        "health": 100,
        "hunger": 100,
        "thirst": 100,
        "starting_items": {"water": 2, "food": 2, "bandage": 1},
        "event_chance": 0.35,
        "night_attack_chance": 0.3,
        "description": "标准难度，平衡的生存挑战"
    },
    "hard": {
        "name": "困难",
        "health": 80,
        "hunger": 80,
        "thirst": 80,
        "starting_items": {"water": 1, "food": 1},
        "event_chance": 0.5,
        "night_attack_chance": 0.5,
        "description": "有限的资源，频繁的危险，只有强者才能生存"
    },
    "nightmare": {
        "name": "噩梦",
        "health": 60,
        "hunger": 60,
        "thirst": 60,
        "starting_items": {},
        "event_chance": 0.7,
        "night_attack_chance": 0.7,
        "description": "极端环境，每一个决定都关乎生死"
    }
}

ITEMS = {
    "water": {"name": "水", "type": "consumable", "effect": {"thirst": 25}, "description": "干净的饮用水"},
    "dirty_water": {"name": "脏水", "type": "consumable", "effect": {"thirst": 15, "health": -10}, "description": "未净化的水，可能生病"},
    "food": {"name": "食物", "type": "consumable", "effect": {"hunger": 25}, "description": "煮熟的食物"},
    "raw_meat": {"name": "生肉", "type": "consumable", "effect": {"hunger": 10, "health": -15}, "description": "生肉，食用可能生病"},
    "raw_fish": {"name": "生鱼", "type": "consumable", "effect": {"hunger": 12, "health": -10}, "description": "生鱼，食用可能生病"},
    "berry": {"name": "浆果", "type": "consumable", "effect": {"hunger": 8, "thirst": 5}, "description": "野生浆果，可食用"},
    "coconut": {"name": "椰子", "type": "consumable", "effect": {"hunger": 15, "thirst": 20}, "description": "椰子，果肉和汁水都可食用"},
    "bandage": {"name": "绷带", "type": "medical", "effect": {"health": 30}, "description": "用于包扎伤口"},
    "herb": {"name": "草药", "type": "medical", "effect": {"health": 20}, "description": "具有治疗效果的草药"},
    "antidote": {"name": "解毒剂", "type": "medical", "effect": {"health": 15, "cure_poison": True}, "description": "可以解毒"},
    "wood": {"name": "木材", "type": "material", "description": "用于建造和制作"},
    "stone": {"name": "石头", "type": "material", "description": "用于建造和制作"},
    "fiber": {"name": "纤维", "type": "material", "description": "用于制作绳索和工具"},
    "vine": {"name": "藤蔓", "type": "material", "description": "可以编织成绳索"},
    "rope": {"name": "绳索", "type": "material", "description": "由纤维编织而成"},
    "iron_ore": {"name": "铁矿", "type": "material", "description": "可以冶炼成铁锭"},
    "iron_ingot": {"name": "铁锭", "type": "material", "description": "用于制作高级工具"},
    "coal": {"name": "煤炭", "type": "material", "description": "可以燃烧，用于冶炼"},
    "flint": {"name": "燧石", "type": "material", "description": "可以生火"},
    "shell": {"name": "贝壳", "type": "material", "description": "可以当作容器或交易品"},
    "axe": {"name": "石斧", "type": "tool", "durability": 20, "effect": {"gather_wood": 2}, "description": "提高木材采集效率"},
    "pickaxe": {"name": "石镐", "type": "tool", "durability": 20, "effect": {"gather_stone": 2}, "description": "提高石材采集效率"},
    "spear": {"name": "长矛", "type": "weapon", "durability": 15, "attack": 15, "description": "用于狩猎和防御"},
    "bow": {"name": "弓", "type": "weapon", "durability": 25, "attack": 20, "description": "远程攻击武器"},
    "arrow": {"name": "箭矢", "type": "ammo", "description": "弓的弹药"},
    "fishing_rod": {"name": "钓鱼竿", "type": "tool", "durability": 15, "effect": {"gather_fish": 2}, "description": "用于钓鱼"},
    "knife": {"name": "石刀", "type": "tool", "durability": 25, "effect": {"gather_fiber": 2}, "description": "提高纤维采集效率"},
    "torch": {"name": "火把", "type": "light", "durability": 5, "description": "夜间照明，驱赶野兽"},
    "iron_axe": {"name": "铁斧", "type": "tool", "durability": 50, "effect": {"gather_wood": 4}, "description": "高级木材采集工具"},
    "iron_sword": {"name": "铁剑", "type": "weapon", "durability": 40, "attack": 30, "description": "强力近战武器"},
    "compass": {"name": "指南针", "type": "tool", "description": "帮助探索，减少迷路概率"},
    "map_fragment": {"name": "地图碎片", "type": "special", "description": "遗迹中发现的地图碎片，收集完整可发现宝藏"},
    "ancient_coin": {"name": "古代钱币", "type": "special", "description": "神秘的古代钱币，可以交易"},
    "gold": {"name": "黄金", "type": "special", "description": "闪闪发光的黄金"},
    "brick": {"name": "砖块", "type": "material", "description": "烧制的砖块，用于高级建筑"},
    "charcoal": {"name": "木炭", "type": "material", "description": "烧制的木炭，高效燃料，用于冶炼和过滤"},
    "rain_collector": {"name": "雨水收集器", "type": "facility", "description": "自动收集雨水"},
}

RECIPES = {
    "axe": {"materials": {"wood": 2, "stone": 3, "fiber": 1}, "category": "tool"},
    "pickaxe": {"materials": {"wood": 2, "stone": 4, "fiber": 1}, "category": "tool"},
    "spear": {"materials": {"wood": 3, "stone": 2, "fiber": 2}, "category": "weapon"},
    "bow": {"materials": {"wood": 3, "fiber": 4}, "category": "weapon"},
    "arrow": {"materials": {"wood": 1, "stone": 1, "fiber": 1}, "category": "ammo", "quantity": 3},
    "fishing_rod": {"materials": {"wood": 3, "fiber": 5}, "category": "tool"},
    "knife": {"materials": {"stone": 2, "wood": 1, "fiber": 1}, "category": "tool"},
    "torch": {"materials": {"wood": 1, "fiber": 2}, "category": "light", "quantity": 2},
    "rope": {"materials": {"fiber": 4}, "category": "material", "quantity": 1},
    "bandage": {"materials": {"fiber": 3}, "category": "medical", "quantity": 2},
    "antidote": {"materials": {"herb": 3, "water": 1}, "category": "medical"},
    "iron_ingot": {"materials": {"iron_ore": 2, "charcoal": 1}, "category": "material", "require_fire": True},
    "iron_axe": {"materials": {"iron_ingot": 2, "wood": 2}, "category": "tool"},
    "iron_sword": {"materials": {"iron_ingot": 3, "wood": 1}, "category": "weapon"},
    "brick": {"materials": {"stone": 3, "wood": 1}, "category": "material", "require_fire": True, "quantity": 2},
    "charcoal": {"materials": {"wood": 3}, "category": "material", "require_fire": True, "quantity": 3},
}

COOKING_RECIPES = {
    "raw_meat": {"output": "food", "quantity": 1, "require_fire": True},
    "raw_fish": {"output": "food", "quantity": 1, "require_fire": True},
}

WATER_PURIFICATION = {
    "water": {"dirty_water": 1, "require_fire": True},
}

MAP_LOCATIONS = {
    "beach": {
        "name": "海滩",
        "description": "金色的沙滩，海浪拍打着岸边。可以找到贝壳、椰子和漂流物。",
        "resources": {"wood": 0.3, "fiber": 0.2, "vine": 0.2, "shell": 0.4, "coconut": 0.3, "dirty_water": 0.3},
        "danger": 0.1,
        "explorable": True,
    },
    "forest": {
        "name": "森林",
        "description": "茂密的丛林，充满了未知的危险和丰富的资源。",
        "resources": {"wood": 0.6, "stone": 0.2, "fiber": 0.5, "vine": 0.4, "berry": 0.4, "herb": 0.3, "flint": 0.15},
        "danger": 0.3,
        "explorable": True,
    },
    "river": {
        "name": "河流",
        "description": "清澈的河水，是淡水和鱼类的来源。",
        "resources": {"dirty_water": 0.6, "raw_fish": 0.4, "stone": 0.3, "fiber": 0.2, "vine": 0.2},
        "danger": 0.2,
        "explorable": True,
    },
    "mountain": {
        "name": "山脉",
        "description": "险峻的山峰，蕴藏着矿物资源，但也很危险。",
        "resources": {"stone": 0.6, "iron_ore": 0.3, "coal": 0.25, "flint": 0.3, "herb": 0.15},
        "danger": 0.5,
        "explorable": True,
    },
    "ruins": {
        "name": "古代遗迹",
        "description": "神秘的古代文明遗迹，可能藏有宝藏和危险。",
        "resources": {"stone": 0.3, "iron_ore": 0.2, "map_fragment": 0.2, "ancient_coin": 0.25, "gold": 0.1},
        "danger": 0.6,
        "explorable": True,
        "is_ruin": True,
    },
    "cave": {
        "name": "洞穴",
        "description": "黑暗的洞穴，可能有矿物和野生动物。",
        "resources": {"stone": 0.4, "iron_ore": 0.35, "coal": 0.3, "flint": 0.25},
        "danger": 0.45,
        "explorable": True,
    },
    "camp": {
        "name": "营地",
        "description": "你的安全基地，可以在这里休息和制作物品。",
        "resources": {},
        "danger": 0,
        "explorable": False,
    }
}

EVENTS = {
    "animal_attack": {
        "name": "野兽袭击",
        "type": "danger",
        "weight": 15,
        "min_damage": 15,
        "max_damage": 30,
        "can_defend": True,
        "message": "一只野兽突然向你扑来！",
    },
    "snake_bite": {
        "name": "毒蛇咬伤",
        "type": "danger",
        "weight": 10,
        "min_damage": 10,
        "max_damage": 20,
        "poison": True,
        "message": "你不小心踩到了一条毒蛇，它咬了你一口！",
    },
    "find_survivor": {
        "name": "发现幸存者",
        "type": "positive",
        "weight": 5,
        "message": "你发现了另一个幸存者！",
    },
    "find_cache": {
        "name": "发现物资",
        "type": "positive",
        "weight": 12,
        "message": "你发现了一个隐藏的物资箱！",
        "rewards": [
            {"water": 2, "food": 2},
            {"bandage": 2, "antidote": 1},
            {"iron_ore": 3, "coal": 2},
            {"ancient_coin": 5, "map_fragment": 1},
        ]
    },
    "rain": {
        "name": "降雨",
        "type": "weather",
        "weight": 12,
        "message": "天空开始下雨了。",
        "effect": {},
    },
    "storm": {
        "name": "暴风雨",
        "type": "weather",
        "weight": 10,
        "message": "一场暴风雨即将来临！",
        "effect": {"thirst": -10, "hunger": -10, "health": -5},
    },
    "heatwave": {
        "name": "热浪",
        "type": "weather",
        "weight": 8,
        "message": "异常炎热的天气，水分消耗加剧！",
        "effect": {"thirst": -20},
    },
    "cold_snap": {
        "name": "寒流",
        "type": "weather",
        "weight": 8,
        "message": "突然的寒流来袭，你需要保暖！",
        "effect": {"hunger": -15, "health": -5},
    },
    "trader": {
        "name": "流浪商人",
        "type": "trade",
        "weight": 6,
        "message": "一个流浪商人出现在附近，愿意与你交易。",
    },
    "injury": {
        "name": "意外受伤",
        "type": "danger",
        "weight": 10,
        "min_damage": 8,
        "max_damage": 15,
        "message": "你在行动中不小心受伤了。",
    },
    "good_luck": {
        "name": "好运",
        "type": "positive",
        "weight": 8,
        "message": "今天运气不错，你有了意外收获。",
        "rewards": [
            {"berry": 5, "coconut": 2},
            {"wood": 5, "stone": 3},
            {"herb": 3, "bandage": 1},
        ]
    },
}

COMPANIONS = {
    "hunter": {
        "name": "猎人",
        "description": "熟练的猎手，擅长狩猎和追踪。",
        "stats": {"attack": 15, "gather_bonus": 0.2},
        "recruit_cost": {"food": 10, "water": 5},
    },
    "gatherer": {
        "name": "采集者",
        "description": "经验丰富的采集者，收集资源效率高。",
        "stats": {"attack": 5, "gather_bonus": 0.5},
        "recruit_cost": {"food": 8, "water": 8},
    },
    "medic": {
        "name": "医生",
        "description": "懂得医术，可以治疗伤病。",
        "stats": {"attack": 3, "heal_bonus": 0.5},
        "recruit_cost": {"bandage": 5, "antidote": 2, "food": 5},
    },
    "scout": {
        "name": "侦察兵",
        "description": "机警的侦察兵，擅长探索和侦查。",
        "stats": {"attack": 8, "explore_bonus": 0.3, "danger_reduction": 0.2},
        "recruit_cost": {"food": 6, "water": 6, "rope": 2},
    },
    "blacksmith": {
        "name": "铁匠",
        "description": "熟练的铁匠，制作效率更高。",
        "stats": {"attack": 6, "craft_bonus": 0.4},
        "recruit_cost": {"iron_ingot": 3, "coal": 5, "food": 8},
    },
}

TRADER_ITEMS = {
    "buy": {
        "water": {"price": {"shell": 3}},
        "food": {"price": {"shell": 4}},
        "bandage": {"price": {"shell": 5}},
        "antidote": {"price": {"shell": 8}},
        "rope": {"price": {"shell": 4}},
        "compass": {"price": {"ancient_coin": 3}},
        "map_fragment": {"price": {"ancient_coin": 5}},
    },
    "sell": {
        "shell": {"price": 1},
        "ancient_coin": {"price": 5},
        "gold": {"price": 10},
        "iron_ore": {"price": 2},
        "iron_ingot": {"price": 6},
    }
}

RUIN_CLUES = {
    "old_camp": {
        "name": "旧营地遗迹",
        "description": "你发现了一个废弃的营地，看起来是之前遇难者留下的。",
        "discovery_chance": 0.25,
        "effect": {"bonus_find_cache": 0.3},
        "score_bonus": 10,
        "unlocks": ["diary_note"],
    },
    "secret_chamber": {
        "name": "神秘密室",
        "description": "你发现了一个隐藏的密室，墙上刻满了奇怪的符号。",
        "discovery_chance": 0.2,
        "requires": ["old_camp"],
        "effect": {"map_fragment_bonus": 0.2},
        "score_bonus": 15,
        "unlocks": ["treasure_hint"],
    },
    "trap_mechanism": {
        "name": "古代机关",
        "description": "你发现了一个复杂的机关装置，似乎需要特定的方法才能触发。",
        "discovery_chance": 0.15,
        "requires": ["secret_chamber"],
        "effect": {"trap_damage_reduction": 0.5},
        "score_bonus": 20,
    },
    "diary_note": {
        "name": "探险日记",
        "description": "一本破旧的日记，记录了前人在岛上的经历。",
        "discovery_chance": 0.2,
        "requires": ["old_camp"],
        "effect": {"companion_recruit_bonus": 0.2},
        "score_bonus": 10,
    },
    "treasure_map": {
        "name": "藏宝图残页",
        "description": "一张残缺的地图，上面标注了宝藏的大致位置。",
        "discovery_chance": 0.1,
        "requires": ["secret_chamber", "diary_note"],
        "effect": {"guaranteed_map_fragment": True},
        "score_bonus": 25,
    },
    "ancient_statue": {
        "name": "古代雕像",
        "description": "一座神秘的雕像，似乎在守护着什么重要的东西。",
        "discovery_chance": 0.12,
        "requires": ["secret_chamber"],
        "effect": {"night_defense_bonus": 0.2},
        "score_bonus": 15,
    },
}

CAMP_UPGRADES = {
    "shelter": {
        "name": "营地",
        "levels": [
            {"level": 1, "name": "简易营地", "cost": {"wood": 10, "stone": 5, "rope": 2}, "benefit": "提供基本庇护，夜间恢复+5生命", "unlocks": ["fire", "storage"], "effects": {"night_heal": 5, "defense": 0}},
            {"level": 2, "name": "加固营地", "cost": {"wood": 15, "stone": 10, "rope": 3}, "benefit": "更坚固的庇护，夜间恢复+8生命，防御+10", "unlocks": ["defense"], "effects": {"night_heal": 8, "defense": 10}},
            {"level": 3, "name": "坚固堡垒", "cost": {"wood": 20, "stone": 20, "rope": 5, "brick": 5, "iron_ingot": 2}, "benefit": "非常坚固，夜间恢复+12生命，防御+20，下雨也能休息", "unlocks": [], "effects": {"night_heal": 12, "defense": 20, "rain_proof": True}},
        ],
        "max_level": 3,
    },
    "fire": {
        "name": "火源",
        "levels": [
            {"level": 1, "name": "篝火", "cost": {"wood": 5, "flint": 2}, "benefit": "可以烹饪食物和净化水，夜间恢复+3生命", "unlocks": ["water_filter", "cooking"], "effects": {"night_heal": 3, "cooking_bonus": 0}},
            {"level": 2, "name": "石砌炉灶", "cost": {"stone": 10, "wood": 5}, "benefit": "烹饪效率+50%，可冶炼金属，夜间恢复+5生命", "unlocks": ["smelting"], "effects": {"night_heal": 5, "cooking_bonus": 0.5}},
            {"level": 3, "name": "砖石壁炉", "cost": {"stone": 20, "brick": 8, "charcoal": 3, "iron_ingot": 1}, "benefit": "烹饪效率+100%，冶炼效率+50%，夜间恢复+8生命，照明范围更大", "unlocks": [], "effects": {"night_heal": 8, "cooking_bonus": 1.0, "smelting_bonus": 0.5}},
        ],
        "max_level": 3,
        "requires": "shelter",
    },
    "storage": {
        "name": "仓库",
        "levels": [
            {"level": 1, "name": "简易货架", "cost": {"wood": 15, "rope": 3}, "benefit": "物品整理更有序，采集效率+10%", "unlocks": [], "effects": {"gather_bonus": 0.1}},
            {"level": 2, "name": "木板仓库", "cost": {"wood": 25, "rope": 5, "iron_ingot": 1}, "benefit": "更大的存储空间，采集效率+20%，物品不会因潮湿损坏", "unlocks": [], "effects": {"gather_bonus": 0.2, "moisture_proof": True}},
        ],
        "max_level": 2,
        "requires": "shelter",
    },
    "water_filter": {
        "name": "净水器",
        "levels": [
            {"level": 1, "name": "简易过滤器", "cost": {"wood": 5, "stone": 10, "fiber": 10}, "benefit": "净化脏水获得2倍净水", "unlocks": [], "effects": {"purify_multiplier": 2}},
            {"level": 2, "name": "多级过滤系统", "cost": {"stone": 15, "fiber": 20, "charcoal": 5, "brick": 3}, "benefit": "净化脏水获得3倍净水，雨天自动收集雨水", "unlocks": [], "effects": {"purify_multiplier": 3, "rain_collection": True}},
        ],
        "max_level": 2,
        "requires": "fire",
    },
    "defense": {
        "name": "防御设施",
        "levels": [
            {"level": 1, "name": "尖刺围栏", "cost": {"wood": 10, "stone": 15, "rope": 2}, "benefit": "夜间防御+10，野兽袭击概率-10%", "unlocks": [], "effects": {"defense": 10, "attack_reduction": 0.1}},
            {"level": 2, "name": "围墙", "cost": {"stone": 25, "wood": 15, "rope": 3, "brick": 5}, "benefit": "夜间防御+25，野兽袭击概率-25%", "unlocks": [], "effects": {"defense": 25, "attack_reduction": 0.25}},
            {"level": 3, "name": "瞭望塔", "cost": {"wood": 30, "stone": 30, "rope": 5, "brick": 10, "iron_ingot": 3}, "benefit": "夜间防御+50，野兽袭击概率-50%，提前1回合预警", "unlocks": [], "effects": {"defense": 50, "attack_reduction": 0.5, "early_warning": True}},
        ],
        "max_level": 3,
        "requires": "shelter",
    },
}

ENDINGS = {
    "rescue": {
        "name": "成功获救",
        "description": "你在荒岛上生存了足够长的时间，最终被路过的船只救起。",
        "condition": "survive_30_days",
        "score": 100,
    },
    "treasure": {
        "name": "找到宝藏",
        "description": "你收集齐了所有地图碎片，找到了古代宝藏，成为了传奇。",
        "condition": "collect_all_maps",
        "score": 150,
    },
    "build_boat": {
        "name": "造船逃离",
        "description": "你用自己的双手建造了一艘小船，成功离开了这座岛屿。",
        "condition": "build_boat",
        "score": 120,
    },
    "starve": {
        "name": "饥饿而死",
        "description": "你因为没有足够的食物而饿死在荒岛上。",
        "condition": "hunger_zero",
        "score": 20,
    },
    "dehydrate": {
        "name": "脱水而死",
        "description": "你因为缺水而死在了寻找水源的路上。",
        "condition": "thirst_zero",
        "score": 20,
    },
    "killed_by_beast": {
        "name": "死于野兽",
        "description": "你在与野兽的搏斗中不幸身亡。",
        "condition": "killed_by_animal",
        "score": 30,
    },
    "poisoned": {
        "name": "中毒身亡",
        "description": "你不幸中毒，没有及时找到解毒剂。",
        "condition": "poison_death",
        "score": 25,
    },
    "infection": {
        "name": "感染而死",
        "description": "你的伤口感染了，最终不治身亡。",
        "condition": "infection_death",
        "score": 30,
    },
}
