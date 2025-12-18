"""
統一ログ管理システム
- 機密情報の自動マスキング処理
- トランザクションID自動付与
- パフォーマンス計測機能
- 環境に応じたログレベル制御
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


# 環境変数からログレベルを取得(dev: debug / prod: info)
log_level_str = os.getenv('LOG_LEVEL', 'DEBUG' if os.getenv('NODE_ENV') != 'production' else 'INFO')
log_level = getattr(logging, log_level_str.upper(), logging.INFO)


def mask_sensitive_data(obj: Any) -> Any:
    """機密情報の自動マスキング処理"""
    if isinstance(obj, dict):
        masked = {}
        sensitive_keys = ['password', 'token', 'secret', 'apikey', 'authorization', 'api_key']
        
        for key, value in obj.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                masked[key] = '***MASKED***'
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    
    elif isinstance(obj, list):
        return [mask_sensitive_data(item) for item in obj]
    
    elif isinstance(obj, str) and len(obj) > 20:
        # 長い文字列で機密情報の可能性がある場合
        lower_obj = obj.lower()
        if any(word in lower_obj for word in ['token', 'secret', 'password', 'key']):
            return '***MASKED***'
    
    return obj


class TransactionContext:
    """トランザクション追跡用のコンテキスト"""
    _current: Optional[str] = None
    
    @classmethod
    def generate_id(cls) -> str:
        """新しいトランザクションIDを生成"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(uuid.uuid4()).split('-')[0]
        return f"txn_{timestamp}_{random_part}"
    
    @classmethod
    def set_current(cls, txn_id: str):
        """現在のトランザクションIDを設定"""
        cls._current = txn_id
    
    @classmethod
    def get_current(cls) -> Optional[str]:
        """現在のトランザクションIDを取得"""
        return cls._current
    
    @classmethod
    def clear(cls):
        """トランザクションIDをクリア"""
        cls._current = None


class StockHarvestLogFormatter(logging.Formatter):
    """Stock Harvest AI専用のログフォーマッター"""
    
    def format(self, record):
        # 基本情報の設定
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': 'stock-harvest-backend'
        }
        
        # トランザクションIDの追加
        txn_id = TransactionContext.get_current()
        if txn_id:
            log_entry['transaction_id'] = txn_id
        
        # 追加メタデータの処理
        if hasattr(record, 'extra_data'):
            log_entry['data'] = mask_sensitive_data(record.extra_data)
        
        # エラー情報の追加
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # パフォーマンス情報の追加
        if hasattr(record, 'duration_ms'):
            log_entry['performance'] = {
                'duration_ms': record.duration_ms,
                'operation': getattr(record, 'operation', 'unknown')
            }
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(name: str) -> logging.Logger:
    """ロガーのセットアップ"""
    logger = logging.getLogger(name)
    
    # 既にハンドラーが設定されている場合はそのまま返す
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(StockHarvestLogFormatter())
    
    logger.addHandler(console_handler)
    logger.propagate = False
    
    return logger


class PerformanceTracker:
    """パフォーマンス計測機能"""
    
    def __init__(self, operation: str, logger_instance: logging.Logger):
        self.operation = operation
        self.logger = logger_instance
        self.start_time = time.time()
        
        # 開始ログ
        self.logger.debug(f"Performance tracking started: {operation}")
    
    def end(self, additional_info: Optional[Dict[str, Any]] = None) -> float:
        """パフォーマンス計測終了"""
        duration = time.time() - self.start_time
        duration_ms = round(duration * 1000, 2)
        
        # パフォーマンスログの出力
        log_record = self.logger.makeRecord(
            name=self.logger.name,
            level=logging.INFO,
            fn="",
            lno=0,
            msg=f"Performance: {self.operation}",
            args=(),
            exc_info=None
        )
        log_record.duration_ms = duration_ms
        log_record.operation = self.operation
        
        if additional_info:
            log_record.extra_data = additional_info
        
        self.logger.handle(log_record)
        
        return duration_ms
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()


# 共通ロガーインスタンスの作成
logger = setup_logger('stock_harvest')


def log_with_data(level: str, message: str, data: Optional[Dict[str, Any]] = None, logger_instance: Optional[logging.Logger] = None):
    """データ付きログ出力のヘルパー関数"""
    if logger_instance is None:
        logger_instance = logger
    
    log_level = getattr(logging, level.upper())
    
    if data:
        log_record = logger_instance.makeRecord(
            name=logger_instance.name,
            level=log_level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        log_record.extra_data = data
        logger_instance.handle(log_record)
    else:
        logger_instance.log(log_level, message)


# トランザクション管理のコンテキストマネージャー
class transaction_scope:
    """トランザクションスコープのコンテキストマネージャー"""
    
    def __init__(self, operation_name: str = ""):
        self.operation_name = operation_name
        self.txn_id = None
        self.old_txn_id = None
    
    def __enter__(self):
        self.old_txn_id = TransactionContext.get_current()
        self.txn_id = TransactionContext.generate_id()
        TransactionContext.set_current(self.txn_id)
        
        if self.operation_name:
            logger.info(f"Transaction started: {self.operation_name}")
        
        return self.txn_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Transaction failed: {self.operation_name}", extra={'error': str(exc_val)})
        else:
            if self.operation_name:
                logger.info(f"Transaction completed: {self.operation_name}")
        
        TransactionContext.set_current(self.old_txn_id)


# 便利な関数をエクスポート
def debug(message: str, data: Optional[Dict[str, Any]] = None):
    log_with_data('debug', message, data)

def info(message: str, data: Optional[Dict[str, Any]] = None):
    log_with_data('info', message, data)

def warning(message: str, data: Optional[Dict[str, Any]] = None):
    log_with_data('warning', message, data)

def error(message: str, data: Optional[Dict[str, Any]] = None):
    log_with_data('error', message, data)

def critical(message: str, data: Optional[Dict[str, Any]] = None):
    log_with_data('critical', message, data)


# PerformanceTrackerの便利なファクトリー関数
def track_performance(operation: str) -> PerformanceTracker:
    """パフォーマンストラッカーの作成"""
    return PerformanceTracker(operation, logger)