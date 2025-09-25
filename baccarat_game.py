# baccarat_game.py
"""
百家乐游戏逻辑
负责游戏流程控制和补牌规则判断
"""

import logging
from card_parser import CardParser

logger = logging.getLogger(__name__)


class BaccaratGame:
    """百家乐游戏类"""
    
    def __init__(self):
        """初始化游戏"""
        self.parser = CardParser()
        self.reset_game()
        
    def reset_game(self):
        """重置游戏状态"""
        self.player_cards = []
        self.banker_cards = []
        self.game_result = None
        
    def add_player_card(self, card_code):
        """添加闲家卡片"""
        self.player_cards.append(card_code)
        logger.info(f"闲家获得: {self.parser.get_card_display(card_code)}")
        
    def add_banker_card(self, card_code):
        """添加庄家卡片"""
        self.banker_cards.append(card_code)
        logger.info(f"庄家获得: {self.parser.get_card_display(card_code)}")
        
    def get_player_points(self):
        """获取闲家点数"""
        return self.parser.calculate_points(self.player_cards)
    
    def get_banker_points(self):
        """获取庄家点数"""
        return self.parser.calculate_points(self.banker_cards)
    
    def check_natural(self):
        """
        检查是否有天牌（8或9点）
        
        Returns:
            bool: True表示有天牌，游戏结束
        """
        player_points = self.get_player_points()
        banker_points = self.get_banker_points()
        
        if player_points >= 8 or banker_points >= 8:
            logger.info(f"天牌! 闲家:{player_points}点, 庄家:{banker_points}点")
            return True
        return False
    
    def player_need_third_card(self):
        """
        判断闲家是否需要补牌
        
        规则:
        - 0-5点: 补牌
        - 6-7点: 停牌
        - 8-9点: 天牌（此方法不会被调用）
        
        Returns:
            bool: True需要补牌，False不需要
        """
        points = self.get_player_points()
        need_card = points <= 5
        
        if need_card:
            logger.info(f"闲家{points}点，需要补牌")
        else:
            logger.info(f"闲家{points}点，停牌")
            
        return need_card
    
    def banker_need_third_card(self, player_third_card=None):
        """
        判断庄家是否需要补牌
        
        庄家补牌规则:
        - 0-2点: 必须补牌
        - 3点: 闲家第三张牌为8时不补，其他补
        - 4点: 闲家第三张牌为0,1,8,9时不补，其他补
        - 5点: 闲家第三张牌为0,1,2,3,8,9时不补，其他补
        - 6点: 闲家第三张牌为6,7时补，其他不补
        - 7点: 停牌
        - 8-9点: 天牌（此方法不会被调用）
        
        Args:
            player_third_card: 闲家第三张牌的代码（如果有）
            
        Returns:
            bool: True需要补牌，False不需要
        """
        banker_points = self.get_banker_points()
        
        # 如果闲家没有补牌
        if player_third_card is None:
            # 闲家停牌时，庄家0-5点补牌，6-7点停牌
            need_card = banker_points <= 5
        else:
            # 获取闲家第三张牌的点数
            player_third_value = self.parser.get_card_value(player_third_card)
            
            if banker_points <= 2:
                need_card = True
            elif banker_points == 3:
                need_card = player_third_value != 8
            elif banker_points == 4:
                need_card = player_third_value not in [0, 1, 8, 9]
            elif banker_points == 5:
                need_card = player_third_value not in [0, 1, 2, 3, 8, 9]
            elif banker_points == 6:
                need_card = player_third_value in [6, 7]
            else:  # 7点
                need_card = False
        
        if need_card:
            logger.info(f"庄家{banker_points}点，需要补牌")
        else:
            logger.info(f"庄家{banker_points}点，停牌")
            
        return need_card
    
    def determine_winner(self):
        """
        判定胜负
        
        Returns:
            str: 'PLAYER'(闲赢), 'BANKER'(庄赢), 'TIE'(和局)
        """
        player_points = self.get_player_points()
        banker_points = self.get_banker_points()
        
        if player_points > banker_points:
            return 'PLAYER'
        elif banker_points > player_points:
            return 'BANKER'
        else:
            return 'TIE'
    
    def get_game_result(self):
        """
        获取游戏结果（格式化为数据库格式）
        
        Returns:
            dict: 游戏结果字典
        """
        # 确保卡片列表至少有3个元素（用空字符串填充）
        player_cards = self.player_cards + [''] * (3 - len(self.player_cards))
        banker_cards = self.banker_cards + [''] * (3 - len(self.banker_cards))
        
        result = {
            'PLAYER1': player_cards[0],
            'PLAYER2': player_cards[1],
            'PLAYER3': player_cards[2],
            'BANKER1': banker_cards[0],
            'BANKER2': banker_cards[1],
            'BANKER3': banker_cards[2]
        }
        
        return result
    
    def display_current_state(self):
        """显示当前游戏状态"""
        print("\n" + "="*50)
        print("当前游戏状态:")
        print("-"*50)
        
        # 显示闲家信息
        player_display = self.parser.format_hand(self.player_cards)
        print(f"闲家: {player_display}")
        
        # 显示庄家信息
        banker_display = self.parser.format_hand(self.banker_cards)
        print(f"庄家: {banker_display}")
        
        # 如果游戏结束，显示结果
        if len(self.player_cards) >= 2 and len(self.banker_cards) >= 2:
            winner = self.determine_winner()
            if winner == 'PLAYER':
                print("\n🎉 闲家赢!")
            elif winner == 'BANKER':
                print("\n🎉 庄家赢!")
            else:
                print("\n🤝 和局!")
        
        print("="*50)
    
    def display_final_result(self):
        """显示最终结果"""
        print("\n" + "╔"*50)
        print("║  最终结果")
        print("╠"*50)
        
        # 显示闲家详细信息
        print("║ 闲家牌:")
        for i, card in enumerate(self.player_cards, 1):
            if card:
                card_display = self.parser.get_card_display(card)
                print(f"║   第{i}张: {card_display} ({card})")
        player_display = self.parser.format_hand(self.player_cards)
        print(f"║ 闲家结果: {player_display}")
        
        print("║")
        
        # 显示庄家详细信息
        print("║ 庄家牌:")
        for i, card in enumerate(self.banker_cards, 1):
            if card:
                card_display = self.parser.get_card_display(card)
                print(f"║   第{i}张: {card_display} ({card})")
        banker_display = self.parser.format_hand(self.banker_cards)
        print(f"║ 庄家结果: {banker_display}")
        
        print("║")
        
        # 显示胜负结果
        winner = self.determine_winner()
        if winner == 'PLAYER':
            print("║ 🎉🎉🎉 闲家胜利! 🎉🎉🎉")
        elif winner == 'BANKER':
            print("║ 🎉🎉🎉 庄家胜利! 🎉🎉🎉")
        else:
            print("║ 🤝🤝🤝 和局! 🤝🤝🤝")
        
        print("╚"*50)