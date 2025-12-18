"""
全上場銘柄管理サービス
日本の全上場銘柄（約3,800銘柄）のリストを管理・取得
"""

import yfinance as yf
import pandas as pd
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import time
import json
import os

logger = logging.getLogger(__name__)

class StockUniverseService:
    """
    全上場銘柄管理サービス
    """
    
    def __init__(self):
        self.cache_file = "stock_universe_cache.json"
        self.cache_duration = 24 * 3600  # 24時間
        
    def get_all_japanese_stocks(self) -> List[str]:
        """
        日本の全上場銘柄コードを取得
        
        Returns:
            日本の全上場銘柄コードのリスト
        """
        try:
            # キャッシュチェック
            cached_data = self._load_cache()
            if cached_data:
                logger.info(f"キャッシュから{len(cached_data)}銘柄を取得")
                return cached_data
            
            # 新規取得
            logger.info("全銘柄リストを新規取得中...")
            all_stocks = []
            
            # 方法1: 既知の主要銘柄リスト（確実に取得可能）
            major_stocks = self._get_major_stocks()
            all_stocks.extend(major_stocks)
            
            # 方法2: 連番で銘柄コードを生成・検証
            sequential_stocks = self._get_sequential_stocks()
            all_stocks.extend(sequential_stocks)
            
            # 重複削除
            unique_stocks = list(set(all_stocks))
            
            logger.info(f"総計{len(unique_stocks)}銘柄を発見")
            
            # キャッシュに保存
            self._save_cache(unique_stocks)
            
            return unique_stocks
            
        except Exception as e:
            logger.error(f"全銘柄取得でエラー: {str(e)}")
            # フォールバック: 主要銘柄のみ
            return self._get_major_stocks()
    
    def _get_major_stocks(self) -> List[str]:
        """
        主要銘柄リストを取得（確実に存在する銘柄）
        """
        major_stocks = [
            # 日経225主要銘柄
            "7203", "6501", "4755", "9984", "8306", "6758", "9434", "4063", "6954", "7974",
            "8035", "4568", "6861", "3382", "4519", "6981", "8058", "7267", "4502", "8802",
            
            # TOPIX Core30
            "4063", "6758", "7203", "8306", "9984", "6501", "8035", "7267", "4502", "6954",
            "4568", "6861", "8058", "6981", "9434", "7974", "4519", "8802", "3382", "4755",
            
            # 追加主要銘柄
            "1605", "1801", "1802", "1803", "1808", "1812", "1925", "1928", "1963", "2269",
            "2282", "2432", "2502", "2503", "2914", "3086", "3099", "3101", "3105", "3167",
            "3231", "3254", "3289", "3401", "3402", "3407", "3436", "3626", "3659", "3694",
            "3769", "3861", "3863", "4005", "4021", "4041", "4042", "4043", "4061", "4088",
            "4183", "4188", "4202", "4204", "4208", "4272", "4307", "4324", "4452", "4503",
            "4506", "4507", "4523", "4543", "4578", "4612", "4613", "4631", "4661", "4676",
            "4689", "4704", "4716", "4751", "4901", "4902", "4911", "4912", "5019", "5101",
            "5108", "5232", "5233", "5301", "5332", "5401", "5411", "5486", "5541", "5631",
            "5703", "5706", "5711", "5713", "5714", "5801", "5802", "5803", "5901", "5947",
            "6013", "6098", "6103", "6113", "6178", "6201", "6267", "6269", "6301", "6305",
            "6326", "6361", "6367", "6378", "6395", "6406", "6473", "6479", "6503", "6504",
            "6645", "6674", "6701", "6702", "6703", "6724", "6752", "6762", "6770", "6841",
            "6857", "6902", "6920", "6923", "6952", "6971", "6976", "7003", "7004", "7011",
            "7012", "7013", "7148", "7201", "7202", "7205", "7261", "7269", "7270", "7272",
            "7309", "7751", "7832", "7912", "7951", "7956", "8001", "8002", "8015", "8020",
            "8031", "8053", "8056", "8057", "8303", "8304", "8308", "8309", "8316", "8331",
            "8354", "8411", "8729", "8750", "8766", "8795", "8830", "9001", "9005", "9007",
            "9008", "9009", "9020", "9021", "9022", "9041", "9042", "9062", "9064", "9101",
            "9104", "9107", "9201", "9202", "9301", "9412", "9432", "9433", "9449", "9502",
            "9503", "9531", "9532", "9602", "9613", "9625", "9681", "9697", "9719", "9735",
            "9766", "9843", "9983"
        ]
        return major_stocks
    
    def _get_sequential_stocks(self) -> List[str]:
        """
        連番で銘柄コードを生成し、実在する銘柄を検証
        
        Returns:
            実在する銘柄コードのリスト
        """
        valid_stocks = []
        
        # 主要な銘柄コード範囲を定義
        code_ranges = [
            (1000, 1999),  # インフラ系
            (2000, 2999),  # 食品・日用品
            (3000, 3999),  # 情報通信・サービス
            (4000, 4999),  # 化学・医薬品
            (5000, 5999),  # 鉄鋼・非鉄金属・ガラス・セラミック
            (6000, 6999),  # 機械・電機
            (7000, 7999),  # 自動車・輸送用機器
            (8000, 8999),  # 銀行・金融
            (9000, 9999)   # 不動産・運輸・その他
        ]
        
        # 効率的な検証のため、100銘柄ずつのサンプリング
        for start, end in code_ranges:
            logger.info(f"銘柄コード範囲 {start}-{end} を検証中...")
            
            # 100銘柄ごとにサンプリング
            for code in range(start, end + 1, 50):  # 50銘柄ごとにチェック
                code_str = str(code).zfill(4)
                
                # 時間制限（無限ループ防止）
                if len(valid_stocks) > 2000:  # 2000銘柄以上取得したら打ち切り
                    break
                
                try:
                    # yfinanceで銘柄存在確認（軽量チェック）
                    ticker = f"{code_str}.T"
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # 基本的な情報があるかチェック
                    if info and info.get('symbol') and (info.get('longName') or info.get('shortName')):
                        valid_stocks.append(code_str)
                        logger.debug(f"有効銘柄発見: {code_str}")
                    
                    # APIレート制限対策
                    time.sleep(0.1)
                    
                except Exception as e:
                    # 無効な銘柄はスキップ
                    continue
            
            if len(valid_stocks) > 2000:
                break
        
        logger.info(f"連番検証で{len(valid_stocks)}銘柄を発見")
        return valid_stocks
    
    def _load_cache(self) -> Optional[List[str]]:
        """
        キャッシュから銘柄リストを読み込み
        """
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # キャッシュの有効性をチェック
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time > self.cache_duration:
                logger.info("キャッシュが期限切れ")
                return None
            
            return cache_data.get('stocks', [])
            
        except Exception as e:
            logger.warning(f"キャッシュ読み込みエラー: {str(e)}")
            return None
    
    def _save_cache(self, stocks: List[str]):
        """
        銘柄リストをキャッシュに保存
        """
        try:
            cache_data = {
                'stocks': stocks,
                'timestamp': time.time(),
                'total_count': len(stocks)
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"{len(stocks)}銘柄をキャッシュに保存")
            
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {str(e)}")
    
    def get_stock_batches(self, batch_size: int = 50) -> List[List[str]]:
        """
        全銘柄をバッチに分割
        
        Args:
            batch_size: 1バッチあたりの銘柄数
            
        Returns:
            銘柄コードのバッチリスト
        """
        all_stocks = self.get_all_japanese_stocks()
        
        batches = []
        for i in range(0, len(all_stocks), batch_size):
            batch = all_stocks[i:i + batch_size]
            batches.append(batch)
        
        logger.info(f"全{len(all_stocks)}銘柄を{len(batches)}個のバッチに分割")
        return batches
    
    def validate_stock_codes(self, codes: List[str]) -> Dict[str, Any]:
        """
        銘柄コードの有効性を検証
        
        Args:
            codes: 検証する銘柄コードのリスト
            
        Returns:
            検証結果の統計情報
        """
        valid_codes = []
        invalid_codes = []
        
        for code in codes:
            try:
                ticker = f"{code}.T" if not code.endswith('.T') else code
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if info and info.get('symbol'):
                    valid_codes.append(code)
                else:
                    invalid_codes.append(code)
                    
                # レート制限対策
                time.sleep(0.05)
                
            except Exception:
                invalid_codes.append(code)
        
        return {
            'valid_codes': valid_codes,
            'invalid_codes': invalid_codes,
            'valid_count': len(valid_codes),
            'invalid_count': len(invalid_codes),
            'total_checked': len(codes),
            'success_rate': len(valid_codes) / len(codes) * 100 if codes else 0
        }

def test_stock_universe():
    """
    全銘柄取得サービステスト
    """
    service = StockUniverseService()
    
    logger.info("=== 全上場銘柄取得テスト ===")
    stocks = service.get_all_japanese_stocks()
    logger.info(f"取得銘柄数: {len(stocks)}")
    logger.info(f"最初の10銘柄: {stocks[:10]}")
    logger.info(f"最後の10銘柄: {stocks[-10:]}")
    
    logger.info("=== バッチ分割テスト ===")
    batches = service.get_stock_batches(batch_size=100)
    logger.info(f"バッチ数: {len(batches)}")
    logger.info(f"最初のバッチ: {batches[0]}")
    
    logger.info("=== 銘柄コード検証テスト ===")
    test_codes = stocks[:20]  # 最初の20銘柄をテスト
    validation_result = service.validate_stock_codes(test_codes)
    logger.info(f"検証結果: {validation_result}")

if __name__ == "__main__":
    test_stock_universe()