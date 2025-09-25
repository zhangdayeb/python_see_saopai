# card_parser.py
"""
卡片解析器
负责解析扫描数据并转换为牌值
"""

import logging
from config import CARD_MAPPING

logger = logging.getLogger(__name__)


class CardParser:
    """卡片解析器类"""
    
    def __init__(self):
        self.card_mapping = CARD_MAPPING
        
    def parse_card(self, card_code):
        """
        解析卡片代码
        
        Args:
            card_code: 卡片代码，如 'D12' 表示方块Q
            
        Returns:
            dict: 包含花色、点数、显示值等信息
        """
        if not card_code:
            return None
            
        card_code = card_code.strip().upper()
        
        if card_code in self.card_mapping:
            return self.card_mapping[card_code]
        else:
            logger.warning(f"未识别的卡片代码: {card_code}")
            return None
    
    def get_card_value(self, card_code):
        """
        获取卡片的百家乐点数值
        
        Args:
            card_code: 卡片代码
            
        Returns:
            int: 点数值 (0-9)
        """
        card_info = self.parse_card(card_code)
        return card_info['value'] if card_info else 0
    
    def get_card_display(self, card_code):
        """
        获取卡片的显示字符串
        
        Args:
            card_code: 卡片代码
            
        Returns:
            str: 显示字符串，如 '♦Q'
        """
        card_info = self.parse_card(card_code)
        return card_info['display'] if card_info else '??'
    
    def calculate_points(self, cards):
        """
        计算一手牌的总点数
        
        Args:
            cards: 卡片代码列表
            
        Returns:
            int: 总点数 (0-9)
        """
        total = 0
        for card in cards:
            if card:  # 忽略空牌
                total += self.get_card_value(card)
        
        # 百家乐规则：取个位数
        return total % 10
    
    def format_hand(self, cards):
        """
        格式化一手牌的显示
        
        Args:
            cards: 卡片代码列表
            
        Returns:
            str: 格式化的显示字符串
        """
        display_cards = []
        for card in cards:
            if card:
                display_cards.append(self.get_card_display(card))
        
        points = self.calculate_points(cards)
        cards_str = ' + '.join(display_cards) if display_cards else '无牌'
        
        return f"{cards_str} = {points}点"