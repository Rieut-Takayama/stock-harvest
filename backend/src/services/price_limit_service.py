"""
制限値幅計算サービス
日本株の値幅制限（ストップ高・ストップ安）価格を自動計算・管理
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from ..database.config import database
from ..database.tables import price_limits, stock_master, stock_data_cache

logger = logging.getLogger(__name__)


class PriceLimitService:
    """制限値幅計算専門サービス"""
    
    def __init__(self):
        # 日本株の値幅制限テーブル（2022年10月改正版）
        self.price_limit_table = [
            # (基準価格範囲下限, 基準価格範囲上限, 値幅制限額)
            (0, 100, 30),
            (100, 200, 50), 
            (200, 500, 80),
            (500, 700, 100),
            (700, 1000, 150),
            (1000, 1500, 300),
            (1500, 2000, 400),
            (2000, 3000, 500),
            (3000, 5000, 700),
            (5000, 7000, 1000),
            (7000, 10000, 1500),
            (10000, 15000, 3000),
            (15000, 20000, 4000),
            (20000, 30000, 5000),
            (30000, 50000, 7000),
            (50000, 70000, 10000),
            (70000, 100000, 15000),
            (100000, 150000, 30000),
            (150000, 200000, 40000),
            (200000, 300000, 50000),
            (300000, 500000, 70000),
            (500000, 700000, 100000),
            (700000, 1000000, 150000),
            (1000000, 1500000, 300000),
            (1500000, 2000000, 400000),
            (2000000, 3000000, 500000),
            (3000000, 5000000, 700000),
            (5000000, 7000000, 1000000),
            (7000000, 10000000, 1500000),
            (10000000, 15000000, 3000000),
            (15000000, float('inf'), 4000000)
        ]
        
        # 値幅拡大制度の倍率
        self.expansion_multipliers = {
            1: 1.0,    # 通常
            2: 2.0,    # 2倍拡大
            3: 3.0     # 3倍拡大（特別措置）
        }
    
    def calculate_price_limits(self, current_price: float, stage: int = 1) -> Dict[str, float]:
        """
        指定価格の制限値幅を計算
        
        Args:
            current_price: 基準価格
            stage: 値幅制限段階（1: 通常, 2: 2倍拡大, 3: 3倍拡大）
            
        Returns:
            上限・下限価格の辞書
        """
        try:
            # 価格を整数に丸める（円単位）
            price = int(round(current_price))
            
            # 該当する値幅制限を検索
            limit_amount = self._find_limit_amount(price)
            
            # 段階別倍率を適用
            multiplier = self.expansion_multipliers.get(stage, 1.0)
            adjusted_limit = int(limit_amount * multiplier)
            
            # 上限・下限を計算
            upper_limit = price + adjusted_limit
            lower_limit = max(1, price - adjusted_limit)  # 下限は1円以上
            
            return {
                'current_price': float(price),
                'upper_limit': float(upper_limit),
                'lower_limit': float(lower_limit),
                'limit_amount': float(adjusted_limit),
                'stage': stage,
                'price_range': self._get_price_range_name(price),
                'calculation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 制限値幅計算エラー (価格: {current_price}): {str(e)}")
            raise Exception(f"制限値幅計算に失敗しました: {str(e)}")
    
    def _find_limit_amount(self, price: int) -> int:
        """価格帯に対応する値幅制限額を取得"""
        for min_price, max_price, limit_amount in self.price_limit_table:
            if min_price <= price < max_price:
                return limit_amount
        
        # 最高価格帯を超える場合は最大制限額
        return self.price_limit_table[-1][2]
    
    def _get_price_range_name(self, price: int) -> str:
        """価格帯の名称を取得"""
        ranges = [
            (0, 100, "100円未満"),
            (100, 500, "100-500円"),
            (500, 1000, "500-1,000円"),
            (1000, 5000, "1,000-5,000円"),
            (5000, 10000, "5,000-10,000円"),
            (10000, 50000, "10,000-50,000円"),
            (50000, 100000, "50,000-100,000円"),
            (100000, 500000, "100,000-500,000円"),
            (500000, 1000000, "500,000-1,000,000円"),
            (1000000, float('inf'), "1,000,000円以上")
        ]
        
        for min_price, max_price, name in ranges:
            if min_price <= price < max_price:
                return name
        
        return "分類不明"
    
    async def update_stock_price_limits(self, stock_code: str, current_price: float, stage: int = 1) -> Dict:
        """
        指定銘柄の制限値幅をデータベースに更新
        
        Args:
            stock_code: 銘柄コード
            current_price: 現在価格
            stage: 値幅制限段階
            
        Returns:
            更新結果
        """
        try:
            # 制限値幅を計算
            limits = self.calculate_price_limits(current_price, stage)
            
            # 市場キャップレンジを判定（簡易版）
            market_cap_range = self._estimate_market_cap_range(current_price)
            
            # データベース更新用データ準備
            update_data = {
                'stock_code': stock_code,
                'current_price': Decimal(str(limits['current_price'])),
                'upper_limit': Decimal(str(limits['upper_limit'])),
                'lower_limit': Decimal(str(limits['lower_limit'])),
                'limit_stage': stage,
                'market_cap_range': market_cap_range,
                'price_range': limits['price_range'],
                'last_price_update': datetime.now(),
                'calculation_method': 'standard',
                'is_suspended': False,
                'metadata_info': {
                    'limit_amount': limits['limit_amount'],
                    'calculation_time': limits['calculation_time'],
                    'price_table_version': '2022-10'
                }
            }
            
            # 既存データ確認
            existing = await database.fetch_one(
                price_limits.select().where(price_limits.c.stock_code == stock_code)
            )
            
            if existing:
                # 更新
                await database.execute(
                    price_limits.update().where(
                        price_limits.c.stock_code == stock_code
                    ).values(**update_data)
                )
                action = "updated"
            else:
                # 新規挿入
                await database.execute(price_limits.insert().values(**update_data))
                action = "inserted"
            
            logger.info(f"✅ {stock_code} 制限値幅{action}: {limits['lower_limit']:.0f} - {limits['upper_limit']:.0f}")
            
            return {
                'stock_code': stock_code,
                'action': action,
                'limits': limits,
                'market_cap_range': market_cap_range
            }
            
        except Exception as e:
            logger.error(f"❌ {stock_code} 制限値幅更新エラー: {str(e)}")
            raise
    
    def _estimate_market_cap_range(self, current_price: float) -> str:
        """
        価格から時価総額レンジを推定（簡易版）
        実際には発行済み株式数が必要だが、概算として価格帯で分類
        """
        if current_price < 500:
            return "Small"
        elif current_price < 5000:
            return "Mid"
        else:
            return "Large"
    
    async def batch_update_price_limits(self, stock_price_data: List[Dict]) -> Dict[str, int]:
        """
        複数銘柄の制限値幅を一括更新
        
        Args:
            stock_price_data: [{'code': str, 'price': float}, ...]
            
        Returns:
            更新統計
        """
        try:
            logger.info(f"🔄 制限値幅一括更新開始: {len(stock_price_data)} 銘柄")
            
            updated = 0
            inserted = 0
            errors = 0
            
            for stock_data in stock_price_data:
                try:
                    result = await self.update_stock_price_limits(
                        stock_data['code'],
                        stock_data['price']
                    )
                    
                    if result['action'] == 'updated':
                        updated += 1
                    else:
                        inserted += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ {stock_data['code']} 更新エラー: {str(e)}")
                    errors += 1
                    continue
            
            result_stats = {
                'updated': updated,
                'inserted': inserted,
                'errors': errors,
                'total': len(stock_price_data)
            }
            
            logger.info(f"✅ 制限値幅一括更新完了: {result_stats}")
            return result_stats
            
        except Exception as e:
            logger.error(f"❌ 制限値幅一括更新エラー: {str(e)}")
            raise
    
    async def get_price_limit_info(self, stock_code: str) -> Optional[Dict]:
        """指定銘柄の制限値幅情報を取得"""
        try:
            result = await database.fetch_one(
                price_limits.select().where(price_limits.c.stock_code == stock_code)
            )
            
            if not result:
                return None
            
            return {
                'stock_code': result['stock_code'],
                'current_price': float(result['current_price']),
                'upper_limit': float(result['upper_limit']),
                'lower_limit': float(result['lower_limit']),
                'limit_stage': result['limit_stage'],
                'price_range': result['price_range'],
                'market_cap_range': result['market_cap_range'],
                'last_update': result['last_price_update'].isoformat() if result['last_price_update'] else None,
                'is_suspended': result['is_suspended'],
                'metadata': result['metadata_info']
            }
            
        except Exception as e:
            logger.error(f"❌ {stock_code} 制限値幅情報取得エラー: {str(e)}")
            return None
    
    async def check_price_alerts(self, stock_code: str, current_price: float) -> Dict[str, bool]:
        """
        価格がストップ高・ストップ安に接近しているかチェック
        
        Returns:
            アラート状況の辞書
        """
        try:
            limit_info = await self.get_price_limit_info(stock_code)
            
            if not limit_info:
                return {'alerts_available': False}
            
            # 接近度の閾値（5%以内）
            approach_threshold = 0.05
            
            # 上限への接近度計算
            upper_distance = (limit_info['upper_limit'] - current_price) / limit_info['current_price']
            lower_distance = (current_price - limit_info['lower_limit']) / limit_info['current_price']
            
            return {
                'alerts_available': True,
                'near_upper_limit': upper_distance <= approach_threshold,
                'near_lower_limit': lower_distance <= approach_threshold,
                'at_upper_limit': current_price >= limit_info['upper_limit'],
                'at_lower_limit': current_price <= limit_info['lower_limit'],
                'upper_distance_percent': round(upper_distance * 100, 2),
                'lower_distance_percent': round(lower_distance * 100, 2),
                'current_stage': limit_info['limit_stage']
            }
            
        except Exception as e:
            logger.error(f"❌ {stock_code} 価格アラートチェックエラー: {str(e)}")
            return {'alerts_available': False, 'error': str(e)}
    
    async def get_price_limit_stats(self) -> Dict:
        """制限値幅データの統計情報を取得"""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_stocks,
                    COUNT(CASE WHEN is_suspended = false THEN 1 END) as active_stocks,
                    COUNT(CASE WHEN limit_stage = 1 THEN 1 END) as normal_stage,
                    COUNT(CASE WHEN limit_stage = 2 THEN 1 END) as expanded_stage,
                    COUNT(CASE WHEN market_cap_range = 'Large' THEN 1 END) as large_cap,
                    COUNT(CASE WHEN market_cap_range = 'Mid' THEN 1 END) as mid_cap,
                    COUNT(CASE WHEN market_cap_range = 'Small' THEN 1 END) as small_cap,
                    AVG(current_price) as avg_price,
                    MAX(updated_at) as last_updated
                FROM price_limits
            """
            
            result = await database.fetch_one(stats_query)
            
            return {
                'total_stocks': result['total_stocks'],
                'active_stocks': result['active_stocks'],
                'stage_breakdown': {
                    'normal': result['normal_stage'],
                    'expanded': result['expanded_stage']
                },
                'market_cap_breakdown': {
                    'large': result['large_cap'],
                    'mid': result['mid_cap'],
                    'small': result['small_cap']
                },
                'avg_price': round(float(result['avg_price'] or 0), 2),
                'last_updated': result['last_updated'].isoformat() if result['last_updated'] else None
            }
            
        except Exception as e:
            logger.error(f"❌ 制限値幅統計取得エラー: {str(e)}")
            return {
                'total_stocks': 0,
                'active_stocks': 0,
                'stage_breakdown': {'normal': 0, 'expanded': 0},
                'market_cap_breakdown': {'large': 0, 'mid': 0, 'small': 0},
                'avg_price': 0,
                'last_updated': None
            }
    
    def get_price_limit_table_info(self) -> Dict:
        """価格制限テーブルの情報を取得"""
        return {
            'version': '2022-10改正版',
            'total_ranges': len(self.price_limit_table),
            'expansion_stages': list(self.expansion_multipliers.keys()),
            'max_limit_amount': self.price_limit_table[-1][2],
            'sample_calculations': [
                self.calculate_price_limits(100),
                self.calculate_price_limits(1000),
                self.calculate_price_limits(10000),
                self.calculate_price_limits(100000)
            ]
        }