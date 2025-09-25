# main.py
"""
百家乐发牌系统主程序
"""

import sys
import time
import logging
import argparse
from datetime import datetime

from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE, DEFAULT_COM_PORT, DEFAULT_BAUD_RATE
from serial_manager import SerialManager
from database_manager import DatabaseManager
from baccarat_game import BaccaratGame
from card_parser import CardParser

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
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
        print("系统初始化完成，等待发牌...")
        print("="*50)
        
        self.is_running = True
        return True
    
    def run_game(self):
        """运行一局游戏"""
        try:
            print("\n" + "🎮"*25)
            print(f"开始新的一局 - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("🎮"*25)
            
            # 重置游戏
            self.game.reset_game()
            
            # 第一轮发牌：闲1 → 庄1 → 闲2 → 庄2
            print("\n📤 开始发牌...")
            print("-"*30)
            
            # 闲家第一张
            print("请扫描闲家第1张牌...")
            card = self.wait_for_card()
            if not card:
                return False
            self.game.add_player_card(card)
            self.game.display_current_state()
            
            # 庄家第一张
            print("\n请扫描庄家第1张牌...")
            card = self.wait_for_card()
            if not card:
                return False
            self.game.add_banker_card(card)
            self.game.display_current_state()
            
            # 闲家第二张
            print("\n请扫描闲家第2张牌...")
            card = self.wait_for_card()
            if not card:
                return False
            self.game.add_player_card(card)
            self.game.display_current_state()
            
            # 庄家第二张
            print("\n请扫描庄家第2张牌...")
            card = self.wait_for_card()
            if not card:
                return False
            self.game.add_banker_card(card)
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
                    card = self.wait_for_card()
                    if not card:
                        return False
                    self.game.add_player_card(card)
                    player_third_card = card
                    self.game.display_current_state()
                
                # 庄家补牌判断
                if self.game.banker_need_third_card(player_third_card):
                    print("\n请扫描庄家补牌...")
                    card = self.wait_for_card()
                    if not card:
                        return False
                    self.game.add_banker_card(card)
                    self.game.display_current_state()
            
            # 显示最终结果
            self.game.display_final_result()
            
            # 保存到数据库
            self.save_result()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  游戏被用户中断")
            return False
        except Exception as e:
            logger.error(f"游戏运行出错: {e}")
            print(f"\n❌ 游戏出错: {e}")
            return False
    
    def wait_for_card(self, timeout=60):
        """
        等待扫描卡片
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            str: 卡片代码
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.serial_manager.is_running():
                print("\n❌ 串口连接已断开，尝试重连...")
                if not self.serial_manager.start_reading():
                    return None
            
            # 尝试读取卡片
            card = self.serial_manager.read_card(timeout=1)
            if card:
                # 验证卡片代码是否有效
                if self.parser.parse_card(card):
                    return card
                else:
                    print(f"⚠️  无效的卡片代码: {card}")
            
            # 显示等待状态
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"\r等待扫描... ({remaining}秒)", end='', flush=True)
        
        print(f"\n❌ 等待扫描超时 ({timeout}秒)")
        return None
    
    def save_result(self):
        """保存游戏结果到数据库"""
        print("\n💾 保存结果到数据库...")
        
        result_data = self.game.get_game_result()
        
        # 先检查是否已有数据
        if self.db_manager.check_table_exists(self.table_id):
            print(f"⚠️  桌号 {self.table_id} 已有数据，跳过保存")
            logger.info(f"桌号 {self.table_id} 已有数据，未保存新结果")
        else:
            if self.db_manager.insert_result(result_data, self.table_id):
                print("✅ 结果已保存到数据库")
                print(f"   数据: {result_data}")
            else:
                print("❌ 保存到数据库失败")
    
    def run(self):
        """运行主循环"""
        if not self.initialize():
            print("\n系统初始化失败，程序退出")
            return
        
        try:
            while self.is_running:
                print("\n" + "🎰"*25)
                print("准备开始新游戏")
                print("按 Ctrl+C 退出程序")
                print("🎰"*25)
                
                # 清空串口缓存
                self.serial_manager.clear_queue()
                
                # 运行一局游戏
                if not self.run_game():
                    print("\n游戏异常结束")
                
                # 询问是否继续
                print("\n" + "-"*50)
                print("是否继续下一局？")
                print("1. 按回车继续")
                print("2. 输入 'q' 退出")
                choice = input("请选择: ").strip().lower()
                
                if choice == 'q':
                    break
                    
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
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
    parser = argparse.ArgumentParser(description='百家乐发牌系统')
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
    print("百家乐发牌系统 v1.0")
    print("🎲"*25)
    print(f"\n配置信息:")
    print(f"  串口: {args.com_port}")
    print(f"  波特率: {args.baud_rate}")
    print(f"  桌号: {args.table_id}")
    
    # 创建并运行系统
    system = BaccaratSystem(args.com_port, args.baud_rate, args.table_id)
    system.run()


if __name__ == '__main__':
    main()