# database_manager.py
"""
数据库管理器
负责MySQL数据库连接、数据操作和自动重连
"""

import pymysql
import json
import time
import logging
from config import DB_CONFIG, DB_RECONNECT_INTERVAL, MAX_RECONNECT_ATTEMPTS

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, custom_config=None):
        """
        初始化数据库管理器
        
        Args:
            custom_config: 自定义数据库配置（可选）
        """
        self.config = custom_config if custom_config else DB_CONFIG.copy()
        self.connection = None
        self.cursor = None
        self.is_connected = False
        self.reconnect_count = 0
        
    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(**self.config)
            self.cursor = self.connection.cursor()
            self.is_connected = True
            self.reconnect_count = 0
            logger.info(f"数据库连接成功: {self.config['host']}:{self.config['port']}")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.is_connected = False
            logger.info("数据库连接已断开")
        except Exception as e:
            logger.error(f"断开数据库连接时出错: {e}")
    
    def ensure_connection(self):
        """确保数据库连接有效，必要时重连"""
        if not self.is_connected:
            return self._try_reconnect()
        
        # 测试连接是否有效
        try:
            self.connection.ping(reconnect=False)
            return True
        except:
            logger.warning("数据库连接已失效，尝试重连...")
            self.is_connected = False
            return self._try_reconnect()
    
    def _try_reconnect(self):
        """尝试重新连接数据库"""
        while self.reconnect_count < MAX_RECONNECT_ATTEMPTS:
            self.reconnect_count += 1
            logger.info(f"尝试重新连接数据库... (第{self.reconnect_count}次)")
            
            if self.connect():
                logger.info("数据库重连成功")
                return True
            
            logger.warning(f"数据库重连失败，{DB_RECONNECT_INTERVAL}秒后重试...")
            time.sleep(DB_RECONNECT_INTERVAL)
        
        logger.error(f"数据库重连失败次数超过限制 ({MAX_RECONNECT_ATTEMPTS}次)")
        return False
    
    def check_table_exists(self, table_id):
        """
        检查指定table_id是否已有数据
        
        Args:
            table_id: 桌号
            
        Returns:
            bool: True表示存在数据，False表示不存在
        """
        if not self.ensure_connection():
            return False
        
        try:
            query = "SELECT COUNT(*) FROM tu_bjl_result WHERE tableId = %s"
            self.cursor.execute(query, (str(table_id),))
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f"检查数据时出错: {e}")
            return False
    
    def insert_result(self, result_data, table_id):
        """
        插入游戏结果
        
        Args:
            result_data: 游戏结果字典
            table_id: 桌号
            
        Returns:
            bool: 是否成功
        """
        if not self.ensure_connection():
            logger.error("数据库连接失败，无法插入数据")
            return False
        
        try:
            # 将结果转换为JSON字符串
            result_json = json.dumps(result_data, ensure_ascii=False)
            
            # 插入数据
            query = "INSERT INTO tu_bjl_result (result, tableId) VALUES (%s, %s)"
            self.cursor.execute(query, (result_json, str(table_id)))
            
            # 提交事务
            self.connection.commit()
            
            logger.info(f"数据插入成功 - Table ID: {table_id}")
            logger.info(f"结果: {result_json}")
            return True
            
        except Exception as e:
            logger.error(f"插入数据时出错: {e}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
    
    def get_latest_result(self, table_id=None):
        """
        获取最新的游戏结果
        
        Args:
            table_id: 桌号（可选）
            
        Returns:
            dict: 结果数据
        """
        if not self.ensure_connection():
            return None
        
        try:
            if table_id:
                query = "SELECT id, result, tableId FROM tu_bjl_result WHERE tableId = %s ORDER BY id DESC LIMIT 1"
                self.cursor.execute(query, (str(table_id),))
            else:
                query = "SELECT id, result, tableId FROM tu_bjl_result ORDER BY id DESC LIMIT 1"
                self.cursor.execute(query)
            
            result = self.cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'result': json.loads(result[1]),
                    'table_id': result[2]
                }
            return None
            
        except Exception as e:
            logger.error(f"获取数据时出错: {e}")
            return None
    
    def delete_result(self, result_id):
        """
        删除指定ID的结果（用于测试）
        
        Args:
            result_id: 记录ID
            
        Returns:
            bool: 是否成功
        """
        if not self.ensure_connection():
            return False
        
        try:
            query = "DELETE FROM tu_bjl_result WHERE id = %s"
            self.cursor.execute(query, (result_id,))
            self.connection.commit()
            logger.info(f"已删除记录 ID: {result_id}")
            return True
        except Exception as e:
            logger.error(f"删除数据时出错: {e}")
            try:
                self.connection.rollback()
            except:
                pass
            return False