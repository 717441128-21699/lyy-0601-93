"""游戏状态管理"""

import json
import os
import random
from datetime import datetime
from game_data import (
    DIFFICULTY_CONFIG, ITEMS, RECIPES, MAP_LOCATIONS, 
    EVENTS, COMPANIONS, TRADER_ITEMS, ENDINGS, RUIN_CLUES, CAMP_UPGRADES
)

SAVE_DIR = "saves"

class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_name = ""
        self.difficulty = "normal"
        self.health = 100
        self.max_health = 100
        self.hunger = 100
        self.thirst = 100
        self.day = 1
        self.turn = 1
        self.time_of_day = "day"
        self.current_location = "camp"
        self.inventory = {}
        self.tools = {}
        self.companions = []
        self.camp = {
            "built": False,
            "has_fire": False,
            "has_water_filter": False,
            "has_storage": False,
            "defense_level": 0,
            "torches": 0,
            "shelter_level": 0,
            "fire_level": 0,
            "storage_level": 0,
            "water_filter_level": 0,
            "defense_upgrade_level": 0,
        }
        self.is_poisoned = False
        self.poison_damage = 0
        self.is_infected = False
        self.map_fragments = 0
        self.total_map_fragments = 5
        self.boat_parts = 0
        self.total_boat_parts = 3
        self.ruin_clues = {}
        self.ruin_exploration_progress = 0
        self.battle_log = []
        self.score = 0
        self.death_cause = None
        self.game_over = False
        self.victory = False
        self.ending = None
        self.action_log = []
        self.event_log = []
        self.trader_available = False
        self.weather = "clear"
        self.weather_forecast = None

    def new_game(self, player_name, difficulty="normal"):
        self.reset()
        self.player_name = player_name
        self.difficulty = difficulty
        config = DIFFICULTY_CONFIG[difficulty]
        self.health = config["health"]
        self.max_health = config["health"]
        self.hunger = config["hunger"]
        self.thirst = config["thirst"]
        self.inventory = dict(config["starting_items"])
        self.log_action(f"开始新游戏，难度：{config['name']}")
        return f"欢迎来到荒岛求生，{player_name}！\n你在一场海难后醒来，发现自己身处一座荒岛上。\n目标：生存30天等待救援，或找到逃离岛屿的方法。\n输入 help 查看命令帮助。"

    def log_action(self, action):
        timestamp = f"第{self.day}天 {self.time_of_day} 回合{self.turn}"
        self.action_log.append(f"[{timestamp}] {action}")
        if len(self.action_log) > 100:
            self.action_log = self.action_log[-100:]

    def log_event(self, event):
        timestamp = f"第{self.day}天 {self.time_of_day} 回合{self.turn}"
        self.event_log.append(f"[{timestamp}] {event}")
        if len(self.event_log) > 50:
            self.event_log = self.event_log[-50:]

    def add_item(self, item_id, quantity=1):
        if item_id in ITEMS:
            if ITEMS[item_id]["type"] in ["tool", "weapon", "light"]:
                if item_id not in self.tools:
                    self.tools[item_id] = {"durability": ITEMS[item_id]["durability"], "quantity": quantity}
                else:
                    self.tools[item_id]["quantity"] += quantity
            else:
                if item_id not in self.inventory:
                    self.inventory[item_id] = 0
                self.inventory[item_id] += quantity
            
            if item_id == "map_fragment":
                self._sync_map_fragments()
                self._check_treasure_ending()
            
            return True
        return False
    
    def _sync_map_fragments(self):
        """同步地图碎片进度，确保 inventory 中的数量和 map_fragments 一致"""
        inv_count = self.inventory.get("map_fragment", 0)
        if inv_count != self.map_fragments:
            self.map_fragments = inv_count
    
    def _check_treasure_ending(self):
        """检查是否收集齐所有地图碎片，触发宝藏结局"""
        if self.map_fragments >= self.total_map_fragments and not self.game_over:
            self.victory = True
            self.ending = "treasure"
            self.game_over = True
            self.calculate_score()
            return True
        return False
    
    def _migrate_old_camp_data(self):
        """迁移旧存档的营地数据到新的升级系统"""
        if "shelter_level" not in self.camp:
            self.camp["shelter_level"] = 1 if self.camp.get("built", False) else 0
        if "fire_level" not in self.camp:
            self.camp["fire_level"] = 1 if self.camp.get("has_fire", False) else 0
        if "water_filter_level" not in self.camp:
            self.camp["water_filter_level"] = 1 if self.camp.get("has_water_filter", False) else 0
        if "storage_level" not in self.camp:
            self.camp["storage_level"] = 1 if self.camp.get("has_storage", False) else 0
        if "defense_upgrade_level" not in self.camp:
            self.camp["defense_upgrade_level"] = self.camp.get("defense_level", 0)
        
        self.camp["built"] = self.camp["shelter_level"] > 0
        self.camp["has_fire"] = self.camp["fire_level"] > 0
        self.camp["has_water_filter"] = self.camp["water_filter_level"] > 0
        self.camp["has_storage"] = self.camp["storage_level"] > 0
        self.camp["defense_level"] = self.camp["defense_upgrade_level"]
    
    def get_facility_effect(self, effect_name):
        """获取所有设施的指定效果总和"""
        total = 0
        for facility_id in CAMP_UPGRADES:
            level = self.get_camp_upgrade_level(facility_id)
            if level > 0:
                level_data = CAMP_UPGRADES[facility_id]["levels"][level - 1]
                if "effects" in level_data and effect_name in level_data["effects"]:
                    value = level_data["effects"][effect_name]
                    if isinstance(value, (int, float)):
                        total += value
        return total
    
    def has_facility_flag(self, flag_name):
        """检查是否有设施开启了指定的功能标志"""
        for facility_id in CAMP_UPGRADES:
            level = self.get_camp_upgrade_level(facility_id)
            if level > 0:
                level_data = CAMP_UPGRADES[facility_id]["levels"][level - 1]
                if "effects" in level_data and level_data["effects"].get(flag_name, False):
                    return True
        return False

    def remove_item(self, item_id, quantity=1):
        if ITEMS[item_id]["type"] in ["tool", "weapon", "light"]:
            if item_id in self.tools and self.tools[item_id]["quantity"] >= quantity:
                self.tools[item_id]["quantity"] -= quantity
                if self.tools[item_id]["quantity"] <= 0:
                    del self.tools[item_id]
                return True
        else:
            if item_id in self.inventory and self.inventory[item_id] >= quantity:
                self.inventory[item_id] -= quantity
                if self.inventory[item_id] <= 0:
                    del self.inventory[item_id]
                
                if item_id == "map_fragment":
                    self._sync_map_fragments()
                
                return True
        return False

    def has_item(self, item_id, quantity=1):
        if ITEMS[item_id]["type"] in ["tool", "weapon", "light"]:
            return item_id in self.tools and self.tools[item_id]["quantity"] >= quantity
        return item_id in self.inventory and self.inventory[item_id] >= quantity

    def get_item_count(self, item_id):
        if ITEMS[item_id]["type"] in ["tool", "weapon", "light"]:
            return self.tools.get(item_id, {}).get("quantity", 0)
        return self.inventory.get(item_id, 0)

    def use_tool(self, tool_id):
        if tool_id in self.tools:
            self.tools[tool_id]["durability"] -= 1
            if self.tools[tool_id]["durability"] <= 0:
                self.tools[tool_id]["quantity"] -= 1
                if self.tools[tool_id]["quantity"] <= 0:
                    del self.tools[tool_id]
                    self.log_event(f"你的{ITEMS[tool_id]['name']}损坏了！")
                    return False, f"{ITEMS[tool_id]['name']}已损坏"
                self.tools[tool_id]["durability"] = ITEMS[tool_id]["durability"]
            return True, None
        return False, "没有该工具"

    def get_total_attack(self):
        attack = 5
        for weapon_id, weapon_data in self.tools.items():
            if ITEMS[weapon_id]["type"] == "weapon":
                attack += ITEMS[weapon_id].get("attack", 0) * weapon_data["quantity"]
        for comp in self.companions:
            attack += COMPANIONS[comp]["stats"].get("attack", 0)
        return attack

    def get_gather_bonus(self, resource_type):
        bonus = 1.0
        for tool_id, tool_data in self.tools.items():
            effect = ITEMS[tool_id].get("effect", {})
            if f"gather_{resource_type}" in effect:
                bonus += effect[f"gather_{resource_type}"] * tool_data["quantity"] * 0.1
        for comp in self.companions:
            bonus += COMPANIONS[comp]["stats"].get("gather_bonus", 0)
        return bonus

    def advance_turn(self, turns=1):
        messages = []
        for _ in range(turns):
            self.turn += 1
            self.hunger -= 2
            self.thirst -= 3
            
            if self.is_poisoned:
                self.health -= self.poison_damage
                self.poison_damage = max(0, self.poison_damage - 2)
                if self.poison_damage <= 0:
                    self.is_poisoned = False
                    messages.append("毒素已经消退。")
                else:
                    messages.append(f"中毒造成 {self.poison_damage} 点伤害！")
            
            if self.is_infected:
                self.health -= 3
                messages.append("伤口感染造成 3 点伤害！")
            
            if self.weather == "storm":
                self.hunger -= 2
                self.thirst -= 2
                self.health -= 2
            
            if self.weather == "heatwave":
                self.thirst -= 5
            
            if self.weather == "cold_snap":
                self.hunger -= 3
                if not self.camp["has_fire"] and self.current_location == "camp":
                    self.health -= 2
            
            if self.weather in ["rain", "storm"] and self.has_facility_flag("rain_collection"):
                water_collected = random.randint(1, 3)
                self.add_item("water", water_collected)
                messages.append(f"雨水收集器收集了 {water_collected} 单位净水！")
            
            self.hunger = max(0, self.hunger)
            self.thirst = max(0, self.thirst)
            self.health = max(0, min(self.max_health, self.health))
            
            if self.hunger <= 0:
                self.health -= 5
                messages.append("你非常饥饿，生命值下降！")
            if self.thirst <= 0:
                self.health -= 8
                messages.append("你非常口渴，生命值快速下降！")
            
            if self.turn > 4:
                self.turn = 1
                if self.time_of_day == "day":
                    self.time_of_day = "night"
                    night_result = self.night_phase()
                    messages.extend(night_result)
                else:
                    self.time_of_day = "day"
                    self.day += 1
                    if self.day >= 30:
                        self.victory = True
                        self.ending = "rescue"
                        self.game_over = True
                        messages.append("救援船只发现了你！你成功获救了！")
                    else:
                        messages.append(f"第 {self.day} 天开始了。")
                        weather_msg = self.roll_weather()
                        if weather_msg:
                            messages.append(weather_msg)
            
            death_check = self.check_death()
            if death_check:
                messages.append(death_check)
                break
        
        return "\n".join(messages) if messages else None

    def night_phase(self):
        messages = ["夜幕降临..."]
        config = DIFFICULTY_CONFIG[self.difficulty]
        self.clear_battle_log()
        
        if self.current_location != "camp":
            messages.append("你在野外过夜，非常危险！")
            self.health -= 10
            messages.append("野外的寒冷和危险造成 10 点伤害！")
            self.log_battle("夜幕降临...")
            self.log_battle("你在野外过夜，非常危险！")
            self.log_battle("野外的寒冷和危险造成 10 点伤害！")
            return messages
        
        torches = self.camp["torches"]
        torch_used = 0
        if torches > 0:
            self.camp["torches"] -= 1
            torch_used = 1
            messages.append(f"火把燃烧了一夜，还剩 {self.camp['torches']} 个。")
        
        # 计算防御和袭击概率 - 与 camp defend 保持一致
        facility_defense = self.get_facility_effect("defense")
        clue_defense_bonus = self.get_clue_effect("night_defense_bonus")
        camp_defense = int(facility_defense * (1 + clue_defense_bonus))
        defense_level = self.get_camp_upgrade_level("defense")
        
        attack_reduction = self.get_facility_effect("attack_reduction")
        torch_bonus = torches * 5
        
        # 计算武器和伙伴战斗力
        total_attack = 5
        weapons_used = []
        for weapon_id in ["spear", "bow", "iron_sword"]:
            if self.has_item(weapon_id):
                wep = ITEMS[weapon_id]
                total_attack += wep.get("attack", 0)
                weapons_used.append(wep["name"])
        
        companion_names = []
        for comp in self.companions:
            comp_data = COMPANIONS[comp]
            total_attack += comp_data["stats"].get("attack", 0)
            companion_names.append(comp_data["name"])
        
        # 记录战斗日志头部
        self.log_battle("=== 夜间战斗 ===")
        self.log_battle(f"第 {self.day} 天夜晚")
        self.log_battle(f"  武器: {', '.join(weapons_used) if weapons_used else '无'}")
        self.log_battle(f"  伙伴: {', '.join(companion_names) if companion_names else '无'}")
        self.log_battle(f"  营地: 防御等级{defense_level} (防御+{camp_defense}, 袭击概率-{int(attack_reduction*100)}%)")
        self.log_battle(f"  火把: {torches}个 (惊吓加成+{torch_bonus})")
        self.log_battle(f"  总战斗力: {total_attack} 攻击 / {camp_defense + torch_bonus} 防御")
        
        if torch_used > 0:
            self.log_battle("  消耗: 点燃1个火把")
        
        # 计算袭击概率
        base_attack_chance = config["night_attack_chance"]
        attack_chance = base_attack_chance
        
        torch_reduction = 0.0
        if torches > 0:
            torch_reduction = 0.3
            attack_chance *= (1 - torch_reduction)
        
        if defense_level > 0:
            attack_chance *= (1 - attack_reduction)
        
        self.log_battle("【战斗阶段】")
        self.log_battle(f"  基础袭击概率: {int(base_attack_chance * 100)}%")
        if torch_reduction > 0:
            self.log_battle(f"  火把降低: -{int(torch_reduction * 100)}%")
        if attack_reduction > 0:
            self.log_battle(f"  防御设施降低: -{int(attack_reduction * 100)}%")
        self.log_battle(f"  最终袭击概率: {int(attack_chance * 100)}%")
        
        old_health = self.health
        total_damage_taken = 0
        
        if random.random() < attack_chance:
            # 发生袭击 - 使用完整的减伤链计算
            beast_types = [
                ("狼群", 30, 15, 25),
                ("野猪", 25, 10, 20),
                ("巨蛇", 20, 15, 30),
                ("豹子", 35, 20, 35),
                ("熊", 50, 25, 40),
            ]
            beast_name, beast_hp, min_dmg, max_dmg = random.choice(beast_types)
            
            messages.append(f"⚠️  一群{beast_name}袭击了营地！")
            self.log_battle(f"  袭击: {beast_name}出现 (生命{beast_hp}, 攻击{min_dmg}-{max_dmg})")
            self.log_event(f"夜间袭击: {beast_name}出现")
            
            beast_current_hp = beast_hp
            round_num = 1
            
            while beast_current_hp > 0 and self.health > 0 and round_num <= 5:
                self.log_battle(f"--- 第{round_num}回合战斗 ---")
                
                # 玩家攻击
                player_damage = random.randint(max(1, total_attack - 5), total_attack + 5)
                beast_current_hp -= player_damage
                self.log_battle(f"  玩家攻击: 造成 {player_damage} 点伤害，野兽剩余{max(0, beast_current_hp)}生命")
                
                if beast_current_hp <= 0:
                    self.log_battle(f"  野兽被击败了！")
                    messages.append(f"你击退了{beast_name}！")
                    break
                
                # 野兽攻击 - 完整减伤链
                beast_damage_raw = random.randint(min_dmg, max_dmg)
                self.log_battle(f"  野兽攻击: 原始伤害 {beast_damage_raw}")
                
                camp_reduction = camp_defense / 100 if camp_defense > 0 else 0
                beast_after_camp = int(beast_damage_raw * (1 - camp_reduction))
                camp_reduced = beast_damage_raw - beast_after_camp
                self.log_battle(f"  营地减伤: -{camp_reduced} (防御{camp_defense}，减免{int(camp_reduction*100)}%)")
                
                torch_reduction_pct = torch_bonus / 100 if torch_bonus > 0 else 0
                beast_after_torch = int(beast_after_camp * (1 - torch_reduction_pct))
                torch_reduced = beast_after_camp - beast_after_torch
                self.log_battle(f"  火把减伤: -{torch_reduced} (惊吓{torch_bonus}，减免{int(torch_reduction_pct*100)}%)")
                
                # 伙伴减伤
                companion_reduced = 0
                for comp in self.companions:
                    comp_def = COMPANIONS[comp]["stats"].get("defense", 0)
                    if comp_def > 0:
                        comp_reduction = min(beast_after_torch, random.randint(1, comp_def))
                        companion_reduced += comp_reduction
                        beast_after_torch -= comp_reduction
                        self.log_battle(f"  伙伴{COMPANIONS[comp]['name']}抵挡: -{comp_reduction}")
                
                final_damage = max(0, beast_after_torch)
                self.health -= final_damage
                total_damage_taken += final_damage
                self.log_battle(f"  实际扣血: -{final_damage} (当前生命: {max(0, self.health)})")
                
                messages.append(f"第{round_num}回合: {beast_name}造成 {final_damage} 点伤害！")
                
                round_num += 1
            
            if self.health <= 0:
                self.death_cause = "killed_by_beast"
                messages.append(f"你被{beast_name}击败了...")
                self.log_event(f"战斗死亡: 被{beast_name}击败，受到{total_damage_taken}点伤害")
        else:
            # 平安无事
            messages.append("🌙 今夜平安无事，只有虫鸣声和海浪声...")
            self.log_battle("  结果: 今夜平安无事")
            
            # 夜间恢复
            night_heal = self.get_facility_effect("night_heal")
            for comp in self.companions:
                night_heal += int(COMPANIONS[comp]["stats"].get("heal_bonus", 0) * 5)
            
            shelter_level = self.get_camp_upgrade_level("shelter")
            fire_level = self.get_camp_upgrade_level("fire")
            
            old_hp = self.health
            self.health = min(self.max_health, self.health + night_heal)
            actual_heal = self.health - old_hp
            
            heal_details = []
            if shelter_level > 0:
                shelter_heal = CAMP_UPGRADES["shelter"]["levels"][shelter_level-1]["effects"].get("night_heal", 0)
                heal_details.append(f"营地+{shelter_heal}")
            if fire_level > 0:
                fire_heal = CAMP_UPGRADES["fire"]["levels"][fire_level-1]["effects"].get("night_heal", 0)
                heal_details.append(f"火源+{fire_heal}")
            
            messages.append(f"你在营地休息，恢复了 {actual_heal} 点生命值。")
            if heal_details:
                messages[-1] += f" ({', '.join(heal_details)})"
            
            self.log_battle(f"  夜间恢复: +{actual_heal} 生命")
            self.log_event(f"夜间平安，恢复{actual_heal}点生命")
        
        self.log_action(f"夜间防守: {'遭遇战斗' if old_health != self.health else '平安无事'}")
        
        return messages

    def roll_weather(self):
        self.weather = "clear"
        self.weather_forecast = None
        
        config = DIFFICULTY_CONFIG[self.difficulty]
        if random.random() < config["event_chance"] * 0.5:
            weather_events = ["rain", "rain", "storm", "heatwave", "cold_snap"]
            weather = random.choice(weather_events)
            self.weather_forecast = weather
            event_data = EVENTS[weather]
            return f"天气预报：{event_data['message']}"
        return None

    def check_death(self):
        if self.health <= 0:
            self.game_over = True
            if self.hunger <= 0:
                self.death_cause = "starve"
            elif self.thirst <= 0:
                self.death_cause = "dehydrate"
            elif self.is_poisoned:
                self.death_cause = "poisoned"
            elif self.is_infected:
                self.death_cause = "infection"
            else:
                self.death_cause = "killed_by_beast"
            self.ending = self.death_cause
            ending_data = ENDINGS[self.death_cause]
            self.calculate_score()
            return f"你死了！原因：{ending_data['name']}\n{ending_data['description']}"
        return None

    def discover_clue(self, clue_id):
        if clue_id in RUIN_CLUES and clue_id not in self.ruin_clues:
            self.ruin_clues[clue_id] = {"discovered": True, "day": self.day}
            self.ruin_exploration_progress = len(self.ruin_clues)
            return True
        return False
    
    def get_available_clues(self):
        available = []
        for clue_id, clue_data in RUIN_CLUES.items():
            if clue_id not in self.ruin_clues:
                requires = clue_data.get("requires", [])
                if all(req in self.ruin_clues for req in requires):
                    available.append(clue_id)
        return available
    
    def get_clue_effect(self, effect_name):
        value = 0
        for clue_id in self.ruin_clues:
            clue_data = RUIN_CLUES.get(clue_id, {})
            if effect_name in clue_data.get("effect", {}):
                value += clue_data["effect"][effect_name]
        return value
    
    def get_camp_upgrade_level(self, facility_id):
        level_key = f"{facility_id}_level"
        return self.camp.get(level_key, 0)
    
    def can_upgrade_facility(self, facility_id):
        if facility_id not in CAMP_UPGRADES:
            return False, "未知设施"
        
        facility = CAMP_UPGRADES[facility_id]
        current_level = self.get_camp_upgrade_level(facility_id)
        
        if current_level >= facility["max_level"]:
            return False, "已达最高等级"
        
        if "requires" in facility:
            required_facility = facility["requires"]
            if self.get_camp_upgrade_level(required_facility) < 1:
                return False, f"需要先建造{CAMP_UPGRADES[required_facility]['name']}"
        
        next_level = facility["levels"][current_level]
        for material, cost in next_level["cost"].items():
            if not self.has_item(material, cost):
                material_name = ITEMS.get(material, {}).get("name", material)
                return False, f"材料不足：{material_name} x{cost}"
        
        return True, next_level
    
    def upgrade_facility(self, facility_id):
        success, result = self.can_upgrade_facility(facility_id)
        if not success:
            return False, result
        
        next_level = result
        for material, cost in next_level["cost"].items():
            self.remove_item(material, cost)
        
        level_key = f"{facility_id}_level"
        self.camp[level_key] = next_level["level"]
        
        if facility_id == "shelter":
            self.camp["built"] = True
        elif facility_id == "fire":
            self.camp["has_fire"] = True
        elif facility_id == "water_filter":
            self.camp["has_water_filter"] = True
        elif facility_id == "storage":
            self.camp["has_storage"] = True
        elif facility_id == "defense":
            self.camp["defense_level"] = next_level["level"]
        
        return True, next_level
    
    def log_battle(self, message):
        self.battle_log.append(message)
    
    def clear_battle_log(self):
        self.battle_log = []
    
    def calculate_score(self):
        base_score = ENDINGS.get(self.ending, {}).get("score", 0)
        survival_bonus = self.day * 2
        companion_bonus = len(self.companions) * 10
        map_bonus = self.map_fragments * 5
        clue_bonus = sum(RUIN_CLUES.get(c, {}).get("score_bonus", 0) for c in self.ruin_clues)
        facility_bonus = sum(
            self.get_camp_upgrade_level(f) * 5 
            for f in ["shelter", "fire", "storage", "water_filter", "defense"]
        )
        difficulty_multiplier = {"easy": 0.8, "normal": 1.0, "hard": 1.5, "nightmare": 2.0}[self.difficulty]
        self.score = int((base_score + survival_bonus + companion_bonus + map_bonus + clue_bonus + facility_bonus) * difficulty_multiplier)

    def save_game(self, slot_name):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        
        save_data = {
            "player_name": self.player_name,
            "difficulty": self.difficulty,
            "health": self.health,
            "max_health": self.max_health,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "day": self.day,
            "turn": self.turn,
            "time_of_day": self.time_of_day,
            "current_location": self.current_location,
            "inventory": self.inventory,
            "tools": self.tools,
            "companions": self.companions,
            "camp": self.camp,
            "is_poisoned": self.is_poisoned,
            "poison_damage": self.poison_damage,
            "is_infected": self.is_infected,
            "map_fragments": self.map_fragments,
            "boat_parts": self.boat_parts,
            "score": self.score,
            "death_cause": self.death_cause,
            "game_over": self.game_over,
            "victory": self.victory,
            "ending": self.ending,
            "action_log": self.action_log,
            "event_log": self.event_log,
            "trader_available": self.trader_available,
            "weather": self.weather,
            "weather_forecast": self.weather_forecast,
            "ruin_clues": self.ruin_clues,
            "ruin_exploration_progress": self.ruin_exploration_progress,
            "battle_log": self.battle_log,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        filename = os.path.join(SAVE_DIR, f"{slot_name}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        return f"游戏已保存到存档：{slot_name}"

    def load_game(self, slot_name):
        filename = os.path.join(SAVE_DIR, f"{slot_name}.json")
        if not os.path.exists(filename):
            return None, f"存档 {slot_name} 不存在！"
        
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.player_name = data["player_name"]
        self.difficulty = data["difficulty"]
        self.health = data["health"]
        self.max_health = data["max_health"]
        self.hunger = data["hunger"]
        self.thirst = data["thirst"]
        self.day = data["day"]
        self.turn = data["turn"]
        self.time_of_day = data["time_of_day"]
        self.current_location = data["current_location"]
        self.inventory = data["inventory"]
        self.tools = data["tools"]
        self.companions = data["companions"]
        self.camp = data["camp"]
        self.is_poisoned = data["is_poisoned"]
        self.poison_damage = data["poison_damage"]
        self.is_infected = data["is_infected"]
        self.map_fragments = data["map_fragments"]
        self.boat_parts = data.get("boat_parts", 0)
        self.score = data["score"]
        self.death_cause = data["death_cause"]
        self.game_over = data["game_over"]
        self.victory = data["victory"]
        self.ending = data["ending"]
        self.action_log = data["action_log"]
        self.event_log = data["event_log"]
        self.trader_available = data.get("trader_available", False)
        self.weather = data.get("weather", "clear")
        self.weather_forecast = data.get("weather_forecast", None)
        self.ruin_clues = data.get("ruin_clues", {})
        self.ruin_exploration_progress = data.get("ruin_exploration_progress", 0)
        self.battle_log = data.get("battle_log", [])
        
        self._sync_map_fragments()
        self._migrate_old_camp_data()
        
        return True, f"已加载存档：{slot_name}（保存于 {data.get('saved_at', '未知时间')}）"

    @staticmethod
    def list_saves():
        if not os.path.exists(SAVE_DIR):
            return []
        saves = []
        for filename in os.listdir(SAVE_DIR):
            if filename.endswith(".json"):
                slot_name = filename[:-5]
                try:
                    with open(os.path.join(SAVE_DIR, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    saves.append({
                        "slot": slot_name,
                        "player": data.get("player_name", "未知"),
                        "day": data.get("day", 0),
                        "difficulty": data.get("difficulty", "normal"),
                        "saved_at": data.get("saved_at", "未知时间"),
                        "game_over": data.get("game_over", False),
                        "victory": data.get("victory", False),
                    })
                except:
                    saves.append({"slot": slot_name, "player": "损坏", "day": 0, "difficulty": "normal", "saved_at": "损坏", "game_over": True, "victory": False})
        return saves
