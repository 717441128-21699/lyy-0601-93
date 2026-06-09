"""游戏命令处理"""

import random
from game_state import GameState
from game_data import (
    DIFFICULTY_CONFIG, ITEMS, RECIPES, MAP_LOCATIONS,
    EVENTS, COMPANIONS, TRADER_ITEMS, ENDINGS, WATER_PURIFICATION
)

def parse_int_param(value, min_val=1, max_val=None, param_name="数量"):
    """解析整数参数，返回 (成功, 结果/错误信息)"""
    if value is None or value == "":
        return False, f"参数错误：{param_name}不能为空。"
    
    try:
        num = int(value)
    except (ValueError, TypeError):
        return False, f"参数错误：{param_name}必须是正整数，不能是'{value}'。"
    
    if num < min_val:
        return False, f"参数错误：{param_name}不能小于{min_val}。"
    
    if max_val is not None and num > max_val:
        return False, f"参数错误：{param_name}不能大于{max_val}。"
    
    return True, num

class CommandHandler:
    def __init__(self, game_state):
        self.game = game_state

    def handle(self, command, args):
        handlers = {
            "start": self.cmd_start,
            "map": self.cmd_map,
            "bag": self.cmd_bag,
            "craft": self.cmd_craft,
            "camp": self.cmd_camp,
            "event": self.cmd_event,
            "save": self.cmd_save,
            "help": self.cmd_help,
            "status": self.cmd_status,
            "use": self.cmd_use,
            "rest": self.cmd_rest,
        }
        
        if command in handlers:
            return handlers[command](args)
        return f"未知命令：{command}。输入 help 查看帮助。"

    def cmd_help(self, args):
        help_text = """
荒岛求生 - 命令帮助

start - 开始游戏
  start new <名字> [难度] - 新建游戏 (难度: easy/normal/hard/nightmare)
  start list - 列出难度说明

map - 地图操作
  map show - 查看地图
  map go <地点> - 前往地点
  map gather [数量] - 在当前地点采集资源
  map explore - 探索当前地点（遗迹等）

bag - 背包操作
  bag show - 查看背包
  bag use <物品> [数量] - 使用物品

craft - 制作系统
  craft list - 查看可制作配方
  craft make <物品> [数量] - 制作物品

camp - 营地操作
  camp show - 查看营地状态
  camp build <设施> - 建造设施 (shelter/fire/water_filter/storage/defense)
  camp cook <原料> - 烹饪食物
  camp purify - 净化饮水
  camp heal - 治疗伤口
  camp defend - 加强夜间防守

event - 事件系统
  event trigger - 触发随机事件
  event recruit <伙伴> - 招募伙伴
  event list_companions - 查看可招募伙伴
  event trade buy <物品> [数量] - 从商人购买
  event trade sell <物品> [数量] - 卖给商人
  event weather - 查看天气预报

save - 存档系统
  save save <存档名> - 保存游戏
  save load <存档名> - 加载游戏
  save list - 列出存档
  save replay - 死亡回放
  save score - 查看结局评分

其他命令：
  status - 查看当前状态
  rest [回合数] - 休息跳过回合
  help - 显示帮助
  exit - 退出游戏
"""
        return help_text

    def cmd_start(self, args):
        if not args:
            return "用法：start new <名字> [难度] 或 start list"
        
        subcmd = args[0]
        if subcmd == "list":
            text = "可用难度：\n"
            for key, config in DIFFICULTY_CONFIG.items():
                text += f"  {key:10} - {config['name']}: {config['description']}\n"
            return text
        elif subcmd == "new":
            if len(args) < 2:
                return "用法：start new <名字> [难度]"
            name = args[1]
            difficulty = args[2] if len(args) > 2 else "normal"
            if difficulty not in DIFFICULTY_CONFIG:
                return f"未知难度：{difficulty}。可用难度：{', '.join(DIFFICULTY_CONFIG.keys())}"
            return self.game.new_game(name, difficulty)
        return "未知子命令。用法：start new 或 start list"

    def cmd_map(self, args):
        if self.game.game_over:
            return "游戏已结束，请开始新游戏。"
        if not self.game.player_name:
            return "请先开始新游戏：start new <名字>"
        
        if not args:
            return "用法：map show | go <地点> | gather [数量] | explore"
        
        subcmd = args[0]
        
        if subcmd == "show":
            text = "=== 荒岛地图 ===\n"
            for loc_id, loc_data in MAP_LOCATIONS.items():
                current = " [当前]" if loc_id == self.game.current_location else ""
                danger = "⚠️" * int(loc_data["danger"] * 5) if loc_data["danger"] > 0 else "安全"
                text += f"  {loc_id:10} - {loc_data['name']}{current}\n"
                text += f"      {loc_data['description']}\n"
                text += f"      危险等级: {danger}\n"
                if loc_data["resources"]:
                    resources = ", ".join([ITEMS[r]["name"] for r in loc_data["resources"].keys()])
                    text += f"      可采集: {resources}\n"
            return text
        
        elif subcmd == "go":
            if len(args) < 2:
                return "用法：map go <地点>"
            location = args[1]
            if location not in MAP_LOCATIONS:
                return f"未知地点：{location}"
            if location == self.game.current_location:
                return f"你已经在{MAP_LOCATIONS[location]['name']}了。"
            
            self.game.current_location = location
            self.game.log_action(f"前往{MAP_LOCATIONS[location]['name']}")
            advance_msg = self.game.advance_turn(1)
            
            msg = f"你来到了{MAP_LOCATIONS[location]['name']}。\n{MAP_LOCATIONS[location]['description']}"
            if advance_msg:
                msg += f"\n{advance_msg}"
            
            if random.random() < MAP_LOCATIONS[location]["danger"] * 0.5:
                event_msg = self._trigger_random_event()
                if event_msg:
                    msg += f"\n{event_msg}"
            
            return msg
        
        elif subcmd == "gather":
            location = MAP_LOCATIONS[self.game.current_location]
            if not location["resources"]:
                return "这里没有可采集的资源。"
            
            if self.game.time_of_day == "night":
                return "夜间太危险，无法采集资源。"
            
            success, result = parse_int_param(
                args[1] if len(args) > 1 else "1",
                min_val=1, max_val=3, param_name="采集数量"
            )
            if not success:
                return result + "\n用法：map gather [数量]，数量范围1-3"
            quantity = result
            
            summary = {
                "gathered": {},
                "tools_used": [],
                "weather_effects": [],
                "events": [],
                "turn_summary": []
            }
            
            for turn in range(1, quantity + 1):
                turn_gathered = {}
                turn_log = [f"--- 第{turn}次采集 ---"]
                
                old_hunger = self.game.hunger
                old_thirst = self.game.thirst
                old_health = self.game.health
                
                for resource, chance in location["resources"].items():
                    resource_type = resource.replace("_", "")
                    bonus = self.game.get_gather_bonus(resource_type)
                    if random.random() < chance * bonus:
                        amount = random.randint(1, 2)
                        turn_gathered[resource] = amount
                        
                        if resource == "wood" and self.game.has_item("axe"):
                            ok, msg = self.game.use_tool("axe")
                            if msg:
                                summary["tools_used"].append(msg)
                        elif resource == "stone" and self.game.has_item("pickaxe"):
                            ok, msg = self.game.use_tool("pickaxe")
                            if msg:
                                summary["tools_used"].append(msg)
                        elif resource == "raw_fish" and self.game.has_item("fishing_rod"):
                            ok, msg = self.game.use_tool("fishing_rod")
                            if msg:
                                summary["tools_used"].append(msg)
                        elif resource in ["fiber", "vine"] and self.game.has_item("knife"):
                            ok, msg = self.game.use_tool("knife")
                            if msg:
                                summary["tools_used"].append(msg)
                
                for item, amount in turn_gathered.items():
                    self.game.add_item(item, amount)
                    if item in summary["gathered"]:
                        summary["gathered"][item] += amount
                    else:
                        summary["gathered"][item] = amount
                    turn_log.append(f"  获得 {ITEMS[item]['name']} x{amount}")
                
                if not turn_gathered:
                    turn_log.append("  什么都没找到...")
                
                advance_msg = self.game.advance_turn(1)
                
                hunger_change = self.game.hunger - old_hunger
                thirst_change = self.game.thirst - old_thirst
                health_change = self.game.health - old_health
                
                if hunger_change != 0 or thirst_change != 0 or health_change != 0:
                    changes = []
                    if hunger_change != 0:
                        changes.append(f"饱食{hunger_change:+d}")
                    if thirst_change != 0:
                        changes.append(f"口渴{thirst_change:+d}")
                    if health_change != 0:
                        changes.append(f"生命{health_change:+d}")
                    turn_log.append(f"  状态变化: {', '.join(changes)}")
                
                if self.game.weather != "clear":
                    weather_names = {"storm": "暴风雨", "heatwave": "热浪", "cold_snap": "寒流"}
                    summary["weather_effects"].append(f"第{turn}次: {weather_names.get(self.game.weather, '恶劣天气')}影响")
                
                if advance_msg:
                    turn_log.append(f"  {advance_msg}")
                
                if random.random() < location["danger"] * 0.3:
                    event_msg = self._trigger_random_event()
                    if event_msg:
                        summary["events"].append(f"第{turn}次: {event_msg.split(chr(10))[0]}")
                        turn_log.append(f"  ⚠️ 发生事件")
                
                summary["turn_summary"].append("\n".join(turn_log))
                
                if self.game.game_over:
                    break
            
            text = f"=== 在{location['name']}采集 {quantity} 次 ===\n"
            
            if quantity > 1:
                text += "\n".join(summary["turn_summary"]) + "\n"
            
            text += "\n=== 采集汇总 ===\n"
            if summary["gathered"]:
                text += "收获物品：\n"
                for item, amount in sorted(summary["gathered"].items()):
                    text += f"  {ITEMS[item]['name']} x{amount}\n"
                    if item == "map_fragment":
                        text += f"    🗺️  地图碎片进度: {self.game.map_fragments}/{self.game.total_map_fragments}\n"
            else:
                text += "收获物品：无\n"
            
            if summary["tools_used"]:
                text += "\n工具损耗：\n"
                for msg in summary["tools_used"]:
                    text += f"  {msg}\n"
            
            if summary["weather_effects"]:
                text += "\n天气影响：\n"
                for msg in summary["weather_effects"]:
                    text += f"  {msg}\n"
            
            if summary["events"]:
                text += "\n遭遇事件：\n"
                for msg in summary["events"]:
                    text += f"  {msg}\n"
            
            text += f"\n最终状态: 生命{self.game.health}/{self.game.max_health} 饱食{self.game.hunger} 口渴{self.game.thirst}\n"
            
            self.game.log_action(f"在{location['name']}采集{quantity}次，收获: {summary['gathered']}")
            
            if self.game.game_over:
                text += f"\n{self.game.check_death()}"
                if self.game.game_over:
                    text += f"\n最终得分：{self.game.score}"
            
            return text
        
        elif subcmd == "explore":
            location = MAP_LOCATIONS[self.game.current_location]
            if not location.get("explorable", False):
                return "这里没有什么可探索的。"
            
            if self.game.time_of_day == "night":
                return "夜间太危险，无法探索。"
            
            text = f"你开始探索{location['name']}...\n"
            self.game.log_action(f"探索{location['name']}")
            
            if location.get("is_ruin", False):
                if random.random() < 0.4:
                    self.game.add_item("map_fragment", 1)
                    text += f"🎉 你发现了一块地图碎片！({self.game.map_fragments}/{self.game.total_map_fragments})\n"
                    if self.game.game_over and self.game.victory:
                        ending = ENDINGS["treasure"]
                        text += "\n🏆 你收集齐了所有地图碎片！你找到了传说中的宝藏！\n"
                        text += f"{ending['description']}\n"
                        text += f"\n最终得分：{self.game.score}"
                        return text
                
                if random.random() < 0.3:
                    coin = random.randint(1, 3)
                    self.game.add_item("ancient_coin", coin)
                    text += f"💰 你发现了 {coin} 枚古代钱币！\n"
            else:
                if random.random() < 0.2:
                    self.game.add_item("map_fragment", 1)
                    text += f"🎉 你发现了一块地图碎片！({self.game.map_fragments}/{self.game.total_map_fragments})\n"
                    if self.game.game_over and self.game.victory:
                        ending = ENDINGS["treasure"]
                        text += "\n🏆 你收集齐了所有地图碎片！你找到了传说中的宝藏！\n"
                        text += f"{ending['description']}\n"
                        text += f"\n最终得分：{self.game.score}"
                        return text
            
            if random.random() < location["danger"] * 0.6:
                damage = random.randint(10, 25)
                self.game.health -= damage
                text += f"⚠️ 探索中遇到危险，受到 {damage} 点伤害！\n"
                if self.game.health <= 0:
                    self.game.check_death()
                    text += f"\n{self.game.check_death()}"
                    if self.game.game_over:
                        text += f"\n最终得分：{self.game.score}"
                        return text
            
            advance_msg = self.game.advance_turn(2)
            if advance_msg:
                text += f"\n{advance_msg}"
            
            return text
        
        return "未知子命令。用法：map show | go <地点> | gather [数量] | explore"

    def cmd_bag(self, args):
        if not self.game.player_name:
            return "请先开始新游戏。"
        
        if not args:
            return self._show_inventory()
        
        subcmd = args[0]
        if subcmd == "show":
            return self._show_inventory()
        elif subcmd == "use":
            if len(args) < 2:
                return "用法：bag use <物品> [数量]\n示例：bag use water 2"
            item_name = args[1]
            
            if len(args) > 2:
                success, result = parse_int_param(
                    args[2], min_val=1, max_val=99, param_name="使用数量"
                )
                if not success:
                    return result + "\n用法：bag use <物品> [数量]"
                quantity = result
            else:
                quantity = 1
            
            item_id = self._find_item_id(item_name)
            if not item_id:
                return f"找不到物品：{item_name}\n用法：bag use <物品> [数量]"
            
            return self._use_item(item_id, quantity)
        
        return "未知子命令。用法：bag show | use <物品>"

    def _show_inventory(self):
        text = "=== 背包 ===\n"
        
        if self.game.inventory:
            text += "\n物品：\n"
            for item_id, count in sorted(self.game.inventory.items()):
                item = ITEMS[item_id]
                text += f"  {item_id:15} - {item['name']:8} x{count}\n"
                text += f"      {item['description']}\n"
        else:
            text += "\n物品：空\n"
        
        if self.game.tools:
            text += "\n工具/武器：\n"
            for tool_id, tool_data in sorted(self.game.tools.items()):
                tool = ITEMS[tool_id]
                dura = tool_data["durability"]
                max_dura = tool["durability"]
                text += f"  {tool_id:15} - {tool['name']:8} x{tool_data['quantity']} 耐久:{dura}/{max_dura}\n"
                text += f"      {tool['description']}\n"
        
        if self.game.companions:
            text += "\n伙伴：\n"
            for comp_id in self.game.companions:
                comp = COMPANIONS[comp_id]
                text += f"  {comp_id:10} - {comp['name']}\n"
                text += f"      {comp['description']}\n"
                stats = []
                for k, v in comp["stats"].items():
                    if v:
                        stats.append(f"{k}: {v}")
                text += f"      属性: {', '.join(stats)}\n"
        
        return text

    def _find_item_id(self, name):
        name = name.lower()
        for item_id, item_data in ITEMS.items():
            if item_id == name or item_data["name"] == name:
                return item_id
        return None

    def _use_item(self, item_id, quantity=1):
        if not self.game.has_item(item_id, quantity):
            return f"没有足够的{ITEMS[item_id]['name']}"
        
        item = ITEMS[item_id]
        if item["type"] not in ["consumable", "medical"]:
            return f"{item['name']}不能直接使用"
        
        messages = []
        for _ in range(quantity):
            effect = item["effect"]
            if "health" in effect:
                self.game.health = min(self.game.max_health, self.game.health + effect["health"])
                messages.append(f"生命值 {'+' if effect['health'] > 0 else ''}{effect['health']}")
            if "hunger" in effect:
                self.game.hunger = min(100, self.game.hunger + effect["hunger"])
                messages.append(f"饱食度 {'+' if effect['hunger'] > 0 else ''}{effect['hunger']}")
            if "thirst" in effect:
                self.game.thirst = min(100, self.game.thirst + effect["thirst"])
                messages.append(f"口渴度 {'+' if effect['thirst'] > 0 else ''}{effect['thirst']}")
            if effect.get("cure_poison"):
                self.game.is_poisoned = False
                self.game.poison_damage = 0
                messages.append("已解毒")
            
            self.game.remove_item(item_id, 1)
        
        self.game.log_action(f"使用 {item['name']} x{quantity}")
        advance_msg = self.game.advance_turn(1)
        
        result = f"使用了 {item['name']} x{quantity}\n" + "\n".join(messages)
        if advance_msg:
            result += f"\n{advance_msg}"
        return result

    def _night_defense_combat(self):
        """夜间防守战斗系统"""
        config = DIFFICULTY_CONFIG[self.game.difficulty]
        
        text = "=== 夜间防守战斗 ===\n\n"
        
        # 战斗准备阶段
        text += "【战斗准备】\n"
        
        # 计算玩家攻击力
        player_attack = 5
        weapons_used = []
        for weapon_id, weapon_data in self.game.tools.items():
            if ITEMS[weapon_id]["type"] == "weapon":
                atk = ITEMS[weapon_id].get("attack", 0)
                qty = weapon_data["quantity"]
                player_attack += atk * qty
                weapons_used.append(f"{ITEMS[weapon_id]['name']}(攻击+{atk})x{qty}")
        
        # 伙伴加成
        companion_attack = 0
        companion_defense = 0
        companion_names = []
        for comp_id in self.game.companions:
            comp = COMPANIONS[comp_id]
            companion_attack += comp["stats"].get("attack", 0)
            companion_defense += comp["stats"].get("danger_reduction", 0)
            companion_names.append(comp["name"])
        
        total_attack = player_attack + companion_attack
        
        # 营地防御
        camp_defense = self.game.camp["defense_level"] * 10
        torches = self.game.camp["torches"]
        torch_bonus = torches * 5
        
        text += f"  武器: {', '.join(weapons_used) if weapons_used else '无'}\n"
        text += f"  伙伴: {', '.join(companion_names) if companion_names else '无'} (攻击+{companion_attack}, 减伤{int(companion_defense*100)}%)\n"
        text += f"  营地: 防御等级{self.game.camp['defense_level']} (防御+{camp_defense})\n"
        text += f"  火把: {torches}个 (惊吓加成+{torch_bonus})\n"
        text += f"  总战斗力: {total_attack} 攻击 / {camp_defense + torch_bonus} 防御\n\n"
        
        # 消耗火把
        if torches > 0:
            self.game.camp["torches"] -= 1
            text += "🔥 点燃了1个火把，照亮了营地周围...\n\n"
        
        # 判断是否有袭击
        attack_chance = config["night_attack_chance"]
        if torches > 0:
            attack_chance *= 0.7
        if camp_defense > 0:
            attack_chance *= 0.8
        
        text += "【战斗阶段】\n"
        
        old_health = self.game.health
        
        if random.random() < attack_chance:
            # 有袭击
            beast_types = [
                ("狼群", 30, 15, 25),
                ("野猪", 25, 10, 20),
                ("巨蛇", 20, 15, 30),
                ("豹子", 35, 20, 35),
                ("熊", 50, 25, 40),
            ]
            beast_name, beast_hp, min_dmg, max_dmg = random.choice(beast_types)
            
            text += f"⚠️  一群{beast_name}袭击了营地！\n\n"
            self.game.log_event(f"夜间袭击: {beast_name}出现")
            
            # 多回合战斗
            round_num = 1
            beast_current_hp = beast_hp
            total_damage_taken = 0
            total_damage_dealt = 0
            
            while beast_current_hp > 0 and self.game.health > 0:
                text += f"--- 第{round_num}回合战斗 ---\n"
                
                # 玩家攻击
                player_damage = random.randint(total_attack - 5, total_attack + 5)
                player_damage = max(1, player_damage)
                beast_current_hp -= player_damage
                total_damage_dealt += player_damage
                text += f"  你和伙伴们发起攻击，造成 {player_damage} 点伤害！\n"
                
                # 武器耐久消耗
                for weapon_id in list(self.game.tools.keys()):
                    if ITEMS[weapon_id]["type"] == "weapon":
                        ok, msg = self.game.use_tool(weapon_id)
                        if msg:
                            text += f"  {msg}\n"
                
                if beast_current_hp <= 0:
                    text += f"  {beast_name}被击退了！\n\n"
                    self.game.log_event(f"击退{beast_name}，造成{total_damage_dealt}点伤害")
                    break
                
                # 野兽攻击
                beast_damage = random.randint(min_dmg, max_dmg)
                
                # 防御减伤
                defense_reduction = (camp_defense + torch_bonus) / 100
                beast_damage = int(beast_damage * (1 - defense_reduction))
                
                # 伙伴减伤
                beast_damage = int(beast_damage * (1 - companion_defense))
                
                beast_damage = max(1, beast_damage)
                self.game.health -= beast_damage
                total_damage_taken += beast_damage
                
                text += f"  {beast_name}反击，造成 {beast_damage} 点伤害！\n"
                
                # 有防御设施的情况
                if camp_defense > 0 and random.random() < 0.3:
                    blocked = random.randint(5, 15)
                    self.game.health = min(self.game.max_health, self.game.health + blocked)
                    text += f"  营地防御设施抵挡了 {blocked} 点伤害！\n"
                
                if torches > 0 and random.random() < 0.2:
                    beast_damage = int(beast_damage * 0.5)
                    text += f"  火把的光芒吓退了{beast_name}，伤害减半！\n"
                
                text += f"  {beast_name}剩余生命: {max(0, beast_current_hp)}/{beast_hp}\n"
                text += f"  你的生命值: {self.game.health}/{self.game.max_health}\n\n"
                
                round_num += 1
                if round_num > 5:
                    text += f"  经过{round_num-1}回合激战，{beast_name}终于撤退了！\n\n"
                    break
            
            actual_damage = old_health - self.game.health
            text += f"=== 战斗结算 ===\n"
            text += f"  战斗回合: {min(round_num, 5)}回合\n"
            text += f"  造成伤害: {total_damage_dealt}\n"
            text += f"  受到伤害: {actual_damage}\n"
            text += f"  最终生命: {self.game.health}/{self.game.max_health}\n"
            
            if self.game.health <= 0:
                self.game.death_cause = "killed_by_beast"
                self.game.ending = "killed_by_beast"
                self.game.game_over = True
                self.game.calculate_score()
                text += f"\n💀 你在与{beast_name}的战斗中倒下了...\n"
                ending = ENDINGS["killed_by_beast"]
                text += f"{ending['name']}: {ending['description']}\n"
                text += f"最终得分: {self.game.score}"
                
                self.game.log_event(f"战斗死亡: 被{beast_name}击败，受到{actual_damage}点伤害")
        else:
            # 没有袭击
            text += "🌙 今夜平安无事，只有虫鸣声和海浪声...\n"
            
            # 夜间恢复
            heal_amount = 5
            if self.game.camp["has_fire"]:
                heal_amount += 3
            for comp in self.game.companions:
                heal_amount += int(COMPANIONS[comp]["stats"].get("heal_bonus", 0) * 5)
            
            old_hp = self.game.health
            self.game.health = min(self.game.max_health, self.game.health + heal_amount)
            actual_heal = self.game.health - old_hp
            text += f"💤 你在营地安心休息，恢复了 {actual_heal} 点生命值。\n"
            
            self.game.log_event(f"夜间平安，恢复{actual_heal}点生命")
        
        self.game.log_action(f"夜间防守: {'遭遇战斗' if old_health != self.game.health else '平安无事'}")
        
        advance_msg = self.game.advance_turn(1)
        if advance_msg:
            text += f"\n{advance_msg}"
        
        return text

    def cmd_craft(self, args):
        if self.game.game_over:
            return "游戏已结束。"
        if not self.game.player_name:
            return "请先开始新游戏。"
        
        if not args:
            return "用法：craft list | make <物品> [数量]\n示例：craft make rope 3"
        
        subcmd = args[0]
        make_quantity = 1
        
        if subcmd == "make":
            # 先验证参数
            if len(args) < 2:
                return "用法：craft make <物品> [数量]\n示例：craft make rope 3"
            
            if len(args) > 2:
                success, result = parse_int_param(
                    args[2], min_val=1, max_val=10, param_name="制作数量"
                )
                if not success:
                    return result + "\n用法：craft make <物品> [数量]，数量范围1-10"
                make_quantity = result
        
        # 再检查是否在营地
        if self.game.current_location != "camp":
            return "必须在营地才能制作物品。"
        
        if subcmd == "list":
            text = "=== 可制作配方 ===\n"
            for item_id, recipe in sorted(RECIPES.items()):
                item = ITEMS[item_id]
                materials = ", ".join([f"{ITEMS[m]['name']} x{n}" for m, n in recipe["materials"].items()])
                can_make = all(self.game.has_item(m, n) for m, n in recipe["materials"].items())
                if recipe.get("require_fire") and not self.game.camp["has_fire"]:
                    can_make = False
                status = "✓" if can_make else "✗"
                qty = f" (产出x{recipe['quantity']})" if recipe.get("quantity", 1) > 1 else ""
                fire_req = " [需要火]" if recipe.get("require_fire") else ""
                text += f"  {status} {item_id:15} - {item['name']}{qty}{fire_req}\n"
                text += f"      材料: {materials}\n"
                text += f"      {item['description']}\n"
            return text
        
        elif subcmd == "make":
            item_name = args[1]
            quantity = make_quantity
            
            item_id = self._find_item_id(item_name)
            if not item_id or item_id not in RECIPES:
                return f"无法制作：{item_name}\n用法：craft make <物品> [数量]\n输入 craft list 查看可制作物品"
            
            recipe = RECIPES[item_id]
            
            if recipe.get("require_fire") and not self.game.camp["has_fire"]:
                return "需要先生火才能制作这个物品。"
            
            for mat_id, mat_qty in recipe["materials"].items():
                needed = mat_qty * quantity
                if not self.game.has_item(mat_id, needed):
                    return f"材料不足：需要 {ITEMS[mat_id]['name']} x{needed}，只有 {self.game.get_item_count(mat_id)}"
            
            craft_bonus = 1.0
            for comp in self.game.companions:
                craft_bonus += COMPANIONS[comp]["stats"].get("craft_bonus", 0)
            
            summary = {
                "materials_used": {},
                "produced": 0,
                "bonus": False,
                "turn_summary": []
            }
            
            for turn in range(1, quantity + 1):
                turn_log = [f"--- 第{turn}次制作 ---"]
                old_hunger = self.game.hunger
                old_thirst = self.game.thirst
                
                for mat_id, mat_qty in recipe["materials"].items():
                    self.game.remove_item(mat_id, mat_qty)
                    if mat_id in summary["materials_used"]:
                        summary["materials_used"][mat_id] += mat_qty
                    else:
                        summary["materials_used"][mat_id] = mat_qty
                
                output_qty = recipe.get("quantity", 1)
                got_bonus = False
                if random.random() < (craft_bonus - 1) * 0.5:
                    output_qty = int(output_qty * 1.5)
                    got_bonus = True
                    summary["bonus"] = True
                
                self.game.add_item(item_id, output_qty)
                summary["produced"] += output_qty
                
                materials_str = ", ".join([f"{ITEMS[m]['name']}x{n}" for m, n in recipe['materials'].items()])
                turn_log.append(f"  消耗: {materials_str}")
                turn_log.append(f"  产出: {ITEMS[item_id]['name']} x{output_qty}{' (工匠加成!)' if got_bonus else ''}")
                
                advance_msg = self.game.advance_turn(1)
                
                hunger_change = self.game.hunger - old_hunger
                thirst_change = self.game.thirst - old_thirst
                if hunger_change != 0 or thirst_change != 0:
                    changes = []
                    if hunger_change != 0:
                        changes.append(f"饱食{hunger_change:+d}")
                    if thirst_change != 0:
                        changes.append(f"口渴{thirst_change:+d}")
                    turn_log.append(f"  状态: {', '.join(changes)}")
                
                if advance_msg:
                    turn_log.append(f"  {advance_msg}")
                
                summary["turn_summary"].append("\n".join(turn_log))
                
                if self.game.game_over:
                    break
            
            text = f"=== 制作 {ITEMS[item_id]['name']} x{quantity} ===\n"
            
            if quantity > 1:
                text += "\n".join(summary["turn_summary"]) + "\n"
            
            text += "\n=== 制作汇总 ===\n"
            text += "消耗材料：\n"
            for mat_id, amount in sorted(summary["materials_used"].items()):
                text += f"  {ITEMS[mat_id]['name']} x{amount}\n"
            text += f"\n产出物品：\n"
            text += f"  {ITEMS[item_id]['name']} x{summary['produced']}"
            if summary["bonus"]:
                text += " (含工匠加成)"
            text += "\n"
            
            text += f"\n最终状态: 生命{self.game.health}/{self.game.max_health} 饱食{self.game.hunger} 口渴{self.game.thirst}\n"
            
            self.game.log_action(f"制作{ITEMS[item_id]['name']}x{quantity}，产出x{summary['produced']}")
            
            if self.game.game_over:
                text += f"\n{self.game.check_death()}"
                if self.game.game_over:
                    text += f"\n最终得分：{self.game.score}"
            
            return text
        
        return "未知子命令。用法：craft list | make <物品>"

    def cmd_camp(self, args):
        if self.game.game_over:
            return "游戏已结束。"
        if not self.game.player_name:
            return "请先开始新游戏。"
        if self.game.current_location != "camp":
            return "必须在营地才能进行营地操作。"
        
        if not args:
            return "用法：camp show | build <设施> | cook | purify | heal | defend"
        
        subcmd = args[0]
        
        if subcmd == "show":
            camp = self.game.camp
            text = "=== 营地状态 ===\n"
            text += f"  营地: {'已建造' if camp['built'] else '未建造'}\n"
            text += f"  火源: {'✓' if camp['has_fire'] else '✗'}\n"
            text += f"  净水器: {'✓' if camp['has_water_filter'] else '✗'}\n"
            text += f"  仓库: {'✓' if camp['has_storage'] else '✗'}\n"
            text += f"  防御等级: {camp['defense_level']}/5\n"
            text += f"  火把: {camp['torches']} 个\n"
            text += f"\n  地图碎片: {self.game.map_fragments}/{self.game.total_map_fragments}\n"
            text += f"  船只零件: {self.game.boat_parts}/{self.game.total_boat_parts}\n"
            return text
        
        elif subcmd == "build":
            if len(args) < 2:
                return "用法：camp build <设施>\n设施：shelter, fire, water_filter, storage, defense, torch, boat_part"
            
            facility = args[1]
            return self._build_facility(facility)
        
        elif subcmd == "cook":
            if not self.game.camp["has_fire"]:
                return "需要先生火才能烹饪。"
            
            raw_items = [("raw_meat", "生肉"), ("raw_fish", "生鱼")]
            cooked = False
            text = ""
            
            for raw_id, raw_name in raw_items:
                while self.game.has_item(raw_id):
                    self.game.remove_item(raw_id, 1)
                    self.game.add_item("food", 1)
                    text += f"烹饪 {raw_name} -> 食物\n"
                    cooked = True
            
            if not cooked:
                return "没有可烹饪的生肉或生鱼。"
            
            self.game.log_action("烹饪食物")
            advance_msg = self.game.advance_turn(1)
            if advance_msg:
                text += f"\n{advance_msg}"
            return text
        
        elif subcmd == "purify":
            if not self.game.camp["has_fire"]:
                return "需要先生火才能净化水。"
            if not self.game.has_item("dirty_water"):
                return "没有脏水可以净化。"
            
            count = 0
            while self.game.has_item("dirty_water"):
                self.game.remove_item("dirty_water", 1)
                if self.game.camp["has_water_filter"]:
                    self.game.add_item("water", 2)
                else:
                    self.game.add_item("water", 1)
                count += 1
            
            self.game.log_action(f"净化 {count} 单位脏水")
            advance_msg = self.game.advance_turn(1)
            output = count * 2 if self.game.camp["has_water_filter"] else count
            text = f"净化了 {count} 单位脏水，得到 {output} 单位净水。"
            if advance_msg:
                text += f"\n{advance_msg}"
            return text
        
        elif subcmd == "heal":
            heal_items = [
                ("bandage", "绷带", 30),
                ("herb", "草药", 20),
                ("antidote", "解毒剂", 15),
            ]
            
            healed = False
            text = ""
            
            if self.game.is_infected and self.game.has_item("bandage", 2):
                self.game.remove_item("bandage", 2)
                self.game.is_infected = False
                text += "处理伤口感染...\n"
                healed = True
            
            if self.game.is_poisoned and self.game.has_item("antidote"):
                self.game.remove_item("antidote", 1)
                self.game.is_poisoned = False
                self.game.poison_damage = 0
                text += "使用解毒剂解毒...\n"
                healed = True
            
            heal_bonus = 1.0
            for comp in self.game.companions:
                heal_bonus += COMPANIONS[comp]["stats"].get("heal_bonus", 0)
            
            for item_id, name, base_heal in heal_items:
                if self.game.health < self.game.max_health and self.game.has_item(item_id):
                    heal_amount = int(base_heal * heal_bonus)
                    old_health = self.game.health
                    self.game.health = min(self.game.max_health, self.game.health + heal_amount)
                    actual_heal = self.game.health - old_health
                    self.game.remove_item(item_id, 1)
                    text += f"使用 {name}，恢复 {actual_heal} 点生命值\n"
                    healed = True
            
            if not healed:
                if self.game.health >= self.game.max_health:
                    return "你的生命值已满，不需要治疗。"
                return "没有足够的医疗用品。"
            
            self.game.log_action("治疗伤口")
            advance_msg = self.game.advance_turn(1)
            if advance_msg:
                text += f"\n{advance_msg}"
            return text
        
        elif subcmd == "defend":
            if not self.game.camp["built"]:
                return "需要先建造营地。"
            
            if self.game.time_of_day != "night":
                return "只有夜间才能进行防守。"
            
            return self._night_defense_combat()
        
        return "未知子命令。用法：camp show | build | cook | purify | heal | defend"

    def _build_facility(self, facility):
        building_costs = {
            "shelter": {"wood": 10, "stone": 5, "rope": 2},
            "fire": {"wood": 5, "flint": 2},
            "water_filter": {"wood": 5, "stone": 10, "fiber": 10},
            "storage": {"wood": 15, "rope": 3},
            "defense": {"wood": 10, "stone": 15, "rope": 2},
            "torch": {"wood": 1, "fiber": 2},
            "boat_part": {"wood": 20, "rope": 5, "iron_ingot": 3},
        }
        
        facility_names = {
            "shelter": "营地",
            "fire": "火源",
            "water_filter": "净水器",
            "storage": "仓库",
            "defense": "防御设施",
            "torch": "火把",
            "boat_part": "船只零件",
        }
        
        if facility not in building_costs:
            return f"未知设施：{facility}"
        
        if facility == "shelter" and self.game.camp["built"]:
            return "营地已经建造了。"
        if facility == "fire" and self.game.camp["has_fire"]:
            return "火已经生好了。"
        if facility == "water_filter" and self.game.camp["has_water_filter"]:
            return "净水器已经建造了。"
        if facility == "storage" and self.game.camp["has_storage"]:
            return "仓库已经建造了。"
        if facility == "defense" and self.game.camp["defense_level"] >= 5:
            return "防御等级已达最高。"
        
        cost = building_costs[facility]
        for mat_id, mat_qty in cost.items():
            if not self.game.has_item(mat_id, mat_qty):
                return f"材料不足：需要 {ITEMS[mat_id]['name']} x{mat_qty}"
        
        for mat_id, mat_qty in cost.items():
            self.game.remove_item(mat_id, mat_qty)
        
        if facility == "shelter":
            self.game.camp["built"] = True
        elif facility == "fire":
            self.game.camp["has_fire"] = True
        elif facility == "water_filter":
            self.game.camp["has_water_filter"] = True
        elif facility == "storage":
            self.game.camp["has_storage"] = True
        elif facility == "defense":
            self.game.camp["defense_level"] += 1
        elif facility == "torch":
            self.game.add_item("torch", 2)
            self.game.camp["torches"] += 2
        elif facility == "boat_part":
            self.game.boat_parts += 1
            if self.game.boat_parts >= self.game.total_boat_parts:
                self.game.victory = True
                self.game.ending = "build_boat"
                self.game.game_over = True
                self.game.calculate_score()
                text = "🏆 你造好了一艘小船！你成功离开了这座荒岛！\n"
                ending = ENDINGS["build_boat"]
                text += f"{ending['description']}\n"
                text += f"\n最终得分：{self.game.score}"
                return text
        
        turns = 2 if facility in ["shelter", "boat_part"] else 1
        advance_msg = self.game.advance_turn(turns)
        
        result = f"建造了 {facility_names[facility]}！"
        if facility == "defense":
            result = f"防御等级提升到 {self.game.camp['defense_level']}！"
        elif facility == "boat_part":
            result = f"船只零件进度：{self.game.boat_parts}/{self.game.total_boat_parts}"
        
        self.game.log_action(f"建造 {facility_names[facility]}")
        if advance_msg:
            result += f"\n{advance_msg}"
        return result

    def cmd_event(self, args):
        if self.game.game_over:
            return "游戏已结束。"
        if not self.game.player_name:
            return "请先开始新游戏。"
        
        if not args:
            return "用法：event trigger | recruit | list_companions | trade | weather"
        
        subcmd = args[0]
        
        if subcmd == "trigger":
            msg = self._trigger_random_event()
            if msg:
                advance_msg = self.game.advance_turn(1)
                if advance_msg:
                    msg += f"\n{advance_msg}"
                return msg
            return "今天风平浪静，什么都没有发生。"
        
        elif subcmd == "list_companions":
            text = "=== 可招募伙伴 ===\n"
            for comp_id, comp_data in COMPANIONS.items():
                cost = ", ".join([f"{ITEMS[m]['name']} x{n}" for m, n in comp_data["recruit_cost"].items()])
                recruited = " [已招募]" if comp_id in self.game.companions else ""
                text += f"  {comp_id:10} - {comp_data['name']}{recruited}\n"
                text += f"      {comp_data['description']}\n"
                text += f"      招募费用: {cost}\n"
            return text
        
        elif subcmd == "recruit":
            if len(args) < 2:
                return "用法：event recruit <伙伴ID>"
            
            comp_id = args[1]
            if comp_id not in COMPANIONS:
                return f"未知伙伴：{comp_id}"
            if comp_id in self.game.companions:
                return "你已经招募了这个伙伴。"
            if len(self.game.companions) >= 3:
                return "最多只能招募3个伙伴。"
            
            comp = COMPANIONS[comp_id]
            for mat_id, mat_qty in comp["recruit_cost"].items():
                if not self.game.has_item(mat_id, mat_qty):
                    return f"资源不足：需要 {ITEMS[mat_id]['name']} x{mat_qty}"
            
            for mat_id, mat_qty in comp["recruit_cost"].items():
                self.game.remove_item(mat_id, mat_qty)
            
            self.game.companions.append(comp_id)
            self.game.log_action(f"招募伙伴 {comp['name']}")
            advance_msg = self.game.advance_turn(1)
            
            result = f"🎉 你成功招募了 {comp['name']}！\n{comp['description']}"
            if advance_msg:
                result += f"\n{advance_msg}"
            return result
        
        elif subcmd == "trade":
            if not self.game.trader_available:
                return "现在没有商人。可以使用 event trigger 尝试触发商人事件。"
            
            if len(args) < 3:
                return "用法：event trade buy <物品> [数量] 或 event trade sell <物品> [数量]\n示例：event trade buy water 3"
            
            trade_type = args[1]
            item_name = args[2]
            
            if len(args) > 3:
                success, result = parse_int_param(
                    args[3], min_val=1, max_val=99, param_name="交易数量"
                )
                if not success:
                    return result + "\n用法：event trade buy/sell <物品> [数量]"
                quantity = result
            else:
                quantity = 1
            
            item_id = self._find_item_id(item_name)
            if not item_id:
                return f"找不到物品：{item_name}\n用法：event trade buy/sell <物品> [数量]"
            
            if trade_type == "buy":
                if item_id not in TRADER_ITEMS["buy"]:
                    return f"商人不卖 {item_name}\n输入 event list 查看商人出售的物品"
                price = TRADER_ITEMS["buy"][item_id]["price"]
                for currency, amount in price.items():
                    total = amount * quantity
                    if not self.game.has_item(currency, total):
                        return f"货币不足：需要 {ITEMS[currency]['name']} x{total}，当前只有 {self.game.get_item_count(currency)}"
                for currency, amount in price.items():
                    self.game.remove_item(currency, amount * quantity)
                self.game.add_item(item_id, quantity)
                
                if item_id == "map_fragment":
                    self.game._check_treasure_ending()
                
                self.game.log_action(f"从商人购买 {ITEMS[item_id]['name']} x{quantity}")
                return f"购买成功：{ITEMS[item_id]['name']} x{quantity}"
            
            elif trade_type == "sell":
                if item_id not in TRADER_ITEMS["sell"]:
                    return f"商人不收 {item_name}\n商人收购：shell, ancient_coin, gold, iron_ore, iron_ingot"
                if not self.game.has_item(item_id, quantity):
                    return f"物品不足：{ITEMS[item_id]['name']} 需要 x{quantity}，当前只有 {self.game.get_item_count(item_id)}"
                self.game.remove_item(item_id, quantity)
                price = TRADER_ITEMS["sell"][item_id]["price"] * quantity
                self.game.add_item("shell", price)
                self.game.log_action(f"卖给商人 {ITEMS[item_id]['name']} x{quantity}，获得贝壳 x{price}")
                return f"出售成功：获得贝壳 x{price}"
            
            return "未知交易类型。用法：event trade buy 或 sell"
        
        elif subcmd == "weather":
            if self.game.weather_forecast:
                weather_data = EVENTS.get(self.game.weather_forecast, {})
                return f"天气预报：{weather_data.get('message', '未知天气')}\n当前天气：{self.game.weather}"
            return "天气预报：近期天气晴朗\n当前天气：晴朗"
        
        return "未知子命令。用法：event trigger | recruit | list_companions | trade | weather"

    def _trigger_random_event(self):
        config = DIFFICULTY_CONFIG[self.game.difficulty]
        if random.random() > config["event_chance"]:
            return None
        
        events = list(EVENTS.items())
        total_weight = sum(e[1]["weight"] for e in events)
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for event_id, event_data in events:
            cumulative += event_data["weight"]
            if r <= cumulative:
                return self._process_event(event_id, event_data)
        
        return None

    def _process_event(self, event_id, event_data):
        text = f"⚠️ 事件：{event_data['name']}\n{event_data['message']}\n"
        self.game.log_event(f"{event_data['name']}: {event_data['message']}")
        
        event_type = event_data["type"]
        
        if event_type == "danger":
            min_dmg = event_data.get("min_damage", 10)
            max_dmg = event_data.get("max_damage", 20)
            damage = random.randint(min_dmg, max_dmg)
            
            if event_data.get("can_defend"):
                total_attack = self.game.get_total_attack()
                if total_attack > 20 and random.random() < 0.3:
                    damage = damage // 2
                    text += f"你成功躲避了部分攻击！\n"
            
            for comp in self.game.companions:
                damage = int(damage * (1 - COMPANIONS[comp]["stats"].get("danger_reduction", 0)))
            
            self.game.health -= damage
            text += f"受到 {damage} 点伤害！\n"
            
            if event_data.get("poison"):
                self.game.is_poisoned = True
                self.game.poison_damage = random.randint(3, 8)
                text += "你中毒了！每回合将持续受到伤害。\n"
            
            if damage > 15 and random.random() < 0.3:
                self.game.is_infected = True
                text += "伤口感染了！\n"
        
        elif event_type == "positive":
            if "rewards" in event_data:
                reward = random.choice(event_data["rewards"])
                for item_id, qty in reward.items():
                    self.game.add_item(item_id, qty)
                    text += f"获得 {ITEMS[item_id]['name']} x{qty}\n"
                    if item_id == "map_fragment":
                        text += f"    🗺️  地图碎片进度: {self.game.map_fragments}/{self.game.total_map_fragments}\n"
                
                if self.game.game_over and self.game.victory and self.game.ending == "treasure":
                    ending = ENDINGS["treasure"]
                    text += "\n🏆 你收集齐了所有地图碎片！你找到了传说中的宝藏！\n"
                    text += f"{ending['description']}\n"
                    text += f"\n最终得分：{self.game.score}"
                    return text
            
            if event_id == "find_survivor":
                available = [c for c in COMPANIONS if c not in self.game.companions]
                if available and len(self.game.companions) < 3:
                    comp_id = random.choice(available)
                    comp = COMPANIONS[comp_id]
                    text += f"\n幸存者 {comp['name']} 愿意加入你的队伍！\n"
                    text += f"是否招募？(需要支付招募费用)\n"
                    text += f"输入 event recruit {comp_id} 来招募。"
        
        elif event_type == "weather":
            self.game.weather = event_id
            if "effect" in event_data:
                for stat, value in event_data["effect"].items():
                    if stat == "health":
                        self.game.health += value
                    elif stat == "hunger":
                        self.game.hunger += value
                    elif stat == "thirst":
                        self.game.thirst += value
                text += "状态受到影响！\n"
        
        elif event_type == "trade":
            self.game.trader_available = True
            text += "商人带来了以下物品：\n"
            text += "购买：\n"
            for item_id, data in TRADER_ITEMS["buy"].items():
                price = ", ".join([f"{ITEMS[c]['name']}x{n}" for c, n in data["price"].items()])
                text += f"  {ITEMS[item_id]['name']} - {price}\n"
            text += "出售（贝壳）：\n"
            for item_id, data in TRADER_ITEMS["sell"].items():
                text += f"  {ITEMS[item_id]['name']} - {data['price']}\n"
            text += "\n使用 event trade buy/sell <物品> 进行交易。"
        
        if self.game.health <= 0:
            death_msg = self.game.check_death()
            if death_msg:
                text += f"\n{death_msg}"
                text += f"\n最终得分：{self.game.score}"
        
        return text

    def cmd_save(self, args):
        if not args:
            return "用法：save save <名字> | load <名字> | list | replay | score"
        
        subcmd = args[0]
        
        if subcmd == "list":
            saves = GameState.list_saves()
            if not saves:
                return "没有存档。"
            text = "=== 存档列表 ===\n"
            for save in saves:
                status = "✓" if save["victory"] else "✗" if save["game_over"] else "▶"
                diff = DIFFICULTY_CONFIG[save["difficulty"]]["name"]
                text += f"  {status} {save['slot']:15} - {save['player']:10} 第{save['day']:3}天 {diff:4} - {save['saved_at']}\n"
            return text
        
        elif subcmd == "save":
            if len(args) < 2:
                return "用法：save save <存档名>"
            if self.game.game_over:
                return "游戏已结束，无法保存。"
            slot = args[1]
            return self.game.save_game(slot)
        
        elif subcmd == "load":
            if len(args) < 2:
                return "用法：save load <存档名>"
            slot = args[1]
            success, msg = self.game.load_game(slot)
            if success:
                if self.game.game_over:
                    msg += "\n注意：该存档游戏已结束。"
            return msg
        
        elif subcmd == "replay":
            if not self.game.game_over:
                return "只有游戏结束后才能查看死亡回放。"
            
            text = "=== 死亡回放 ===\n"
            text += f"玩家：{self.game.player_name}\n"
            text += f"生存天数：{self.game.day} 天\n"
            text += f"难度：{DIFFICULTY_CONFIG[self.game.difficulty]['name']}\n"
            if self.game.ending:
                ending = ENDINGS.get(self.game.ending, {})
                text += f"结局：{ending.get('name', '未知')}\n"
                text += f"{ending.get('description', '')}\n"
            text += "\n--- 事件记录 ---\n"
            for event in self.game.event_log[-20:]:
                text += f"{event}\n"
            text += "\n--- 行动记录 ---\n"
            for action in self.game.action_log[-20:]:
                text += f"{action}\n"
            return text
        
        elif subcmd == "score":
            if not self.game.game_over:
                return "只有游戏结束后才能查看最终评分。"
            
            self.game.calculate_score()
            text = "=== 结局评分 ===\n"
            if self.game.ending:
                ending = ENDINGS.get(self.game.ending, {})
                text += f"结局：{ending.get('name', '未知')}\n"
                text += f"{ending.get('description', '')}\n"
            text += f"\n基础分：{ENDINGS.get(self.game.ending, {}).get('score', 0)}\n"
            text += f"生存奖励：{self.game.day * 2} ({self.game.day}天 × 2)\n"
            text += f"伙伴奖励：{len(self.game.companions) * 10} ({len(self.game.companions)}人 × 10)\n"
            text += f"地图奖励：{self.game.map_fragments * 5} ({self.game.map_fragments}块 × 5)\n"
            diff_mult = {"easy": 0.8, "normal": 1.0, "hard": 1.5, "nightmare": 2.0}[self.game.difficulty]
            text += f"难度系数：×{diff_mult}\n"
            text += f"\n最终得分：{self.game.score}\n"
            
            if self.game.score >= 200:
                text += "\n评价：传奇生存者！你是真正的荒岛之王！"
            elif self.game.score >= 150:
                text += "\n评价：优秀生存者！你的生存技能令人印象深刻。"
            elif self.game.score >= 100:
                text += "\n评价：熟练生存者！你成功适应了荒岛生活。"
            elif self.game.score >= 50:
                text += "\n评价：初级生存者。你还有很多需要学习。"
            else:
                text += "\n评价：新手。下次会更好的！"
            
            return text
        
        return "未知子命令。用法：save save | load | list | replay | score"

    def cmd_status(self, args):
        if not self.game.player_name:
            return "请先开始新游戏。"
        
        time_map = {"day": "白天", "night": "夜晚"}
        weather_map = {"clear": "晴朗", "storm": "暴风雨", "heatwave": "热浪", "cold_snap": "寒流"}
        
        text = f"=== {self.game.player_name} 的状态 ===\n"
        text += f"第 {self.game.day} 天 {time_map[self.game.time_of_day]} 回合 {self.game.turn}\n"
        text += f"难度：{DIFFICULTY_CONFIG[self.game.difficulty]['name']}\n"
        text += f"位置：{MAP_LOCATIONS[self.game.current_location]['name']}\n"
        text += f"天气：{weather_map.get(self.game.weather, '晴朗')}\n"
        text += "\n"
        
        bar_length = 20
        hp_bar = "█" * int(self.game.health / self.game.max_health * bar_length) + "░" * (bar_length - int(self.game.health / self.game.max_health * bar_length))
        hunger_bar = "█" * int(self.game.hunger / 100 * bar_length) + "░" * (bar_length - int(self.game.hunger / 100 * bar_length))
        thirst_bar = "█" * int(self.game.thirst / 100 * bar_length) + "░" * (bar_length - int(self.game.thirst / 100 * bar_length))
        
        text += f"生命: [{hp_bar}] {self.game.health}/{self.game.max_health}\n"
        text += f"饱食: [{hunger_bar}] {self.game.hunger}/100\n"
        text += f"口渴: [{thirst_bar}] {self.game.thirst}/100\n"
        
        status_effects = []
        if self.game.is_poisoned:
            status_effects.append(f"中毒({self.game.poison_damage}伤害/回合)")
        if self.game.is_infected:
            status_effects.append("伤口感染")
        if status_effects:
            text += f"\n状态: {', '.join(status_effects)}\n"
        
        if self.game.companions:
            text += f"\n伙伴: {len(self.game.companions)}人\n"
        
        if self.game.trader_available:
            text += "\n商人在营地，可以交易！\n"
        
        if self.game.weather_forecast:
            forecast = EVENTS.get(self.game.weather_forecast, {})
            text += f"\n天气预报: {forecast.get('message', '')}\n"
        
        return text

    def cmd_use(self, args):
        if not args:
            return "用法：use <物品> [数量]"
        return self.cmd_bag(["use"] + args)

    def cmd_rest(self, args):
        if self.game.game_over:
            return "游戏已结束。"
        if not self.game.player_name:
            return "请先开始新游戏。"
        
        if args:
            success, result = parse_int_param(
                args[0], min_val=1, max_val=8, param_name="休息回合数"
            )
            if not success:
                return result + "\n用法：rest [回合数]，回合数范围1-8"
            turns = result
        else:
            turns = 1
        
        summary = {
            "total_heal": 0,
            "weather_effects": [],
            "events": [],
            "turn_summary": []
        }
        
        for turn in range(1, turns + 1):
            turn_log = [f"--- 休息第{turn}回合 ---"]
            old_health = self.game.health
            
            if self.game.current_location != "camp":
                heal_per_turn = 2
            else:
                heal_per_turn = 5
                if self.game.camp["has_fire"]:
                    heal_per_turn += 2
                for comp in self.game.companions:
                    heal_per_turn += int(COMPANIONS[comp]["stats"].get("heal_bonus", 0) * 3)
            
            old_health_before = self.game.health
            self.game.health = min(self.game.max_health, self.game.health + heal_per_turn)
            actual_heal = self.game.health - old_health_before
            summary["total_heal"] += actual_heal
            
            turn_log.append(f"  恢复生命值 +{actual_heal}")
            
            advance_msg = self.game.advance_turn(1)
            
            health_change = self.game.health - old_health
            if health_change != 0:
                turn_log.append(f"  生命变化: {health_change:+d}")
            
            if self.game.weather != "clear":
                weather_names = {"storm": "暴风雨", "heatwave": "热浪", "cold_snap": "寒流"}
                summary["weather_effects"].append(f"第{turn}回合: {weather_names.get(self.game.weather, '恶劣天气')}")
            
            if advance_msg:
                turn_log.append(f"  {advance_msg}")
            
            event_msg = self._trigger_random_event()
            if event_msg:
                summary["events"].append(f"第{turn}回合: {event_msg.split(chr(10))[0]}")
                turn_log.append(f"  ⚠️ 发生事件")
            
            summary["turn_summary"].append("\n".join(turn_log))
            
            if self.game.game_over:
                break
        
        location = "野外" if self.game.current_location != "camp" else "营地"
        text = f"=== 在{location}休息 {turns} 回合 ===\n"
        
        if turns > 1:
            text += "\n".join(summary["turn_summary"]) + "\n"
        
        text += "\n=== 休息汇总 ===\n"
        text += f"总恢复生命值: +{summary['total_heal']}\n"
        
        if summary["weather_effects"]:
            text += "\n天气影响：\n"
            for msg in summary["weather_effects"]:
                text += f"  {msg}\n"
        
        if summary["events"]:
            text += "\n遭遇事件：\n"
            for msg in summary["events"]:
                text += f"  {msg}\n"
        
        text += f"\n最终状态: 生命{self.game.health}/{self.game.max_health} 饱食{self.game.hunger} 口渴{self.game.thirst}\n"
        
        self.game.log_action(f"在{location}休息{turns}回合，恢复+{summary['total_heal']}生命")
        
        if self.game.game_over:
            text += f"\n{self.game.check_death()}"
            if self.game.game_over:
                text += f"\n最终得分：{self.game.score}"
        
        return text
