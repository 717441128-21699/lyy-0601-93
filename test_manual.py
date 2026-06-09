#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""手动测试：验证主要功能正常工作"""

from game_state import GameState
from commands import CommandHandler
import random

def test_all_features():
    print("荒岛求生 - 手动测试")
    print("=" * 60)
    
    # 初始化
    game = GameState()
    handler = CommandHandler(game)
    all_passed = [True]
    
    def test_passed(name):
        print(f"  ✓ {name}")
    
    def test_failed(name, expected, actual):
        all_passed[0] = False
        print(f"  ✗ {name}: 期望 {expected}, 实际 {actual}")
    
    def ensure_game_running():
        if game.game_over:
            game.game_over = False
            game.health = 500
            game.hunger = 200
            game.thirst = 200
    
    # 测试1: 开始游戏
    print("\n【测试1: 游戏初始化】")
    game.new_game("测试玩家", "easy")  # 用简单模式防止测试中死亡
    game.health = 500  # 大幅增加生命值防止测试中死亡
    game.max_health = 500
    game.hunger = 200  # 增加饱食度
    game.thirst = 200  # 增加口渴度
    test_passed("新游戏创建成功")
    if game.player_name == "测试玩家":
        test_passed("玩家名称正确")
    else:
        test_failed("玩家名称", "测试玩家", game.player_name)
    
    # 测试2: 采集资源
    print("\n【测试2: 资源采集】")
    handler.handle("map", ["go", "beach"])
    result = handler.handle("map", ["gather", "1"])
    if "收获" in result or "获得" in result:
        test_passed("采集资源成功")
    else:
        test_failed("采集资源", "有收获", result[:50])
    
    # 测试3: 营地建造升级
    print("\n【测试3: 营地建造升级】")
    handler.handle("map", ["go", "camp"])
    game.add_item("wood", 50)
    game.add_item("stone", 30)
    game.add_item("rope", 10)
    game.add_item("flint", 5)
    game.add_item("vine", 10)
    game.add_item("leather", 10)
    game.add_item("iron_ore", 10)
    game.add_item("dirty_water", 20)
    
    # build shelter
    result = handler.handle("camp", ["build", "shelter"])
    if "建造了" in result or "升级到" in result or "建造成功" in result or "升级成功" in result:
        test_passed("camp build shelter 成功")
    else:
        test_failed("camp build shelter", "成功", result[:100])
    
    # upgrade shelter
    result = handler.handle("camp", ["upgrade", "shelter"])
    if "升级到" in result or "建造了" in result or "升级成功" in result or "建造成功" in result:
        test_passed("camp upgrade shelter 成功")
    else:
        test_failed("camp upgrade shelter", "成功", result[:100])
    
    # 检查等级
    if game.get_camp_upgrade_level("shelter") == 2:
        test_passed("营地等级正确 (2级)")
    else:
        test_failed("营地等级", 2, game.get_camp_upgrade_level("shelter"))
    
    # 测试4: camp show
    print("\n【测试4: camp show 显示】")
    result = handler.handle("camp", ["show"])
    if "加固营地" in result and "下一级" in result:
        test_passed("camp show 显示正确信息")
    else:
        print(f"  ! 输出:\n{result[:200]}")
        test_failed("camp show", "包含加固营地和下一级", "不包含")
    
    # 测试5: 建造火源和净水器
    print("\n【测试5: 设施建造】")
    ensure_game_running()
    game.add_item("vine", 50)  # 补充足够材料
    game.add_item("rope", 30)
    game.add_item("fiber", 50)
    game.add_item("charcoal", 20)
    
    result = handler.handle("camp", ["build", "fire"])
    if "建造了" in result or "成功" in result:
        test_passed("建造火源成功")
    else:
        test_failed("建造火源", "成功", result[:100])
    
    result = handler.handle("camp", ["build", "water_filter"])
    if "建造了" in result or "成功" in result:
        test_passed("建造净水器成功")
    else:
        test_failed("建造净水器", "成功", result[:100])
    
    # 升级火源和净水器以获得加成
    game.add_item("stone", 40)
    game.add_item("wood", 40)
    game.add_item("brick", 20)
    result = handler.handle("camp", ["upgrade", "fire"])
    if "升级到" in result or "成功" in result:
        test_passed("升级火源到2级成功")
    else:
        test_failed("升级火源", "成功", result[:100])
    
    result = handler.handle("camp", ["upgrade", "water_filter"])
    if "升级到" in result or "成功" in result:
        test_passed("升级净水器到2级成功")
    else:
        test_failed("升级净水器", "成功", result[:100])
    
    # 测试6: 制作砖块和木炭
    print("\n【测试6: 资源链制作】")
    ensure_game_running()
    game.add_item("wood", 10)
    game.add_item("stone", 10)
    
    result = handler.handle("craft", ["make", "brick"])
    if "砖块" in result or "brick" in result:
        test_passed("制作砖块成功")
    else:
        test_failed("制作砖块", "成功", result[:100])
    
    result = handler.handle("craft", ["make", "charcoal"])
    if "木炭" in result or "charcoal" in result:
        test_passed("制作木炭成功")
    else:
        test_failed("制作木炭", "成功", result[:100])
    
    # 检查木炭数量
    if game.get_item_count("charcoal") >= 3:
        test_passed("木炭制作获得正确数量 (3个)")
    else:
        test_failed("木炭数量", ">=3", game.get_item_count("charcoal"))
    
    # 测试7: 冶炼铁锭
    print("\n【测试7: 冶炼铁锭】")
    ensure_game_running()
    game.add_item("iron_ore", 5)
    result = handler.handle("craft", ["make", "iron_ingot"])
    if "铁锭" in result or "iron_ingot" in result:
        test_passed("冶炼铁锭成功")
    else:
        test_failed("冶炼铁锭", "成功", result[:100])
    
    # 测试8: 烹饪加成
    print("\n【测试8: 烹饪加成】")
    ensure_game_running()
    game.add_item("raw_meat", 5)
    result = handler.handle("camp", ["cook", "raw_meat"])
    if "食物" in result and "烹饪" in result:
        test_passed("烹饪成功")
        if "效率加成" in result or "+" in result:
            test_passed("烹饪显示加成")
        else:
            print(f"  ! 烹饪输出:\n{result[:200]}")
            test_failed("烹饪加成", "显示加成", "无加成显示")
    else:
        test_failed("烹饪", "成功", result[:100])
    
    # 测试9: 净化水加成
    print("\n【测试9: 净化水加成】")
    ensure_game_running()
    game.add_item("dirty_water", 5)
    result = handler.handle("camp", ["purify"])
    if "净水" in result:
        test_passed("净化水成功")
        if "净水器x" in result:
            test_passed("净化水显示倍数")
        else:
            # 检查净水器等级
            wf_level = game.get_camp_upgrade_level("water_filter")
            print(f"  ! 净水器等级: {wf_level}, 净化水输出:\n{result[:200]}")
            test_failed("净化水倍数", "显示倍数", "无倍数显示")
    else:
        test_failed("净化水", "成功", result[:100])
    
    # 测试10: 夜间防守 - 通过推进回合触发夜间防守
    print("\n【测试10: 夜间防守】")
    ensure_game_running()
    random.seed(123)
    game.health = 500
    game.camp["torches"] = 2  # 加火把
    old_health = game.health
    old_day = game.day
    msg = game.advance_turn(1)  # 推进回合触发夜间
    msg_str = str(msg) if msg else ""
    
    # 检查战斗日志（即使消息为空，战斗日志也应该有记录）
    if len(game.battle_log) > 0:
        test_passed(f"战斗日志已记录 {len(game.battle_log)} 条")
        has_raw_damage = any("原始伤害" in log for log in game.battle_log)
        has_camp_reduction = any("营地减伤" in log for log in game.battle_log)
        has_torch_reduction = any("火把减伤" in log for log in game.battle_log)
        has_peaceful = any("平安无事" in log for log in game.battle_log)
        has_night_battle = any("夜间战斗" in log for log in game.battle_log)
        
        if has_night_battle and ((has_raw_damage and has_camp_reduction and has_torch_reduction) or has_peaceful):
            test_passed("自然夜间战斗日志口径与 camp defend 一致")
        else:
            print(f"  ! 战斗日志示例: {game.battle_log[:10]}")
            test_failed("战斗日志口径", "包含夜间战斗和减伤字段或平安无事", 
                f"夜间战斗:{has_night_battle}, 原始伤害:{has_raw_damage}, 营地减伤:{has_camp_reduction}, 火把减伤:{has_torch_reduction}, 平安:{has_peaceful}")
    else:
        print(f"  ! 推进消息: {msg_str}, 天数变化: {old_day} -> {game.day}")
        test_failed("战斗日志", "有记录", "无记录")
    
    # 测试11: 智能目标提示
    print("\n【测试11: 智能目标提示】")
    ensure_game_running()
    result = handler.handle("event", ["quest"])
    if "建议" in result or "目标" in result or "任务" in result:
        test_passed("event quest 显示提示")
    else:
        print(f"  ! quest 输出:\n{result[:200]}")
        test_failed("event quest", "显示提示", "无提示")
    
    result = handler.handle("camp", ["plan"])
    if "建议" in result or "目标" in result or "任务" in result:
        test_passed("camp plan 显示提示")
    else:
        print(f"  ! plan 输出:\n{result[:200]}")
        test_failed("camp plan", "显示提示", "无提示")
    
    # 测试12: 雨水收集 - 确保净水器2级并在雨天
    print("\n【测试12: 雨水收集】")
    ensure_game_running()
    # 确保净水器等级足够
    wf_level = game.get_camp_upgrade_level("water_filter")
    if wf_level >= 2:
        test_passed(f"净水器等级足够 (Lv.{wf_level})")
    else:
        test_failed("净水器等级", ">=2", wf_level)
    
    game.weather = "rain"
    game.day = 10  # 设置为白天，这样推进回合会到夜晚
    old_water = game.get_item_count("water")
    old_day = game.day
    msg = game.advance_turn(1)  # 从白天推进到夜晚，会触发夜间阶段
    msg_str = str(msg) if msg else ""
    new_water = game.get_item_count("water")
    if new_water > old_water:
        test_passed(f"雨水收集成功: {old_water} -> {new_water}")
    else:
        # 检查是否有雨水收集的消息
        has_rain_collection = "雨水收集" in msg_str
        print(f"  ! 收集消息: {msg_str}, 净水器等级: {wf_level}, 是否雨天: {game.weather == 'rain'}")
        print(f"  ! 天数变化: {old_day} -> {game.day}, 水变化: {old_water} -> {new_water}")
        test_failed("雨水收集", f"水增加 (当前{old_water})", f"水不变 ({new_water})")
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed[0]:
        print("所有手动测试通过！✓")
    else:
        print("部分测试失败！✗")
    print("=" * 60)
    
    return all_passed[0]

if __name__ == "__main__":
    test_all_features()
