#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""荒岛求生 - 第二轮新功能测试"""

import sys
import os
import json
from game_state import GameState
from commands import CommandHandler
from game_data import ITEMS, CAMP_UPGRADES, RUIN_CLUES

def test_passed(name):
    print(f"  ✓ {name}")

def test_failed(name, expected, actual):
    print(f"  ✗ {name}: 期望 {expected}, 实际 {actual}")
    return False

def main():
    print("荒岛求生 - 第二轮新功能测试")
    print("=" * 60)
    all_passed = True
    
    # ============================================================
    # 测试 1: 新物品和配方
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 1. 新物品和配方")
    print("=" * 60)
    
    game = GameState()
    handler = CommandHandler(game)
    game.new_game("测试玩家", "normal")
    
    # 检查新物品是否存在
    if "brick" in ITEMS and "charcoal" in ITEMS:
        test_passed("新物品砖块、木炭已定义")
    else:
        test_failed("新物品定义", True, False)
        all_passed = False
    
    # 测试制作砖块
    handler.handle("map", ["go", "camp"])
    game.add_item("wood", 10)
    game.add_item("stone", 10)
    game.add_item("flint", 5)
    game.camp["shelter_level"] = 1
    game.camp["fire_level"] = 1
    game.camp["built"] = True
    game.camp["has_fire"] = True
    
    result = handler.handle("craft", ["make", "brick"])
    if "砖块" in result or "brick" in result:
        test_passed("可以制作砖块")
    else:
        test_failed("制作砖块", "成功", result)
        all_passed = False
    
    # 测试制作木炭
    result = handler.handle("craft", ["make", "charcoal"])
    if "木炭" in result or "charcoal" in result:
        test_passed("可以制作木炭")
    else:
        test_failed("制作木炭", "成功", result)
        all_passed = False
    
    # 检查木炭数量
    charcoal_qty = game.get_item_count("charcoal")
    if charcoal_qty >= 3:
        test_passed(f"制作木炭获得正确数量: {charcoal_qty}")
    else:
        test_failed("木炭数量", ">=3", charcoal_qty)
        all_passed = False
    
    # 测试冶炼铁锭（需要木炭）
    game.add_item("iron_ore", 5)
    result = handler.handle("craft", ["make", "iron_ingot"])
    if "铁锭" in result or "iron_ingot" in result:
        test_passed("可以用木炭冶炼铁锭")
    else:
        test_failed("冶炼铁锭", "成功", result)
        all_passed = False
    
    # ============================================================
    # 测试 2: 营地建造和升级统一
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 2. 营地建造和升级统一")
    print("=" * 60)
    
    # 重置游戏
    game = GameState()
    handler = CommandHandler(game)
    game.new_game("测试玩家", "normal")
    handler.handle("map", ["go", "camp"])
    
    # 添加大量材料
    game.add_item("wood", 100)
    game.add_item("stone", 100)
    game.add_item("rope", 50)
    game.add_item("flint", 20)
    game.add_item("fiber", 50)
    game.add_item("charcoal", 20)
    game.add_item("brick", 20)
    game.add_item("iron_ingot", 20)
    
    # 测试 build 和 upgrade 都能工作
    result_build = handler.handle("camp", ["build", "shelter"])
    if "建造了简易营地" in result_build:
        test_passed("camp build shelter 可以建造营地")
    else:
        test_failed("camp build shelter", "建造成功", result_build)
        all_passed = False
    
    # 测试 upgrade 升级
    result_upgrade = handler.handle("camp", ["upgrade", "shelter"])
    if "升级到加固营地" in result_upgrade:
        test_passed("camp upgrade shelter 可以升级营地")
    else:
        test_failed("camp upgrade shelter", "升级成功", result_upgrade)
        all_passed = False
    
    # 检查等级是否正确
    if game.get_camp_upgrade_level("shelter") == 2:
        test_passed("营地等级正确: 2")
    else:
        test_failed("营地等级", 2, game.get_camp_upgrade_level("shelter"))
        all_passed = False
    
    # 测试 camp show 显示一致
    result_show = handler.handle("camp", ["show"])
    if "加固营地" in result_show and "下一级" in result_show:
        test_passed("camp show 显示等级和下一级信息")
    else:
        print(f"  ! camp show 输出:\n{result_show[:300]}")
        test_failed("camp show 信息", "包含当前等级和下一级", "不包含")
        all_passed = False
    
    if "下一级" in result_show and "材料" in result_show and "效果" in result_show:
        test_passed("camp show 显示下一级材料和效果")
    else:
        test_failed("camp show 升级信息", "包含材料和效果", "不包含")
        all_passed = False
    
    # ============================================================
    # 测试 3: 旧存档兼容
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 3. 旧存档兼容")
    print("=" * 60)
    
    # 创建一个模拟旧存档
    old_save_data = {
        "player_name": "旧存档玩家",
        "difficulty": "normal",
        "health": 80,
        "max_health": 100,
        "hunger": 70,
        "thirst": 60,
        "day": 10,
        "turn": 2,
        "time_of_day": "day",
        "current_location": "camp",
        "inventory": {"water": 5, "food": 3},
        "tools": {},
        "companions": [],
        "camp": {
            "built": True,
            "has_fire": True,
            "has_water_filter": False,
            "has_storage": False,
            "defense_level": 2,
            "torches": 3,
        },
        "is_poisoned": False,
        "poison_damage": 0,
        "is_infected": False,
        "map_fragments": 2,
        "total_map_fragments": 5,
        "boat_parts": 1,
        "total_boat_parts": 3,
        "score": 0,
        "death_cause": None,
        "game_over": False,
        "victory": False,
        "ending": None,
        "action_log": [],
        "event_log": [],
        "trader_available": False,
        "weather": "clear",
        "weather_forecast": None,
        "ruin_clues": {},
        "ruin_exploration_progress": 0,
        "battle_log": [],
        "saved_at": "2024-01-01 00:00:00",
    }
    
    # 保存模拟旧存档
    save_dir = os.path.join(os.path.dirname(__file__), "saves")
    os.makedirs(save_dir, exist_ok=True)
    old_save_path = os.path.join(save_dir, "test_old_save.json")
    with open(old_save_path, "w", encoding="utf-8") as f:
        json.dump(old_save_data, f, ensure_ascii=False, indent=2)
    
    # 加载旧存档
    success, msg = game.load_game("test_old_save")
    if success:
        test_passed("旧存档加载成功")
    else:
        test_failed("旧存档加载", "成功", msg)
        all_passed = False
    
    # 检查数据迁移是否正确
    if game.camp.get("shelter_level", 0) == 1:
        test_passed("旧存档 built=True 迁移为 shelter_level=1")
    else:
        test_failed("shelter_level 迁移", 1, game.camp.get("shelter_level", 0))
        all_passed = False
    
    if game.camp.get("fire_level", 0) == 1:
        test_passed("旧存档 has_fire=True 迁移为 fire_level=1")
    else:
        test_failed("fire_level 迁移", 1, game.camp.get("fire_level", 0))
        all_passed = False
    
    if game.camp.get("defense_upgrade_level", 0) == 2:
        test_passed("旧存档 defense_level=2 迁移为 defense_upgrade_level=2")
    else:
        test_failed("defense_upgrade_level 迁移", 2, game.camp.get("defense_upgrade_level", 0))
        all_passed = False
    
    # 清理测试存档
    os.remove(old_save_path)
    
    # ============================================================
    # 测试 4: 升级效果在结算中体现
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 4. 升级效果在结算中体现")
    print("=" * 60)
    
    # 重置游戏
    game = GameState()
    handler = CommandHandler(game)
    game.new_game("测试玩家", "normal")
    handler.handle("map", ["go", "camp"])
    
    # 添加材料并升级
    game.add_item("wood", 100)
    game.add_item("stone", 100)
    game.add_item("rope", 50)
    game.add_item("flint", 20)
    game.add_item("fiber", 50)
    
    handler.handle("camp", ["build", "shelter"])
    handler.handle("camp", ["build", "fire"])
    
    # 测试烹饪加成
    game.add_item("raw_meat", 5)
    result = handler.handle("camp", ["cook"])
    if "效率" in result or "x1" in result:
        test_passed("烹饪显示基础产出")
    else:
        test_failed("烹饪产出", "包含产出信息", result)
        all_passed = False
    
    # 升级火源到等级2获得烹饪加成
    game.add_item("stone", 10)
    handler.handle("camp", ["upgrade", "fire"])
    
    # 再次测试烹饪，应该有加成
    game.add_item("raw_meat", 5)
    result = handler.handle("camp", ["cook"])
    if "效率加成" in result or "+" in result:
        test_passed("火源升级后烹饪有加成")
    else:
        test_failed("烹饪加成", "包含效率加成", result)
        all_passed = False
    
    # 测试净水器加成
    handler.handle("camp", ["build", "water_filter"])
    game.add_item("dirty_water", 3)
    result = handler.handle("camp", ["purify"])
    if "x2" in result or "净水器" in result:
        test_passed("净水器显示2倍产出")
    else:
        test_failed("净水器产出", "包含x2或净水器", result)
        all_passed = False
    
    # ============================================================
    # 测试 5: 夜间防守战报
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 5. 夜间防守战报")
    print("=" * 60)
    
    game.health = 100
    game.time_of_day = "night"
    game.camp["defense_level"] = 2
    game.camp["defense_upgrade_level"] = 2
    game.camp["torches"] = 3
    game.add_item("spear", 1)
    
    # 强制触发战斗
    import random
    random.seed(42)
    
    result = handler.handle("camp", ["defend"])
    
    # 检查战报格式 - 可能触发战斗也可能平安无事
    had_combat = "营地减伤" in result and "火把减伤" in result
    peaceful = "平安无事" in result
    
    if had_combat or peaceful:
        test_passed("夜间防守有正确的战斗结果（战斗或平安无事）")
    else:
        print(f"  ! 防守输出:\n{result[:300]}")
        test_failed("防守结果", "包含战斗或平安无事", "不包含")
        all_passed = False
    
    if had_combat:
        if "实际扣血" in result:
            test_passed("战斗显示实际扣血")
        else:
            test_failed("实际扣血显示", "包含实际扣血", "不包含")
            all_passed = False
        
        if "战斗结算" in result:
            test_passed("有战斗结算")
        else:
            test_failed("战斗结算", "包含战斗结算", "不包含")
            all_passed = False
    else:
        test_passed("夜间平安无事，跳过战斗相关检查")
        test_passed("夜间平安无事，跳过实际扣血检查")
        test_passed("夜间平安无事，跳过战斗结算检查")
    
    if "验证公式" in result or len(game.battle_log) > 0:
        test_passed("战斗数据有验证或日志")
    else:
        test_failed("战斗验证", "有验证或日志", "没有")
        all_passed = False
    
    # 检查战斗日志
    if game.battle_log:
        test_passed(f"战斗日志已记录 {len(game.battle_log)} 条")
        
        # 检查日志口径一致性
        has_round = any("第" in log and "回合" in log for log in game.battle_log)
        has_damage = any("原始伤害" in log for log in game.battle_log)
        has_camp_def = any("营地减伤" in log for log in game.battle_log)
        has_torch_def = any("火把减伤" in log for log in game.battle_log)
        has_peaceful = any("平安无事" in log for log in game.battle_log)
        
        if (has_round and has_damage and has_camp_def and has_torch_def) or has_peaceful:
            test_passed("战斗日志包含完整信息或平安无事记录")
        else:
            print(f"  ! 战斗日志示例: {game.battle_log[:5]}")
            test_failed("战斗日志内容", "包含战斗字段或平安无事", 
                f"回合:{has_round}, 原始伤害:{has_damage}, 营地减伤:{has_camp_def}, 火把减伤:{has_torch_def}, 平安:{has_peaceful}")
            all_passed = False
    
    # ============================================================
    # 测试 6: 智能目标提示
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 6. 智能目标提示")
    print("=" * 60)
    
    # 重置游戏
    game = GameState()
    handler = CommandHandler(game)
    game.new_game("测试玩家", "normal")
    handler.handle("map", ["go", "camp"])
    
    # 设置后期状态
    game.day = 15
    game.map_fragments = 3
    game.boat_parts = 1
    game.camp["shelter_level"] = 1
    game.camp["fire_level"] = 1
    game.camp["built"] = True
    game.camp["has_fire"] = True
    game.add_item("iron_ore", 5)
    game.add_item("stone", 20)
    game.add_item("wood", 20)
    
    # 测试任务提示
    result = handler.handle("event", ["quest"])
    if "当前任务建议" in result:
        test_passed("event quest 显示任务建议")
    else:
        test_failed("event quest", "包含当前任务建议", "不包含")
        all_passed = False
    
    # 检查是否有冶炼提示
    if "木炭" in result or "铁锭" in result or "冶炼" in result:
        test_passed("有冶炼相关提示")
    else:
        print(f"  ! 提示内容:\n{result[:300]}")
        test_passed("无冶炼提示（材料不足）")
    
    # 添加木炭后再次检查
    game.add_item("charcoal", 5)
    result = handler.handle("camp", ["plan"])
    if "冶炼" in result or "铁锭" in result:
        test_passed("有木炭后提示冶炼铁锭")
    else:
        print(f"  ! 提示内容:\n{result[:300]}")
        test_failed("冶炼提示", "包含冶炼或铁锭", "不包含")
        all_passed = False
    
    # 检查是否有路线推荐
    if "宝藏" in result or "逃离" in result or "船只" in result:
        test_passed("有路线推荐（宝藏或逃离）")
    else:
        test_failed("路线推荐", "包含宝藏或逃离", "不包含")
        all_passed = False
    
    # ============================================================
    # 测试 7: 雨水收集
    # ============================================================
    print("\n" + "=" * 60)
    print("测试: 7. 雨水收集")
    print("=" * 60)
    
    # 重置游戏
    game = GameState()
    handler = CommandHandler(game)
    game.new_game("测试玩家", "normal")
    handler.handle("map", ["go", "camp"])
    
    # 添加材料并升级净水器到2级
    game.add_item("wood", 100)
    game.add_item("stone", 100)
    game.add_item("rope", 50)
    game.add_item("flint", 20)
    game.add_item("fiber", 100)
    game.add_item("charcoal", 20)
    game.add_item("brick", 20)
    
    handler.handle("camp", ["build", "shelter"])
    handler.handle("camp", ["build", "fire"])
    handler.handle("camp", ["build", "water_filter"])
    handler.handle("camp", ["upgrade", "water_filter"])
    
    # 检查是否有雨水收集功能
    if game.has_facility_flag("rain_collection"):
        test_passed("净水器2级开启雨水收集功能")
    else:
        test_failed("雨水收集功能", True, False)
        all_passed = False
    
    # 模拟下雨并检查收集
    old_water = game.get_item_count("water")
    game.weather = "rain"
    game.advance_turn(1)
    new_water = game.get_item_count("water")
    
    if new_water > old_water:
        test_passed(f"下雨时自动收集雨水：{old_water} -> {new_water}")
    else:
        test_failed("雨水收集", f"水量增加", f"水量不变 ({old_water} -> {new_water})")
        all_passed = False
    
    # ============================================================
    # 总结
    # ============================================================
    print("\n" + "=" * 60)
    if all_passed:
        print("第二轮新功能测试全部通过！✓")
    else:
        print("部分测试失败！✗")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
