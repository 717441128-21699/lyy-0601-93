"""荒岛求生 - 命令行生存游戏"""

import sys
import os
from game_state import GameState
from commands import CommandHandler

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                     荒 岛 求 生                              ║
║                   Island Survival                           ║
╠══════════════════════════════════════════════════════════════╣
║  你在一场海难后醒来，发现自己身处一座荒岛上。                ║
║  你必须采集资源、建造营地、寻找食物和水源，                  ║
║  与恶劣的天气和凶猛的野兽搏斗，生存30天等待救援。            ║
║                                                              ║
║  或者...找到逃离这座岛屿的方法！                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    print_banner()
    
    game = GameState()
    handler = CommandHandler(game)
    
    print("输入 help 查看命令帮助，输入 start new <名字> 开始游戏。\n")
    
    while True:
        try:
            if game.player_name and not game.game_over:
                prompt = f"[{game.day}天 {game.time_of_day} 回合{game.turn}] "
            else:
                prompt = "> "
            
            line = input(prompt).strip()
            
            if not line:
                continue
            
            if line.lower() in ["exit", "quit", "q"]:
                print("感谢游玩荒岛求生！再见。")
                break
            
            parts = line.split()
            command = parts[0].lower()
            args = parts[1:]
            
            try:
                result = handler.handle(command, args)
                if result:
                    print(f"\n{result}\n")
            except Exception as e:
                print(f"\n命令执行出错：{e}\n")
                import traceback
                traceback.print_exc()
            
        except KeyboardInterrupt:
            print("\n\n游戏已中断。输入 exit 退出，或继续游戏。")
        except EOFError:
            print("\n感谢游玩荒岛求生！再见。")
            break

if __name__ == "__main__":
    main()
