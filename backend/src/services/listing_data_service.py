"""
上場日データ管理サービス
日本取引所グループの公開データを活用した上場日情報の管理
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
import pandas as pd
from ..database.config import database
from ..database.tables import listing_dates, stock_master

logger = logging.getLogger(__name__)


class ListingDataService:
    """上場日データ管理専門サービス"""
    
    def __init__(self):
        self.jse_data_sources = {
            # 日本取引所グループの公開データソース
            'prime': 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls',
            'standard': 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls',
            'growth': 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
        }
        
        # テスト用のサンプルデータ（本番では削除または無効化）
        self.sample_listing_data = [
            {"code": "7203", "name": "トヨタ自動車", "listing_date": "1949-05-16", "market": "Prime"},
            {"code": "6758", "name": "ソニーグループ", "listing_date": "1958-12-05", "market": "Prime"},
            {"code": "9984", "name": "ソフトバンクグループ", "listing_date": "1994-07-22", "market": "Prime"},
            {"code": "4689", "name": "Zホールディングス", "listing_date": "2019-10-01", "market": "Prime"},
            {"code": "8306", "name": "三菱UFJフィナンシャル・グループ", "listing_date": "2001-10-01", "market": "Prime"},
            {"code": "6861", "name": "キーエンス", "listing_date": "1995-10-26", "market": "Prime"},
            {"code": "9433", "name": "KDDI", "listing_date": "1993-10-27", "market": "Prime"},
            {"code": "4063", "name": "信越化学工業", "listing_date": "1949-05-16", "market": "Prime"},
            {"code": "6954", "name": "ファナック", "listing_date": "1976-07-20", "market": "Prime"},
            {"code": "8058", "name": "三菱商事", "listing_date": "1950-03-11", "market": "Prime"},
            # テスト用：最近上場した企業（2.5-5年範囲）
            {"code": "4477", "name": "BASE", "listing_date": "2019-10-25", "market": "Growth"},
            {"code": "4490", "name": "ビザスク", "listing_date": "2020-03-19", "market": "Growth"},
            {"code": "4475", "name": "HENNGE", "listing_date": "2019-10-10", "market": "Standard"}
        ]
    
    async def update_listing_data(self, use_sample: bool = True) -> Dict[str, int]:
        """
        上場日データを更新
        
        Args:
            use_sample: サンプルデータを使用するかどうか
            
        Returns:
            更新結果統計
        """
        try:
            logger.info("📅 上場日データ更新を開始")
            
            if use_sample:
                # 開発・テスト用：サンプルデータを使用
                listing_data = self._prepare_sample_data()
                logger.info(f"🧪 サンプルデータを使用: {len(listing_data)} 件")
            else:
                # 本番用：実際のJSEデータを取得
                listing_data = await self._fetch_jse_listing_data()
                logger.info(f"📊 JSEデータを取得: {len(listing_data)} 件")
            
            # データベースに保存
            result = await self._save_listing_data(listing_data)
            
            # 上場期間をもとにスキャン対象フラグを更新
            target_count = await self._update_target_flags()
            result['target_stocks'] = target_count
            
            logger.info(f"✅ 上場日データ更新完了: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 上場日データ更新エラー: {str(e)}")
            raise Exception(f"上場日データ更新に失敗しました: {str(e)}")
    
    def _prepare_sample_data(self) -> List[Dict]:
        """サンプルデータを準備"""
        prepared_data = []
        
        for item in self.sample_listing_data:
            # 上場からの年数を計算
            listing_date = datetime.strptime(item['listing_date'], '%Y-%m-%d')
            years_since_listing = (datetime.now() - listing_date).days / 365.25
            
            # スキャン対象判定（2.5年～5年以内）
            is_target = 2.5 <= years_since_listing <= 5.0
            
            prepared_data.append({
                'stock_code': item['code'],
                'listing_date': listing_date,
                'market': item['market'],
                'company_name': item['name'],
                'years_since_listing': round(years_since_listing, 2),
                'is_target': is_target,
                'data_source': 'sample',
                'sector': self._guess_sector(item['name']),
                'metadata_info': {
                    'sample_data': True,
                    'prepared_at': datetime.now().isoformat()
                }
            })
        
        return prepared_data
    
    def _guess_sector(self, company_name: str) -> str:
        """会社名から業種を推測（簡易版）"""
        sector_keywords = {
            '自動車': 'トヨタ',
            'テクノロジー': 'ソニー,キーエンス,ファナック',
            '通信': 'ソフトバンク,KDDI',
            '金融': '三菱UFJ',
            '商社': '三菱商事',
            '化学': '信越化学',
            'インターネット': 'Z Holdings,BASE,ビザスク,HENNGE'
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in company_name for keyword in keywords.split(',')):
                return sector
        
        return '分類不明'
    
    async def _fetch_jse_listing_data(self) -> List[Dict]:
        """
        日本取引所グループから実際のデータを取得
        注意: 実装は概念的なもの。実際のAPIエンドポイントとフォーマットに応じて調整が必要
        """
        try:
            # 実際の実装では、JSEの公開データAPIまたはExcelファイルを解析
            # ここではHTTPリクエストのサンプル実装
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                listing_data = []
                
                for market, url in self.jse_data_sources.items():
                    try:
                        logger.info(f"📥 {market}市場データを取得中...")
                        
                        # 注意: 実際のエンドポイントに合わせて調整必要
                        async with session.get(url) as response:
                            if response.status == 200:
                                # Excelファイルの場合、pandas.read_excelを使用
                                # ここでは仮想的な処理
                                content = await response.read()
                                market_data = self._parse_jse_excel_data(content, market)
                                listing_data.extend(market_data)
                            else:
                                logger.warning(f"⚠️ {market}市場データ取得失敗: {response.status}")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ {market}市場データ取得エラー: {str(e)}")
                        continue
                
                if not listing_data:
                    # フォールバック: サンプルデータを使用
                    logger.warning("🔄 JSEデータ取得失敗、サンプルデータにフォールバック")
                    return self._prepare_sample_data()
                
                return listing_data
                
        except Exception as e:
            logger.error(f"❌ JSEデータ取得エラー: {str(e)}")
            # エラー時はサンプルデータを返す
            return self._prepare_sample_data()
    
    def _parse_jse_excel_data(self, excel_content: bytes, market: str) -> List[Dict]:
        """
        JSEのExcelデータを解析
        注意: 実際のファイル構造に応じて実装調整が必要
        """
        try:
            # pandas で Excel を読み込み（実際の列名に調整必要）
            # df = pd.read_excel(io.BytesIO(excel_content))
            
            # 仮想的な解析処理
            # 実際には、Excelの具体的な列構造に合わせる
            parsed_data = []
            
            # 仮の実装：実際のExcel解析ロジックに置き換える
            logger.info(f"📊 {market}市場データの解析をスキップ（実装が必要）")
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"❌ {market}市場データ解析エラー: {str(e)}")
            return []
    
    async def _save_listing_data(self, listing_data: List[Dict]) -> Dict[str, int]:
        """上場日データをデータベースに保存"""
        try:
            inserted = 0
            updated = 0
            errors = 0
            
            for data in listing_data:
                try:
                    # 既存データの確認
                    existing = await database.fetch_one(
                        listing_dates.select().where(
                            listing_dates.c.stock_code == data['stock_code']
                        )
                    )
                    
                    if existing:
                        # 更新
                        await database.execute(
                            listing_dates.update().where(
                                listing_dates.c.stock_code == data['stock_code']
                            ).values(**data)
                        )
                        updated += 1
                    else:
                        # 新規挿入
                        await database.execute(
                            listing_dates.insert().values(**data)
                        )
                        inserted += 1
                
                except Exception as e:
                    logger.warning(f"⚠️ 銘柄 {data['stock_code']} 保存エラー: {str(e)}")
                    errors += 1
                    continue
            
            return {
                'inserted': inserted,
                'updated': updated,
                'errors': errors,
                'total': len(listing_data)
            }
            
        except Exception as e:
            logger.error(f"❌ 上場日データ保存エラー: {str(e)}")
            raise
    
    async def _update_target_flags(self) -> int:
        """上場期間に基づいてスキャン対象フラグを更新"""
        try:
            # 現在の日付から2.5-5年範囲を計算
            now = datetime.now()
            min_date = now - timedelta(days=5*365.25)  # 5年前
            max_date = now - timedelta(days=2.5*365.25)  # 2.5年前
            
            # 対象範囲の銘柄を is_target = True に更新
            result = await database.execute(
                listing_dates.update().where(
                    (listing_dates.c.listing_date >= min_date) &
                    (listing_dates.c.listing_date <= max_date)
                ).values(is_target=True)
            )
            
            # 範囲外の銘柄を is_target = False に更新
            await database.execute(
                listing_dates.update().where(
                    (listing_dates.c.listing_date < min_date) |
                    (listing_dates.c.listing_date > max_date)
                ).values(is_target=False)
            )
            
            logger.info(f"✅ スキャン対象フラグ更新完了: {result} 件が対象")
            return result
            
        except Exception as e:
            logger.error(f"❌ スキャン対象フラグ更新エラー: {str(e)}")
            return 0
    
    async def get_target_stocks(self, limit: int = 100) -> List[Dict]:
        """スキャン対象銘柄リストを取得"""
        try:
            query = """
                SELECT 
                    stock_code,
                    company_name,
                    listing_date,
                    market,
                    sector,
                    years_since_listing
                FROM listing_dates 
                WHERE is_target = true 
                ORDER BY listing_date DESC 
                LIMIT :limit
            """
            
            results = await database.fetch_all(query, values={"limit": limit})
            
            return [
                {
                    'code': row['stock_code'],
                    'name': row['company_name'],
                    'listing_date': row['listing_date'].isoformat(),
                    'market': row['market'],
                    'sector': row['sector'],
                    'years_since_listing': float(row['years_since_listing'])
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ スキャン対象銘柄取得エラー: {str(e)}")
            return []
    
    async def get_listing_stats(self) -> Dict:
        """上場日データの統計情報を取得"""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_stocks,
                    COUNT(CASE WHEN is_target = true THEN 1 END) as target_stocks,
                    COUNT(CASE WHEN market = 'Prime' THEN 1 END) as prime_count,
                    COUNT(CASE WHEN market = 'Standard' THEN 1 END) as standard_count,
                    COUNT(CASE WHEN market = 'Growth' THEN 1 END) as growth_count,
                    AVG(years_since_listing) as avg_years_listed,
                    MAX(last_updated) as last_updated
                FROM listing_dates
            """
            
            result = await database.fetch_one(stats_query)
            
            return {
                'total_stocks': result['total_stocks'],
                'target_stocks': result['target_stocks'],
                'market_breakdown': {
                    'prime': result['prime_count'],
                    'standard': result['standard_count'],
                    'growth': result['growth_count']
                },
                'avg_years_listed': round(float(result['avg_years_listed'] or 0), 2),
                'last_updated': result['last_updated'].isoformat() if result['last_updated'] else None
            }
            
        except Exception as e:
            logger.error(f"❌ 上場統計取得エラー: {str(e)}")
            return {
                'total_stocks': 0,
                'target_stocks': 0,
                'market_breakdown': {'prime': 0, 'standard': 0, 'growth': 0},
                'avg_years_listed': 0,
                'last_updated': None
            }