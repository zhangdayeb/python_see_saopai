# main.py
"""
百家乐发牌系统主程序 - 永久循环版本
"""

import sys
import time
import logging
import argparse
from datetime import datetime

from config import (
    LOG_LEVEL, LOG_FORMAT,
    DEFAULT_COM_PORT, DEFAULT_BAUD_RATE,
    GAME_TIMEOUT, CARD_SCAN_TIMEOUT
)
from serial_manager import SerialManager
from database_manager import DatabaseManager
from baccarat_game import BaccaratGame
from card_parser import CardParser

# 配置日志 - 只输出到控制台
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler()  # 只保留控制台输出
    ]
)

logger = logging.getLogger(__name__)


class BaccaratSystem:
    """百家乐系统主类"""
    
    def __init__(self, com_port, baud_rate, table_id):
        """
        初始化系统
        
        Args:
            com_port: 串口号
            baud_rate: 波特率
            table_id: 桌号
        """
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.table_id = table_id
        
        # 初始化各个组件
        self.serial_manager = SerialManager(com_port, baud_rate)
        self.db_manager = DatabaseManager()
        self.game = BaccaratGame()
        self.parser = CardParser()
        
        self.is_running = False
        
        # 游戏状态跟踪
        self.game_start_time = None  # 游戏开始时间
        self.last_scan_time = None   # 最后扫描时间
        self.game_count = 0          # 游戏局数统计
        
    def initialize(self):
        """初始化系统连接"""
        print("\n" + "="*50)
        print("百家乐发牌系统启动中...")
        print("="*50)
        
        # 连接串口
        print(f"\n正在连接串口 {self.com_port} (波特率: {self.baud_rate})...")
        if not self.serial_manager.start_reading():
            print("❌ 串口连接失败!")
            return False
        print("✅ 串口连接成功!")
        
        # 连接数据库
        print("\n正在连接数据库...")
        if not self.db_manager.connect():
            print("❌ 数据库连接失败!")
            return False
        print("✅ 数据库连接成功!")
        
        # 检查是否已有数据
        print(f"\n检查桌号 {self.table_id} 的数据...")
        if self.db_manager.check_table_exists(self.table_id):
            print(f"⚠️  桌号 {self.table_id} 已有数据存在")
        else:
            print(f"✅ 桌号 {self.table_id} 无数据，可以开始新游戏")
        
        print("\n" + "="*50)
        print(f"系统初始化完成")
        print(f"游戏超时设置: {GAME_TIMEOUT}秒")
        print(f"系统将永久运行，按 Ctrl+C 退出")
        print("="*50)
        
        self.is_running = True
        return True
    
    def check_game_timeout(self):
        """
        检查游戏是否超时
        
        Returns:
            bool: True表示超时，False表示未超时
        """
        if self.game_start_time is None:
            return False
        
        elapsed = time.time() - self.game_start_time
        
        # 如果有最后扫描时间，使用最后扫描时间
        if self.last_scan_time:
            elapsed = time.time() - self.last_scan_time
        
        if elapsed > GAME_TIMEOUT:
            logger.warning(f"游戏超时: {elapsed:.1f}秒无操作")
            return True
        
        return False
    
    def handle_game_timeout(self):
        """处理游戏超时"""
        print("\n" + "⚠️"*25)
        print(f"游戏超时！{GAME_TIMEOUT}秒内未扫描到任何牌")
        print("正在重置游戏并清理数据...")
        print("⚠️"*25)
        
        # 清理远程数据库数据
        if self.db_manager.clear_table_data(self.table_id):
            print(f"✅ 已清理桌号 {self.table_id} 的所有数据")
        else:
            print(f"❌ 清理数据失败")
        
        # 重置本地游戏状态
        self.game.reset_game()
        self.game_start_time = None
        self.last_scan_time = None
        
        print("游戏已重置，3秒后自动开始新游戏...")
        time.sleep(3)  # 短暂等待，让操作员看到消息
    
    def run_game(self):
        """运行一局游戏"""
        try:
            self.game_count += 1
            print("\n" + "🎮"*25)
            print(f"第 {self.game_count} 局 - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("🎮"*25)
            
            # 重置游戏
            self.game.reset_game()
            
            # 设置游戏开始时间
            self.game_start_time = time.time()
            self.last_scan_time = None
            
            # 第一轮发牌：闲1 → 庄1 → 闲2 → 庄2
            print("\n📤 开始发牌...")
            print("-"*30)
            
            # 闲家第一张
            print("请扫描闲家第1张牌...")
            card = self.wait_for_card_with_timeout()
            if not card:
                if self.check_game_timeout():
                    self.handle_game_timeout()
                return False
            self.game.add_player_card(card)
            self.db_manager.insert_temp_card(self.table_id, 'xian_1', card)
            self.game.display_current_state()
            
            # 庄家第一张
            print("\n请扫描庄家第1张牌...")
            card = self.wait_for_card_with_timeout()
            if not card:
                if self.check_game_timeout():
                    self.handle_game_timeout()
                return False
            self.game.add_banker_card(card)
            self.db_manager.insert_temp_card(self.table_id, 'zhuang_1', card)
            self.game.display_current_state()
            
            # 闲家第二张
            print("\n请扫描闲家第2张牌...")
            card = self.wait_for_card_with_timeout()
            if not card:
                if self.check_game_timeout():
                    self.handle_game_timeout()
                return False
            self.game.add_player_card(card)
            self.db_manager.insert_temp_card(self.table_id, 'xian_2', card)
            self.game.display_current_state()
            
            # 庄家第二张
            print("\n请扫描庄家第2张牌...")
            card = self.wait_for_card_with_timeout()
            if not card:
                if self.check_game_timeout():
                    self.handle_game_timeout()
                return False
            self.game.add_banker_card(card)
            self.db_manager.insert_temp_card(self.table_id, 'zhuang_2', card)
            self.game.display_current_state()
            
            # 检查天牌
            if self.game.check_natural():
                print("\n🎊 天牌！游戏结束！")
            else:
                # 判断是否需要补牌
                print("\n📊 判断是否需要补牌...")
                print("-"*30)
                
                player_third_card = None
                
                # 闲家补牌判断
                if self.game.player_need_third_card():
                    print("\n请扫描闲家补牌...")
                    card = self.wait_for_card_with_timeout()
                    if not card:
                        if self.check_game_timeout():
                            self.handle_game_timeout()
                        return False
                    self.game.add_player_card(card)
                    player_third_card = card
                    self.db_manager.insert_temp_card(self.table_id, 'xian_3', card)
                    self.game.display_current_state()
                
                # 庄家补牌判断
                if self.game.banker_need_third_card(player_third_card):
                    print("\n请扫描庄家补牌...")
                    card = self.wait_for_card_with_timeout()
                    if not card:
                        if self.check_game_timeout():
                            self.handle_game_timeout()
                        return False
                    self.game.add_banker_card(card)
                    self.db_manager.insert_temp_card(self.table_id, 'zhuang_3', card)
                    self.game.display_current_state()
            
            # 显示最终结果
            self.game.display_final_result()
            
            # 保存到数据库
            self.save_result()
            
            # 重置时间记录
            self.game_start_time = None
            self.last_scan_time = None
            
            # 短暂等待，让操作员看到结果
            print("\n" + "="*50)
            print(f"✅ 第 {self.game_count} 局完成")
            print("5秒后自动开始下一局...")
            print("="*50)
            time.sleep(5)
            
            return True
            
        except KeyboardInterrupt:
            # 向上层传递中断信号
            raise
        except Exception as e:
            logger.error(f"游戏运行出错: {e}")
            print(f"\n❌ 游戏出错: {e}")
            print("5秒后自动重试...")
            time.sleep(5)
            return False
    
    def wait_for_card_with_timeout(self):
        """
        等待扫描卡片（带超时检查）
        
        Returns:
            str: 卡片代码，或None（超时）
        """
        start_time = time.time()
        
        while True:
            # 检查游戏总超时
            if self.check_game_timeout():
                return None
            
            # 检查单张牌扫描超时
            if time.time() - start_time > CARD_SCAN_TIMEOUT:
                print(f"\n⚠️  单张牌扫描超时 ({CARD_SCAN_TIMEOUT}秒)")
                # 继续检查游戏总超时
                if self.check_game_timeout():
                    return None
                # 如果游戏未超时，继续等待
                start_time = time.time()  # 重置单张牌超时计时
                print("继续等待扫描...")
            
            if not self.serial_manager.is_running():
                print("\n❌ 串口连接已断开，尝试重连...")
                if not self.serial_manager.start_reading():
                    print("串口重连失败，5秒后重试...")
                    time.sleep(5)
                    continue
            
            # 尝试读取卡片
            card = self.serial_manager.read_card(timeout=1)
            if card:
                # 验证卡片代码是否有效
                if self.parser.parse_card(card):
                    # 更新最后扫描时间
                    self.last_scan_time = time.time()
                    return card
                else:
                    print(f"⚠️  无效的卡片代码: {card}")
            
            # 显示等待状态
            elapsed = int(time.time() - start_time)
            game_elapsed = int(time.time() - self.game_start_time) if self.game_start_time else 0
            remaining = CARD_SCAN_TIMEOUT - elapsed
            game_remaining = GAME_TIMEOUT - game_elapsed
            
            print(f"\r等待扫描... (单张牌: {remaining}秒 | 游戏总计: {game_remaining}秒)", end='', flush=True)
    
    def save_result(self):
        """保存游戏结果到数据库"""
        print("\n💾 保存结果到数据库...")
        
        result_data = self.game.get_game_result()
        
        # 先检查是否已有数据
        if self.db_manager.check_table_exists(self.table_id):
            print(f"⚠️  桌号 {self.table_id} 已有数据，清理后重新保存...")
            # 清理旧数据
            self.db_manager.clear_table_data(self.table_id)
        
        # 保存新数据
        if self.db_manager.insert_result(result_data, self.table_id):
            print("✅ 结果已保存到数据库")
            print(f"   数据: {result_data}")
        else:
            print("❌ 保存到数据库失败")
    
    def run(self):
        """运行主循环 - 永久运行"""
        if not self.initialize():
            print("\n系统初始化失败，程序退出")
            return
        
        try:
            print("\n" + "🎰"*25)
            print("系统开始永久运行模式")
            print("游戏将自动循环，无需人工确认")
            print("按 Ctrl+C 退出程序")
            print("🎰"*25)
            
            # 永久循环
            while self.is_running:
                try:
                    # 清空串口缓存
                    self.serial_manager.clear_queue()
                    
                    # 运行一局游戏
                    self.run_game()
                    
                except KeyboardInterrupt:
                    # 捕获内部的中断信号并向上传递
                    raise
                except Exception as e:
                    logger.error(f"游戏循环出错: {e}")
                    print(f"\n❌ 游戏循环出错: {e}")
                    print("10秒后自动重试...")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("\n\n" + "⚠️"*25)
            print("程序被用户中断")
            print(f"共进行了 {self.game_count} 局游戏")
            print("⚠️"*25)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("\n正在清理资源...")
        
        if self.serial_manager:
            self.serial_manager.disconnect()
        
        if self.db_manager:
            self.db_manager.disconnect()
        
        print("资源清理完成，程序退出")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='百家乐发牌系统 - 永久循环版')
    parser.add_argument('com_port', 
                       nargs='?',
                       default=DEFAULT_COM_PORT,
                       help=f'串口号 (默认: {DEFAULT_COM_PORT})')
    parser.add_argument('baud_rate', 
                       nargs='?',
                       type=int,
                       default=DEFAULT_BAUD_RATE,
                       help=f'波特率 (默认: {DEFAULT_BAUD_RATE})')
    parser.add_argument('table_id', 
                       nargs='?',
                       default='1',
                       help='桌号 (默认: 1)')
    
    args = parser.parse_args()
    
    # 显示启动信息
    print("\n" + "🎲"*25)
    print("百家乐发牌系统 v1.0 - 永久循环版")
    print("🎲"*25)
    print(f"\n配置信息:")
    print(f"  串口: {args.com_port}")
    print(f"  波特率: {args.baud_rate}")
    print(f"  桌号: {args.table_id}")
    print(f"  游戏超时: {GAME_TIMEOUT}秒")
    print(f"  单牌超时: {CARD_SCAN_TIMEOUT}秒")
    print(f"\n⚠️  系统将永久运行，游戏自动循环")
    print(f"⚠️  无需人工确认，按 Ctrl+C 退出")
    
    # 创建并运行系统
    system = BaccaratSystem(args.com_port, args.baud_rate, args.table_id)
    system.run()


if __name__ == '__main__':
    main()