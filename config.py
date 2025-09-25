# config.py
"""
百家乐系统配置文件
"""

# 数据库配置
DB_CONFIG = {
    'host': '43.202.109.59',  # 请修改为实际的远程数据库地址
    'port': 3306,
    'user': 'poker_see',       # 请修改为实际的用户名
    'password': 'CbPYRGWJ5S7cXBNj',       # 请修改为实际的密码
    'database': 'poker_see',
    'charset': 'utf8mb4',
    'connect_timeout': 10,
    'autocommit': True
}

# 串口配置默认值
DEFAULT_COM_PORT = 'COM5'
DEFAULT_BAUD_RATE = 9600

# 重连配置
SERIAL_RECONNECT_INTERVAL = 2  # 串口重连间隔(秒)
DB_RECONNECT_INTERVAL = 5      # 数据库重连间隔(秒)
MAX_RECONNECT_ATTEMPTS = 10    # 最大重连次数

# ========== 新增：游戏超时配置 ==========
GAME_TIMEOUT = 180  # 游戏超时时间(秒)，默认180秒
CARD_SCAN_TIMEOUT = 60  # 单张牌扫描超时(秒)

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# LOG_FILE = 'baccarat_system.log'  # 注释掉，不生成日志文件

# 牌值映射
CARD_MAPPING = {
    # 黑桃 Spades (A)
    'A01': {'suit': '黑桃', 'rank': 'A', 'value': 1, 'display': '♠A'},
    'A02': {'suit': '黑桃', 'rank': '2', 'value': 2, 'display': '♠2'},
    'A03': {'suit': '黑桃', 'rank': '3', 'value': 3, 'display': '♠3'},
    'A04': {'suit': '黑桃', 'rank': '4', 'value': 4, 'display': '♠4'},
    'A05': {'suit': '黑桃', 'rank': '5', 'value': 5, 'display': '♠5'},
    'A06': {'suit': '黑桃', 'rank': '6', 'value': 6, 'display': '♠6'},
    'A07': {'suit': '黑桃', 'rank': '7', 'value': 7, 'display': '♠7'},
    'A08': {'suit': '黑桃', 'rank': '8', 'value': 8, 'display': '♠8'},
    'A09': {'suit': '黑桃', 'rank': '9', 'value': 9, 'display': '♠9'},
    'A10': {'suit': '黑桃', 'rank': '10', 'value': 0, 'display': '♠10'},
    'A11': {'suit': '黑桃', 'rank': 'J', 'value': 0, 'display': '♠J'},
    'A12': {'suit': '黑桃', 'rank': 'Q', 'value': 0, 'display': '♠Q'},
    'A13': {'suit': '黑桃', 'rank': 'K', 'value': 0, 'display': '♠K'},
    
    # 红心 Hearts (H)
    'H01': {'suit': '红心', 'rank': 'A', 'value': 1, 'display': '♥A'},
    'H02': {'suit': '红心', 'rank': '2', 'value': 2, 'display': '♥2'},
    'H03': {'suit': '红心', 'rank': '3', 'value': 3, 'display': '♥3'},
    'H04': {'suit': '红心', 'rank': '4', 'value': 4, 'display': '♥4'},
    'H05': {'suit': '红心', 'rank': '5', 'value': 5, 'display': '♥5'},
    'H06': {'suit': '红心', 'rank': '6', 'value': 6, 'display': '♥6'},
    'H07': {'suit': '红心', 'rank': '7', 'value': 7, 'display': '♥7'},
    'H08': {'suit': '红心', 'rank': '8', 'value': 8, 'display': '♥8'},
    'H09': {'suit': '红心', 'rank': '9', 'value': 9, 'display': '♥9'},
    'H10': {'suit': '红心', 'rank': '10', 'value': 0, 'display': '♥10'},
    'H11': {'suit': '红心', 'rank': 'J', 'value': 0, 'display': '♥J'},
    'H12': {'suit': '红心', 'rank': 'Q', 'value': 0, 'display': '♥Q'},
    'H13': {'suit': '红心', 'rank': 'K', 'value': 0, 'display': '♥K'},
    
    # 梅花 Clubs (C)
    'C01': {'suit': '梅花', 'rank': 'A', 'value': 1, 'display': '♣A'},
    'C02': {'suit': '梅花', 'rank': '2', 'value': 2, 'display': '♣2'},
    'C03': {'suit': '梅花', 'rank': '3', 'value': 3, 'display': '♣3'},
    'C04': {'suit': '梅花', 'rank': '4', 'value': 4, 'display': '♣4'},
    'C05': {'suit': '梅花', 'rank': '5', 'value': 5, 'display': '♣5'},
    'C06': {'suit': '梅花', 'rank': '6', 'value': 6, 'display': '♣6'},
    'C07': {'suit': '梅花', 'rank': '7', 'value': 7, 'display': '♣7'},
    'C08': {'suit': '梅花', 'rank': '8', 'value': 8, 'display': '♣8'},
    'C09': {'suit': '梅花', 'rank': '9', 'value': 9, 'display': '♣9'},
    'C10': {'suit': '梅花', 'rank': '10', 'value': 0, 'display': '♣10'},
    'C11': {'suit': '梅花', 'rank': 'J', 'value': 0, 'display': '♣J'},
    'C12': {'suit': '梅花', 'rank': 'Q', 'value': 0, 'display': '♣Q'},
    'C13': {'suit': '梅花', 'rank': 'K', 'value': 0, 'display': '♣K'},
    
    # 方块 Diamonds (D)
    'D01': {'suit': '方块', 'rank': 'A', 'value': 1, 'display': '♦A'},
    'D02': {'suit': '方块', 'rank': '2', 'value': 2, 'display': '♦2'},
    'D03': {'suit': '方块', 'rank': '3', 'value': 3, 'display': '♦3'},
    'D04': {'suit': '方块', 'rank': '4', 'value': 4, 'display': '♦4'},
    'D05': {'suit': '方块', 'rank': '5', 'value': 5, 'display': '♦5'},
    'D06': {'suit': '方块', 'rank': '6', 'value': 6, 'display': '♦6'},
    'D07': {'suit': '方块', 'rank': '7', 'value': 7, 'display': '♦7'},
    'D08': {'suit': '方块', 'rank': '8', 'value': 8, 'display': '♦8'},
    'D09': {'suit': '方块', 'rank': '9', 'value': 9, 'display': '♦9'},
    'D10': {'suit': '方块', 'rank': '10', 'value': 0, 'display': '♦10'},
    'D11': {'suit': '方块', 'rank': 'J', 'value': 0, 'display': '♦J'},
    'D12': {'suit': '方块', 'rank': 'Q', 'value': 0, 'display': '♦Q'},
    'D13': {'suit': '方块', 'rank': 'K', 'value': 0, 'display': '♦K'},
}

# ========== 新增：牌值格式转换映射 ==========
def convert_card_to_db_format(card_code):
    """
    将卡片代码转换为数据库格式
    例如: 'D12' -> '12|f'
    
    Args:
        card_code: 原始卡片代码 (如 'D12', 'A01')
    
    Returns:
        str: 数据库格式 (如 '12|f', '1|h')
    """
    if not card_code:
        return '0|0'
    
    card_code = card_code.strip().upper()
    
    # 花色映射
    suit_map = {
        'A': 'h',  # 黑桃 -> h
        'H': 'r',  # 红心 -> r
        'C': 'm',  # 梅花 -> m
        'D': 'f'   # 方块 -> f
    }
    
    if len(card_code) >= 3 and card_code[0] in suit_map:
        suit = suit_map[card_code[0]]
        # 提取数字部分并转换为整数
        try:
            rank = int(card_code[1:])
            return f"{rank}|{suit}"
        except ValueError:
            return '0|0'
    
    return '0|0'