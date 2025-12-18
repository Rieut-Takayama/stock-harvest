"""
IRバンク連携サービス
適時開示情報と決算短信データの自動取得・構造化
"""

import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from ..database.config import database
from ..database.tables import earnings_schedule, stock_master
from ..lib.logger import logger

class IRBankIntegrationService:
    """IRバンク連携専門サービス"""
    
    def __init__(self):
        # IRバンクの基本URL（概念的な実装）
        self.base_url = "https://irbank.net"
        self.api_endpoints = {
            'search_company': '/api/search/companies',
            'company_profile': '/api/companies/{company_id}',
            'earnings_schedule': '/api/earnings/schedule',
            'earnings_results': '/api/earnings/results/{company_id}',
            'disclosure_info': '/api/disclosure/{company_id}',
            'financial_data': '/api/financial/{company_id}'
        }
        
        # リクエストヘッダー
        self.headers = {
            'User-Agent': 'Stock Harvest AI Bot/1.0',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8'
        }
        
        # キャッシュ
        self.cache = {}
        self.cache_ttl = 3600  # 1時間
        
        # レート制限（毎分最大10リクエスト）
        self.rate_limit = {
            'requests_per_minute': 10,
            'request_times': []
        }
    
    async def fetch_earnings_schedule(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        決算発表予定を取得
        
        Args:
            target_date: 対象日（YYYY-MM-DD形式、未指定の場合は今日から1ヶ月）
            
        Returns:
            決算発表予定のリスト
        """
        try:
            logger.info("📊 IRバンク決算スケジュール取得開始")
            
            if not target_date:
                target_date = datetime.now().strftime('%Y-%m-%d')
            
            # レート制限チェック
            await self._check_rate_limit()
            
            # キャッシュチェック
            cache_key = f"earnings_schedule_{target_date}"
            cached_data = self._get_cache(cache_key)
            if cached_data:
                logger.info(f"📋 キャッシュからデータ取得: {len(cached_data)} 件")
                return cached_data
            
            # APIまたはスクレイピングでデータ取得
            earnings_data = await self._fetch_earnings_from_irbank(target_date)
            
            # データ構造化
            structured_data = self._structure_earnings_data(earnings_data)
            
            # キャッシュに保存
            self._set_cache(cache_key, structured_data)
            
            logger.info(f"✅ 決算スケジュール取得完了: {len(structured_data)} 件")
            return structured_data
            
        except Exception as e:
            logger.error(f"❌ IRバンク決算スケジュール取得エラー: {str(e)}")
            # フォールバック: サンプルデータ
            return self._get_sample_earnings_schedule()
    
    async def _fetch_earnings_from_irbank(self, target_date: str) -> List[Dict[str, Any]]:
        """
        IRバンクから決算データを実際に取得
        注意: 実際のAPIエンドポイントとフォーマットに応じて調整が必要
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
                
                # 実際のIRバンクAPIまたはスクレイピングの実装
                # 注意: IRバンクの利用規約とAPI仕様に従って実装する必要がある
                
                # 概念的な実装例
                url = f"{self.base_url}{self.api_endpoints['earnings_schedule']}"
                params = {
                    'date_from': target_date,
                    'date_to': (datetime.strptime(target_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'format': 'json'
                }
                
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            
                            if 'application/json' in content_type:
                                # JSON API レスポンス
                                data = await response.json()
                                return data.get('earnings', [])
                            else:
                                # HTML スクレイピング
                                html_content = await response.text()
                                return self._parse_earnings_html(html_content)
                        else:
                            logger.warning(f"⚠️ IRバンクAPI応答エラー: {response.status}")
                            return []
                
                except aiohttp.ClientError as e:
                    logger.warning(f"⚠️ IRバンク接続エラー: {str(e)}")
                    return []
                
        except Exception as e:
            logger.error(f"❌ IRバンクデータ取得エラー: {str(e)}")
            return []
    
    def _parse_earnings_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        IRバンクのHTMLページから決算情報を解析
        注意: 実際のHTML構造に合わせて調整が必要
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            earnings_list = []
            
            # IRバンクの決算テーブルを検索（概念的な実装）
            earnings_table = soup.find('table', {'class': 'earnings-schedule'})
            if not earnings_table:
                # 代替的な検索
                earnings_table = soup.find('table', {'id': 'earnings'})
            
            if earnings_table:
                rows = earnings_table.find_all('tr')[1:]  # ヘッダー行をスキップ
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        try:
                            earning_data = {
                                'date': cells[0].get_text(strip=True),
                                'company_code': self._extract_stock_code(cells[1].get_text(strip=True)),
                                'company_name': cells[1].get_text(strip=True),
                                'fiscal_quarter': cells[2].get_text(strip=True),
                                'announcement_time': cells[3].get_text(strip=True) if len(cells) > 3 else None,
                                'source': 'irbank_html'
                            }
                            
                            if earning_data['company_code']:
                                earnings_list.append(earning_data)
                        
                        except Exception as e:
                            logger.warning(f"⚠️ 行解析エラー: {str(e)}")
                            continue
            
            return earnings_list
            
        except Exception as e:
            logger.error(f"❌ IRバンクHTML解析エラー: {str(e)}")
            return []
    
    def _extract_stock_code(self, text: str) -> Optional[str]:
        """テキストから銘柄コード（4桁数字）を抽出"""
        match = re.search(r'\b\d{4}\b', text)
        return match.group() if match else None
    
    def _structure_earnings_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生データを構造化"""
        structured_data = []
        
        for item in raw_data:
            try:
                # 日付の正規化
                scheduled_date = self._normalize_date(item.get('date'))
                
                # 四半期の正規化
                fiscal_quarter = self._normalize_quarter(item.get('fiscal_quarter', ''))
                
                # 発表時間の正規化
                announcement_time = self._normalize_announcement_time(item.get('announcement_time', ''))
                
                structured_item = {
                    'stock_code': item.get('company_code'),
                    'stock_name': item.get('company_name', ''),
                    'fiscal_year': datetime.now().year,  # 概算
                    'fiscal_quarter': fiscal_quarter,
                    'scheduled_date': scheduled_date,
                    'announcement_time': announcement_time,
                    'earnings_status': 'scheduled',
                    'data_source': 'irbank',
                    'last_updated_from_source': datetime.now(),
                    'metadata_info': {
                        'irbank_raw_data': item,
                        'extracted_at': datetime.now().isoformat()
                    }
                }
                
                if structured_item['stock_code'] and structured_item['scheduled_date']:
                    structured_data.append(structured_item)
                    
            except Exception as e:
                logger.warning(f"⚠️ データ構造化エラー: {str(e)}")
                continue
        
        return structured_data
    
    def _normalize_date(self, date_str: str) -> Optional[datetime]:
        """日付文字列を正規化"""
        if not date_str:
            return None
        
        # 複数の日付フォーマットを試行
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%Y年%m月%d日'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _normalize_quarter(self, quarter_str: str) -> str:
        """四半期文字列を正規化"""
        quarter_mapping = {
            '第1四半期': 'Q1',
            '第2四半期': 'Q2', 
            '第3四半期': 'Q3',
            '第4四半期': 'Q4',
            '通期': 'FY',
            '1Q': 'Q1',
            '2Q': 'Q2',
            '3Q': 'Q3', 
            '4Q': 'Q4'
        }
        
        quarter_str = quarter_str.strip()
        return quarter_mapping.get(quarter_str, 'Q4')  # デフォルトは通期
    
    def _normalize_announcement_time(self, time_str: str) -> str:
        """発表時間を正規化"""
        time_str = time_str.lower().strip()
        
        if '前場' in time_str or 'pre' in time_str:
            return 'pre_market'
        elif '後場' in time_str or 'after' in time_str:
            return 'after_market'
        else:
            return 'trading_hours'
    
    async def fetch_disclosure_info(self, stock_code: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        適時開示情報を取得
        
        Args:
            stock_code: 銘柄コード
            days_back: 過去何日分取得するか
            
        Returns:
            適時開示情報のリスト
        """
        try:
            logger.info(f"📢 適時開示情報取得開始: {stock_code}")
            
            # レート制限チェック
            await self._check_rate_limit()
            
            # キャッシュチェック
            cache_key = f"disclosure_{stock_code}_{days_back}"
            cached_data = self._get_cache(cache_key)
            if cached_data:
                return cached_data
            
            # IRバンクから適時開示を取得
            disclosure_data = await self._fetch_disclosure_from_irbank(stock_code, days_back)
            
            # データ構造化
            structured_data = self._structure_disclosure_data(disclosure_data)
            
            # キャッシュに保存
            self._set_cache(cache_key, structured_data)
            
            logger.info(f"✅ 適時開示情報取得完了: {len(structured_data)} 件")
            return structured_data
            
        except Exception as e:
            logger.error(f"❌ 適時開示情報取得エラー: {str(e)}")
            return self._get_sample_disclosure_data(stock_code)
    
    async def _fetch_disclosure_from_irbank(self, stock_code: str, days_back: int) -> List[Dict[str, Any]]:
        """IRバンクから適時開示情報を取得"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
                
                url = f"{self.base_url}{self.api_endpoints['disclosure_info'].format(company_id=stock_code)}"
                params = {
                    'days_back': days_back,
                    'format': 'json'
                }
                
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            content = await response.text()
                            return self._parse_disclosure_html(content, stock_code)
                        else:
                            logger.warning(f"⚠️ 適時開示API応答エラー: {response.status}")
                            return []
                            
                except aiohttp.ClientError as e:
                    logger.warning(f"⚠️ 適時開示接続エラー: {str(e)}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ 適時開示データ取得エラー: {str(e)}")
            return []
    
    def _parse_disclosure_html(self, html_content: str, stock_code: str) -> List[Dict[str, Any]]:
        """適時開示HTMLを解析"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            disclosures = []
            
            # IRバンクの適時開示テーブルを検索
            disclosure_table = soup.find('table', {'class': 'disclosure-list'})
            if not disclosure_table:
                disclosure_table = soup.find('table', {'id': 'disclosure'})
            
            if disclosure_table:
                rows = disclosure_table.find_all('tr')[1:]  # ヘッダー行をスキップ
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        disclosure = {
                            'date': cells[0].get_text(strip=True),
                            'title': cells[1].get_text(strip=True),
                            'category': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                            'stock_code': stock_code,
                            'source': 'irbank_disclosure'
                        }
                        disclosures.append(disclosure)
            
            return disclosures
            
        except Exception as e:
            logger.error(f"❌ 適時開示HTML解析エラー: {str(e)}")
            return []
    
    def _structure_disclosure_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """適時開示データを構造化"""
        structured_data = []
        
        for item in raw_data:
            try:
                disclosure_date = self._normalize_date(item.get('date'))
                
                structured_item = {
                    'stock_code': item.get('stock_code'),
                    'disclosure_date': disclosure_date,
                    'title': item.get('title', ''),
                    'category': item.get('category', ''),
                    'is_earnings_related': self._is_earnings_related(item.get('title', '')),
                    'importance_level': self._assess_importance(item.get('title', '')),
                    'data_source': 'irbank',
                    'extracted_at': datetime.now(),
                    'metadata_info': {
                        'raw_data': item
                    }
                }
                
                if structured_item['disclosure_date']:
                    structured_data.append(structured_item)
                    
            except Exception as e:
                logger.warning(f"⚠️ 適時開示構造化エラー: {str(e)}")
                continue
        
        return structured_data
    
    def _is_earnings_related(self, title: str) -> bool:
        """タイトルから決算関連かどうかを判定"""
        earnings_keywords = [
            '決算', '業績', '売上', '利益', '損失', '四半期',
            '通期', '予想', '修正', '上方修正', '下方修正'
        ]
        
        return any(keyword in title for keyword in earnings_keywords)
    
    def _assess_importance(self, title: str) -> str:
        """適時開示の重要度を評価"""
        high_importance_keywords = [
            '業績修正', '重要事象', '合併', '買収', 'M&A',
            '上場廃止', '特別損失', '代表取締役'
        ]
        
        medium_importance_keywords = [
            '決算', '四半期', '配当', '株式分割',
            '新規事業', '業務提携'
        ]
        
        if any(keyword in title for keyword in high_importance_keywords):
            return 'high'
        elif any(keyword in title for keyword in medium_importance_keywords):
            return 'medium'
        else:
            return 'low'
    
    async def save_earnings_to_database(self, earnings_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """決算スケジュールをデータベースに保存"""
        try:
            logger.info(f"💾 決算スケジュールDB保存開始: {len(earnings_data)} 件")
            
            inserted = 0
            updated = 0
            errors = 0
            
            for data in earnings_data:
                try:
                    # IDの生成
                    earnings_id = f"earnings-{data['stock_code']}-{data['fiscal_year']}-{data['fiscal_quarter']}"
                    
                    # 既存データの確認
                    existing = await database.fetch_one(
                        earnings_schedule.select().where(
                            earnings_schedule.c.id == earnings_id
                        )
                    )
                    
                    # データ準備
                    db_data = {
                        'id': earnings_id,
                        'stock_code': data['stock_code'],
                        'stock_name': data['stock_name'],
                        'fiscal_year': data['fiscal_year'],
                        'fiscal_quarter': data['fiscal_quarter'],
                        'scheduled_date': data['scheduled_date'],
                        'announcement_time': data['announcement_time'],
                        'earnings_status': data['earnings_status'],
                        'data_source': data['data_source'],
                        'last_updated_from_source': data['last_updated_from_source'],
                        'metadata_info': data.get('metadata_info', {})
                    }
                    
                    if existing:
                        # 更新
                        await database.execute(
                            earnings_schedule.update().where(
                                earnings_schedule.c.id == earnings_id
                            ).values(**db_data)
                        )
                        updated += 1
                    else:
                        # 新規挿入
                        await database.execute(
                            earnings_schedule.insert().values(**db_data)
                        )
                        inserted += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ 決算データ保存エラー: {str(e)}")
                    errors += 1
                    continue
            
            result = {
                'inserted': inserted,
                'updated': updated,
                'errors': errors,
                'total': len(earnings_data)
            }
            
            logger.info(f"✅ 決算スケジュールDB保存完了: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 決算スケジュールDB保存エラー: {str(e)}")
            raise
    
    def _get_sample_earnings_schedule(self) -> List[Dict[str, Any]]:
        """サンプル決算スケジュールデータ"""
        return [
            {
                'stock_code': '7203',
                'stock_name': 'トヨタ自動車',
                'fiscal_year': 2024,
                'fiscal_quarter': 'Q3',
                'scheduled_date': datetime.now() + timedelta(days=7),
                'announcement_time': 'after_market',
                'earnings_status': 'scheduled',
                'data_source': 'irbank_sample',
                'last_updated_from_source': datetime.now(),
                'metadata_info': {'sample_data': True}
            },
            {
                'stock_code': '6758',
                'stock_name': 'ソニーグループ',
                'fiscal_year': 2024,
                'fiscal_quarter': 'Q3',
                'scheduled_date': datetime.now() + timedelta(days=14),
                'announcement_time': 'after_market',
                'earnings_status': 'scheduled',
                'data_source': 'irbank_sample',
                'last_updated_from_source': datetime.now(),
                'metadata_info': {'sample_data': True}
            }
        ]
    
    def _get_sample_disclosure_data(self, stock_code: str) -> List[Dict[str, Any]]:
        """サンプル適時開示データ"""
        return [
            {
                'stock_code': stock_code,
                'disclosure_date': datetime.now() - timedelta(days=1),
                'title': f'{stock_code} 第3四半期決算発表について',
                'category': '決算関連',
                'is_earnings_related': True,
                'importance_level': 'high',
                'data_source': 'irbank_sample',
                'extracted_at': datetime.now(),
                'metadata_info': {'sample_data': True}
            }
        ]
    
    async def _check_rate_limit(self):
        """レート制限チェック"""
        now = datetime.now().timestamp()
        # 1分前より古いリクエストを削除
        self.rate_limit['request_times'] = [
            t for t in self.rate_limit['request_times'] 
            if now - t < 60
        ]
        
        if len(self.rate_limit['request_times']) >= self.rate_limit['requests_per_minute']:
            # レート制限に引っかかった場合は少し待機
            await asyncio.sleep(1)
        
        self.rate_limit['request_times'].append(now)
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """キャッシュからデータ取得"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """キャッシュにデータ保存"""
        self.cache[key] = (data, datetime.now().timestamp())
    
    async def get_service_status(self) -> Dict[str, Any]:
        """IRバンク連携サービスの状態取得"""
        return {
            'service_name': 'IRバンク連携サービス',
            'status': 'active',
            'cache_entries': len(self.cache),
            'rate_limit_status': {
                'requests_in_last_minute': len(self.rate_limit['request_times']),
                'max_requests_per_minute': self.rate_limit['requests_per_minute']
            },
            'endpoints': self.api_endpoints,
            'last_updated': datetime.now().isoformat()
        }

# テスト用関数
async def test_irbank_integration():
    """IRバンク連携サービスのテスト"""
    service = IRBankIntegrationService()
    
    logger.info("=== IRバンク連携テスト開始 ===")
    
    # 決算スケジュール取得テスト
    earnings_data = await service.fetch_earnings_schedule()
    logger.info(f"決算スケジュール: {len(earnings_data)} 件取得")
    
    # 適時開示取得テスト
    disclosure_data = await service.fetch_disclosure_info('7203')
    logger.info(f"適時開示情報: {len(disclosure_data)} 件取得")
    
    # サービス状態確認
    status = await service.get_service_status()
    logger.info(f"サービス状態: {status['status']}")

if __name__ == "__main__":
    asyncio.run(test_irbank_integration())