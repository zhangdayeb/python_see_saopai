# serial_manager.py
"""
串口管理器
负责串口连接、数据读取和自动重连
"""

import serial
import time
import threading
import logging
from queue import Queue, Empty
from config import SERIAL_RECONNECT_INTERVAL, MAX_RECONNECT_ATTEMPTS

logger = logging.getLogger(__name__)


class SerialManager:
    """串口管理器类"""
    
    def __init__(self, port, baudrate, timeout=1):
        """
        初始化串口管理器
        
        Args:
            port: 串口号，如 'COM3'
            baudrate: 波特率，如 9600
            timeout: 超时时间（秒）
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_connected = False
        self.data_queue = Queue()
        self.running = False
        self.read_thread = None
        self.reconnect_count = 0
        
    def connect(self):
        """连接串口"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.is_connected = True
            self.reconnect_count = 0
            logger.info(f"串口连接成功: {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            logger.error(f"串口连接失败: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """断开串口连接"""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                logger.info("串口已断开")
            except Exception as e:
                logger.error(f"断开串口时出错: {e}")
        self.is_connected = False
    
    def start_reading(self):
        """开始读取串口数据"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        self.running = True
        self.read_thread = threading.Thread(target=self._read_loop)
        self.read_thread.daemon = True
        self.read_thread.start()
        logger.info("串口读取线程已启动")
        return True
    
    def _read_loop(self):
        """串口读取循环（在独立线程中运行）"""
        while self.running:
            try:
                if not self.is_connected:
                    self._try_reconnect()
                    continue
                
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    # 读取数据直到遇到换行符
                    data = self.serial_connection.readline()
                    if data:
                        # 解码并去除换行符
                        decoded_data = data.decode('utf-8').strip()
                        if decoded_data:
                            logger.debug(f"接收到数据: {decoded_data}")
                            self.data_queue.put(decoded_data)
                            
            except serial.SerialException as e:
                logger.error(f"串口读取错误: {e}")
                self.is_connected = False
                self._try_reconnect()
            except Exception as e:
                logger.error(f"未知错误: {e}")
                time.sleep(0.1)
            
            time.sleep(0.01)  # 避免CPU占用过高
    
    def _try_reconnect(self):
        """尝试重新连接串口"""
        if self.reconnect_count >= MAX_RECONNECT_ATTEMPTS:
            logger.error(f"重连失败次数超过限制 ({MAX_RECONNECT_ATTEMPTS}次)")
            self.running = False
            return
        
        self.reconnect_count += 1
        logger.info(f"尝试重新连接串口... (第{self.reconnect_count}次)")
        
        time.sleep(SERIAL_RECONNECT_INTERVAL)
        
        if self.connect():
            logger.info("串口重连成功")
        else:
            logger.warning(f"串口重连失败，{SERIAL_RECONNECT_INTERVAL}秒后重试...")
    
    def read_card(self, timeout=30):
        """
        读取一张卡片数据
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            str: 卡片代码，如 'D12'
        """
        try:
            data = self.data_queue.get(timeout=timeout)
            logger.info(f"读取到卡片: {data}")
            return data
        except Empty:
            logger.warning(f"等待卡片超时 ({timeout}秒)")
            return None
    
    def clear_queue(self):
        """清空数据队列"""
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except Empty:
                break
        logger.debug("数据队列已清空")
    
    def is_running(self):
        """检查串口是否正在运行"""
        return self.running and self.is_connected
    
    def get_queue_size(self):
        """获取队列中待处理的数据数量"""
        return self.data_queue.qsize()