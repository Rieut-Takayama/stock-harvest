"""
強化版決算スケジュール管理サービス
四半期別決算管理・黒字転換検出・IRバンク/カブタン統合
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import and_, or_, desc, asc
from ..database.config import database
from ..database.tables import earnings_schedule, stock_master, listing_dates
from .irbank_integration_service import IRBankIntegrationService
from .kabutan_integration_service import KabutanIntegrationService
from .earnings_analysis_service import EarningsAnalysisService
from ..lib.logger import logger

class EnhancedEarningsService:
    """強化版決算スケジュール管理専門サービス"""
    
    def __init__(self):
        # 外部連携サービス
        self.irbank_service = IRBankIntegrationService()
        self.kabutan_service = KabutanIntegrationService()
        self.earnings_analysis = EarningsAnalysisService()
        
        # 設定
        self.config = {
            'black_ink_threshold_months': 12,  # 黒字転換判定期間
            'forecast_accuracy_threshold': 0.15,  # 予想精度閾値（15%）
            'priority_sectors': ['テクノロジー', '医薬品', 'バイオ'],  # 優先業種
            'max_historical_years': 5,  # 過去データ保持年数
            'auto_update_earnings': True  # 自動決算データ更新
        }
    
    async def get_comprehensive_earnings_calendar(self, 
                                                 start_date: Optional[str] = None, 
                                                 end_date: Optional[str] = None,
                                                 include_forecasts: bool = True) -> Dict[str, Any]:
        """
        包括的な決算カレンダーを取得
        
        Args:
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）
            include_forecasts: 業績予想を含めるか
            
        Returns:
            決算カレンダーデータ
        """
        try:
            logger.info("📅 包括的決算カレンダー取得開始")
            
            # 日付範囲の設定
            if not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
            
            # 基本の決算スケジュールを取得
            earnings_query = """
                SELECT 
                    e.*,
                    l.market,
                    l.sector,
                    l.years_since_listing,
                    l.is_target as is_listing_target
                FROM earnings_schedule e
                LEFT JOIN listing_dates l ON e.stock_code = l.stock_code
                WHERE e.scheduled_date BETWEEN :start_date AND :end_date
                ORDER BY e.scheduled_date ASC, e.announcement_time ASC
            """
            
            earnings_results = await database.fetch_all(
                earnings_query, 
                values={"start_date": start_date, "end_date": end_date}
            )
            
            # 決算データを構造化
            calendar_data = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_days': (datetime.strptime(end_date, '%Y-%m-%d') - 
                                 datetime.strptime(start_date, '%Y-%m-%d')).days
                },
                'summary': {
                    'total_earnings': len(earnings_results),
                    'black_ink_candidates': 0,
                    'priority_sector_count': 0,
                    'listing_target_count': 0
                },
                'by_date': {},
                'by_quarter': {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': [], 'FY': []},
                'by_sector': {},
                'black_ink_candidates': [],
                'high_priority_earnings': []
            }
            
            # 各決算データを処理
            for row in earnings_results:
                earnings_item = await self._enrich_earnings_data(dict(row), include_forecasts)
                
                # 日付別グループ化
                sched_date = earnings_item['scheduled_date'].strftime('%Y-%m-%d')
                if sched_date not in calendar_data['by_date']:
                    calendar_data['by_date'][sched_date] = []
                calendar_data['by_date'][sched_date].append(earnings_item)
                
                # 四半期別グループ化
                quarter = earnings_item['fiscal_quarter']
                if quarter in calendar_data['by_quarter']:
                    calendar_data['by_quarter'][quarter].append(earnings_item)
                
                # 業種別グループ化
                sector = earnings_item.get('sector', '未分類')
                if sector not in calendar_data['by_sector']:
                    calendar_data['by_sector'][sector] = []
                calendar_data['by_sector'][sector].append(earnings_item)
                
                # 黒字転換候補
                if earnings_item.get('is_black_ink_conversion'):
                    calendar_data['black_ink_candidates'].append(earnings_item)
                    calendar_data['summary']['black_ink_candidates'] += 1
                
                # 優先セクター
                if sector in self.config['priority_sectors']:
                    calendar_data['summary']['priority_sector_count'] += 1
                
                # 上場対象
                if earnings_item.get('is_listing_target'):
                    calendar_data['summary']['listing_target_count'] += 1
                
                # 高優先度決算
                priority_score = self._calculate_earnings_priority(earnings_item)
                if priority_score >= 70:
                    calendar_data['high_priority_earnings'].append({
                        **earnings_item,
                        'priority_score': priority_score
                    })
            
            # 高優先度決算を優先度順でソート
            calendar_data['high_priority_earnings'].sort(
                key=lambda x: x['priority_score'], reverse=True
            )
            
            logger.info(f"✅ 決算カレンダー取得完了: {len(earnings_results)} 件")
            return calendar_data
            
        except Exception as e:
            logger.error(f"❌ 決算カレンダー取得エラー: {str(e)}")
            raise
    
    async def _enrich_earnings_data(self, earnings_base: Dict[str, Any], include_forecasts: bool = True) -> Dict[str, Any]:
        """決算データを追加情報で強化"""
        try:
            stock_code = earnings_base['stock_code']
            
            # 基本情報の構造化
            enriched = {
                **earnings_base,
                'days_until_earnings': self._calculate_days_until(earnings_base.get('scheduled_date')),
                'earnings_status_display': self._get_status_display(earnings_base.get('earnings_status')),
                'announcement_time_display': self._get_announcement_time_display(earnings_base.get('announcement_time'))
            }
            
            # 黒字転換判定の詳細化
            if earnings_base.get('is_black_ink_conversion'):
                enriched['black_ink_details'] = await self._analyze_black_ink_conversion(earnings_base)
            
            # カブタンから追加の財務データ取得（高優先度の場合のみ）
            priority_score = self._calculate_earnings_priority(earnings_base)
            if priority_score >= 60 and self.config['auto_update_earnings']:
                try:
                    kabutan_data = await self.kabutan_service.fetch_earnings_summary(stock_code)
                    if kabutan_data:
                        enriched['kabutan_data'] = {
                            'latest_results': kabutan_data.get('latest_annual'),
                            'growth_analysis': kabutan_data.get('growth_analysis'),
                            'risk_assessment': kabutan_data.get('risk_assessment')
                        }
                except Exception as e:
                    logger.warning(f"⚠️ {stock_code} カブタンデータ取得エラー: {str(e)}")
            
            # 業績予想データの取得
            if include_forecasts:
                enriched['forecasts'] = await self._get_earnings_forecasts(stock_code, earnings_base['fiscal_year'])
            
            # 過去実績との比較
            enriched['historical_comparison'] = await self._get_historical_comparison(stock_code)
            
            return enriched
            
        except Exception as e:
            logger.warning(f"⚠️ 決算データ強化エラー: {str(e)}")
            return earnings_base
    
    def _calculate_days_until(self, scheduled_date: Any) -> Optional[int]:
        """決算発表までの日数を計算"""
        try:
            if not scheduled_date:
                return None
            
            if isinstance(scheduled_date, str):
                target_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            elif isinstance(scheduled_date, datetime):
                target_date = scheduled_date.date()
            else:
                target_date = scheduled_date
            
            today = date.today()
            return (target_date - today).days
            
        except Exception:
            return None
    
    def _get_status_display(self, status: str) -> str:
        """決算ステータスの表示名を取得"""
        status_map = {
            'scheduled': '予定',
            'announced': '発表済み',
            'delayed': '延期',
            'cancelled': '中止'
        }
        return status_map.get(status, status)
    
    def _get_announcement_time_display(self, time_code: str) -> str:
        """発表時間の表示名を取得"""
        time_map = {
            'pre_market': '場前',
            'after_market': '場後',
            'trading_hours': '場中'
        }
        return time_map.get(time_code, time_code)
    
    def _calculate_earnings_priority(self, earnings_data: Dict[str, Any]) -> int:
        """決算の優先度スコアを計算"""
        score = 0
        
        # 黒字転換候補
        if earnings_data.get('is_black_ink_conversion'):
            score += 40
        
        # 上場対象（2.5-5年以内）
        if earnings_data.get('is_listing_target'):
            score += 30
        
        # 優先セクター
        sector = earnings_data.get('sector', '')
        if sector in self.config['priority_sectors']:
            score += 20
        
        # 決算発表までの日数
        days_until = self._calculate_days_until(earnings_data.get('scheduled_date'))
        if days_until is not None:
            if days_until <= 7:
                score += 20
            elif days_until <= 14:
                score += 10
        
        # ロジックB対象フラグ
        if earnings_data.get('is_target_for_logic_b'):
            score += 25
        
        return min(score, 100)  # 最大100点
    
    async def _analyze_black_ink_conversion(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """黒字転換の詳細分析"""
        try:
            stock_code = earnings_data['stock_code']
            
            # Yahoo Finance APIで詳細分析
            yahoo_analysis = self.earnings_analysis.get_earnings_data(stock_code)
            
            if yahoo_analysis and not yahoo_analysis.get('error'):
                return {
                    'conversion_type': yahoo_analysis.get('conversion_type'),
                    'growth_rate': yahoo_analysis.get('growth_rate'),
                    'profit_change_description': yahoo_analysis.get('profit_change_description'),
                    'trend_analysis': yahoo_analysis.get('trend_analysis'),
                    'operating_income_analysis': yahoo_analysis.get('operating_income'),
                    'quarterly_analysis': yahoo_analysis.get('quarterly')
                }
            else:
                return {
                    'conversion_type': 'unknown',
                    'analysis_available': False,
                    'error': yahoo_analysis.get('error') if yahoo_analysis else 'データ取得不可'
                }
                
        except Exception as e:
            logger.warning(f"⚠️ 黒字転換分析エラー: {str(e)}")
            return {'analysis_available': False, 'error': str(e)}
    
    async def _get_earnings_forecasts(self, stock_code: str, fiscal_year: int) -> Dict[str, Any]:
        """業績予想データを取得"""
        try:
            # データベースから既存の予想データを取得
            forecast_query = """
                SELECT forecast_revision
                FROM earnings_schedule
                WHERE stock_code = :stock_code AND fiscal_year = :fiscal_year
                AND forecast_revision IS NOT NULL
                ORDER BY updated_at DESC
                LIMIT 1
            """
            
            result = await database.fetch_one(
                forecast_query,
                values={"stock_code": stock_code, "fiscal_year": fiscal_year}
            )
            
            forecasts = {
                'has_forecasts': False,
                'revisions': [],
                'accuracy_analysis': None
            }
            
            if result and result['forecast_revision']:
                forecasts['has_forecasts'] = True
                forecasts['revisions'] = result['forecast_revision']
                
                # 予想精度の分析
                forecasts['accuracy_analysis'] = self._analyze_forecast_accuracy(
                    result['forecast_revision']
                )
            
            return forecasts
            
        except Exception as e:
            logger.warning(f"⚠️ 業績予想取得エラー: {str(e)}")
            return {'has_forecasts': False, 'error': str(e)}
    
    def _analyze_forecast_accuracy(self, forecast_revisions: Any) -> Dict[str, Any]:
        """予想精度を分析"""
        try:
            if not forecast_revisions or not isinstance(forecast_revisions, list):
                return {'accuracy_available': False}
            
            # 予想修正回数
            revision_count = len(forecast_revisions)
            
            # 修正幅の分析
            revision_magnitudes = []
            for revision in forecast_revisions:
                if isinstance(revision, dict) and 'magnitude' in revision:
                    revision_magnitudes.append(abs(revision['magnitude']))
            
            avg_revision = sum(revision_magnitudes) / len(revision_magnitudes) if revision_magnitudes else 0
            
            # 精度評価
            accuracy_level = 'high'
            if avg_revision > self.config['forecast_accuracy_threshold']:
                accuracy_level = 'low'
            elif avg_revision > self.config['forecast_accuracy_threshold'] / 2:
                accuracy_level = 'medium'
            
            return {
                'accuracy_available': True,
                'revision_count': revision_count,
                'average_revision_magnitude': round(avg_revision, 3),
                'accuracy_level': accuracy_level
            }
            
        except Exception as e:
            return {'accuracy_available': False, 'error': str(e)}
    
    async def _get_historical_comparison(self, stock_code: str) -> Dict[str, Any]:
        """過去実績との比較データを取得"""
        try:
            # 過去5年の決算データを取得
            historical_query = """
                SELECT fiscal_year, fiscal_quarter, revenue_actual, profit_actual
                FROM earnings_schedule
                WHERE stock_code = :stock_code
                AND revenue_actual IS NOT NULL
                AND fiscal_year >= :min_year
                ORDER BY fiscal_year DESC, 
                    CASE fiscal_quarter 
                        WHEN 'FY' THEN 5
                        WHEN 'Q4' THEN 4
                        WHEN 'Q3' THEN 3
                        WHEN 'Q2' THEN 2
                        WHEN 'Q1' THEN 1
                        ELSE 0
                    END DESC
                LIMIT 20
            """
            
            min_year = datetime.now().year - self.config['max_historical_years']
            
            results = await database.fetch_all(
                historical_query,
                values={"stock_code": stock_code, "min_year": min_year}
            )
            
            if not results:
                return {'historical_data_available': False}
            
            # データを年度・四半期別に整理
            annual_data = []
            quarterly_data = []
            
            for row in results:
                row_dict = dict(row)
                if row['fiscal_quarter'] == 'FY':
                    annual_data.append(row_dict)
                else:
                    quarterly_data.append(row_dict)
            
            # トレンド分析
            revenue_trend = self._analyze_trend([r['revenue_actual'] for r in annual_data[:3]])
            profit_trend = self._analyze_trend([r['profit_actual'] for r in annual_data[:3]])
            
            return {
                'historical_data_available': True,
                'years_of_data': len(annual_data),
                'quarters_of_data': len(quarterly_data),
                'latest_annual': annual_data[0] if annual_data else None,
                'latest_quarterly': quarterly_data[0] if quarterly_data else None,
                'trends': {
                    'revenue_trend': revenue_trend,
                    'profit_trend': profit_trend
                },
                'growth_rates': self._calculate_historical_growth_rates(annual_data)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ 過去実績比較エラー: {str(e)}")
            return {'historical_data_available': False, 'error': str(e)}
    
    def _analyze_trend(self, values: List[float]) -> str:
        """数値リストのトレンドを分析"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # 連続成長判定
        is_growing = True
        for i in range(len(values) - 1):
            if values[i] <= values[i + 1]:
                is_growing = False
                break
        
        if is_growing:
            return 'growing'
        
        # 連続減少判定
        is_declining = True
        for i in range(len(values) - 1):
            if values[i] >= values[i + 1]:
                is_declining = False
                break
        
        if is_declining:
            return 'declining'
        
        return 'volatile'
    
    def _calculate_historical_growth_rates(self, annual_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """過去の成長率を計算"""
        growth_rates = {
            'revenue_1y': None,
            'revenue_3y_cagr': None,
            'profit_1y': None,
            'profit_3y_cagr': None
        }
        
        if len(annual_data) >= 2:
            latest = annual_data[0]
            previous = annual_data[1]
            
            # 1年成長率
            if latest['revenue_actual'] and previous['revenue_actual']:
                growth_rates['revenue_1y'] = ((latest['revenue_actual'] - previous['revenue_actual']) / 
                                            abs(previous['revenue_actual'])) * 100
            
            if latest['profit_actual'] and previous['profit_actual'] and previous['profit_actual'] != 0:
                growth_rates['profit_1y'] = ((latest['profit_actual'] - previous['profit_actual']) / 
                                           abs(previous['profit_actual'])) * 100
        
        # 3年CAGR
        if len(annual_data) >= 4:
            latest = annual_data[0]
            three_years_ago = annual_data[3]
            
            if latest['revenue_actual'] and three_years_ago['revenue_actual'] and three_years_ago['revenue_actual'] > 0:
                growth_rates['revenue_3y_cagr'] = (((latest['revenue_actual'] / three_years_ago['revenue_actual']) ** (1/3)) - 1) * 100
            
            if (latest['profit_actual'] and three_years_ago['profit_actual'] and 
                three_years_ago['profit_actual'] > 0 and latest['profit_actual'] > 0):
                growth_rates['profit_3y_cagr'] = (((latest['profit_actual'] / three_years_ago['profit_actual']) ** (1/3)) - 1) * 100
        
        # 値を丸める
        for key, value in growth_rates.items():
            if value is not None:
                growth_rates[key] = round(value, 2)
        
        return growth_rates
    
    async def get_black_ink_conversion_pipeline(self) -> Dict[str, Any]:
        """黒字転換パイプライン分析"""
        try:
            logger.info("💰 黒字転換パイプライン分析開始")
            
            # 黒字転換候補を取得
            pipeline_query = """
                SELECT 
                    e.*,
                    l.market,
                    l.sector,
                    l.years_since_listing,
                    l.is_target as is_listing_target
                FROM earnings_schedule e
                LEFT JOIN listing_dates l ON e.stock_code = l.stock_code
                WHERE (
                    e.is_black_ink_conversion = true
                    OR e.is_target_for_logic_b = true
                    OR (e.profit_previous <= 0 AND e.profit_estimate > 0)
                )
                AND e.fiscal_year >= :current_year - 1
                ORDER BY 
                    CASE 
                        WHEN e.is_black_ink_conversion = true THEN 1
                        WHEN e.is_target_for_logic_b = true THEN 2
                        ELSE 3
                    END,
                    e.scheduled_date ASC
            """
            
            results = await database.fetch_all(
                pipeline_query,
                values={"current_year": datetime.now().year}
            )
            
            # パイプラインデータを構造化
            pipeline_data = {
                'summary': {
                    'total_candidates': len(results),
                    'confirmed_conversions': 0,
                    'probable_conversions': 0,
                    'potential_conversions': 0
                },
                'by_stage': {
                    'confirmed': [],    # 確実な黒字転換
                    'probable': [],     # 可能性高い
                    'potential': []     # 潜在的
                },
                'by_sector': {},
                'by_timing': {
                    'next_30_days': [],
                    'next_90_days': [],
                    'beyond_90_days': []
                },
                'risk_analysis': {
                    'high_confidence': [],
                    'medium_confidence': [],
                    'low_confidence': []
                }
            }
            
            # 各候補を分析・分類
            for row in results:
                candidate = dict(row)
                
                # 確実性の評価
                confidence_level = self._assess_conversion_confidence(candidate)
                stage = self._determine_conversion_stage(candidate)
                
                candidate['confidence_level'] = confidence_level
                candidate['conversion_stage'] = stage
                
                # ステージ別分類
                pipeline_data['by_stage'][stage].append(candidate)
                pipeline_data['summary'][f'{stage}_conversions'] += 1
                
                # 業種別分類
                sector = candidate.get('sector', '未分類')
                if sector not in pipeline_data['by_sector']:
                    pipeline_data['by_sector'][sector] = []
                pipeline_data['by_sector'][sector].append(candidate)
                
                # タイミング別分類
                days_until = self._calculate_days_until(candidate.get('scheduled_date'))
                if days_until is not None:
                    if days_until <= 30:
                        pipeline_data['by_timing']['next_30_days'].append(candidate)
                    elif days_until <= 90:
                        pipeline_data['by_timing']['next_90_days'].append(candidate)
                    else:
                        pipeline_data['by_timing']['beyond_90_days'].append(candidate)
                
                # リスク分析
                pipeline_data['risk_analysis'][confidence_level].append(candidate)
            
            logger.info(f"✅ 黒字転換パイプライン分析完了: {len(results)} 候補")
            return pipeline_data
            
        except Exception as e:
            logger.error(f"❌ 黒字転換パイプライン分析エラー: {str(e)}")
            raise
    
    def _assess_conversion_confidence(self, candidate: Dict[str, Any]) -> str:
        """黒字転換の確実性を評価"""
        score = 0
        
        # 確実な黒字転換フラグ
        if candidate.get('is_black_ink_conversion'):
            score += 60
        
        # 前期赤字、今期予想黒字
        if (candidate.get('profit_previous', 0) <= 0 and 
            candidate.get('profit_estimate', 0) > 0):
            score += 40
        
        # ロジックB対象
        if candidate.get('is_target_for_logic_b'):
            score += 30
        
        # 上場年数（若い企業ほど高スコア）
        years_since = candidate.get('years_since_listing', 10)
        if years_since <= 3:
            score += 20
        elif years_since <= 5:
            score += 10
        
        # 優先セクター
        if candidate.get('sector') in self.config['priority_sectors']:
            score += 15
        
        # 信頼度レベル決定
        if score >= 80:
            return 'high_confidence'
        elif score >= 50:
            return 'medium_confidence'
        else:
            return 'low_confidence'
    
    def _determine_conversion_stage(self, candidate: Dict[str, Any]) -> str:
        """転換ステージを判定"""
        # 既に発表済みで黒字転換確認
        if (candidate.get('earnings_status') == 'announced' and 
            candidate.get('is_black_ink_conversion')):
            return 'confirmed'
        
        # 発表予定で高確度
        if (candidate.get('earnings_status') == 'scheduled' and 
            candidate.get('is_black_ink_conversion')):
            return 'probable'
        
        # その他の候補
        return 'potential'
    
    async def update_earnings_from_external_sources(self, stock_codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """外部ソースから決算データを更新"""
        try:
            logger.info("🔄 外部ソース決算データ更新開始")
            
            # 対象銘柄の決定
            if not stock_codes:
                # 優先度の高い銘柄を自動選択
                target_query = """
                    SELECT DISTINCT stock_code
                    FROM earnings_schedule
                    WHERE (
                        is_black_ink_conversion = true
                        OR is_target_for_logic_b = true
                        OR scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
                    )
                    ORDER BY 
                        CASE 
                            WHEN is_black_ink_conversion = true THEN 1
                            WHEN is_target_for_logic_b = true THEN 2
                            ELSE 3
                        END
                    LIMIT 20
                """
                
                results = await database.fetch_all(target_query)
                stock_codes = [row['stock_code'] for row in results]
            
            # 更新統計
            update_stats = {
                'total_requested': len(stock_codes),
                'irbank_updates': 0,
                'kabutan_updates': 0,
                'errors': 0,
                'successful_stocks': []
            }
            
            # 各銘柄の更新
            for stock_code in stock_codes:
                try:
                    # IRバンクから適時開示情報を取得
                    disclosure_info = await self.irbank_service.fetch_disclosure_info(stock_code, days_back=14)
                    if disclosure_info:
                        update_stats['irbank_updates'] += len(disclosure_info)
                    
                    # カブタンから決算サマリーを取得
                    earnings_summary = await self.kabutan_service.fetch_earnings_summary(stock_code)
                    if earnings_summary:
                        # データベースを更新
                        saved = await self.kabutan_service.save_earnings_to_database(earnings_summary)
                        if saved:
                            update_stats['kabutan_updates'] += 1
                            update_stats['successful_stocks'].append(stock_code)
                    
                except Exception as e:
                    logger.warning(f"⚠️ {stock_code} 更新エラー: {str(e)}")
                    update_stats['errors'] += 1
                    continue
            
            logger.info(f"✅ 外部ソース更新完了: {update_stats}")
            return update_stats
            
        except Exception as e:
            logger.error(f"❌ 外部ソース更新エラー: {str(e)}")
            raise
    
    async def get_service_configuration(self) -> Dict[str, Any]:
        """サービス設定を取得"""
        return {
            'service_name': '強化版決算スケジュール管理サービス',
            'version': '1.0.0',
            'configuration': self.config,
            'capabilities': [
                '包括的決算カレンダー',
                '黒字転換パイプライン分析',
                'IRバンク・カブタン統合',
                '業績予想精度分析',
                '過去実績比較分析'
            ],
            'last_updated': datetime.now().isoformat()
        }

# テスト用関数
async def test_enhanced_earnings_service():
    """強化版決算サービスのテスト"""
    service = EnhancedEarningsService()
    
    logger.info("=== 強化版決算サービステスト開始 ===")
    
    try:
        # 決算カレンダー取得テスト
        calendar = await service.get_comprehensive_earnings_calendar()
        logger.info(f"決算カレンダー: {calendar['summary']['total_earnings']} 件")
        
        # 黒字転換パイプライン分析テスト
        pipeline = await service.get_black_ink_conversion_pipeline()
        logger.info(f"黒字転換候補: {pipeline['summary']['total_candidates']} 件")
        
        # 外部ソース更新テスト
        update_result = await service.update_earnings_from_external_sources(['7203', '6758'])
        logger.info(f"外部ソース更新: {update_result}")
        
        # サービス設定確認
        config = await service.get_service_configuration()
        logger.info(f"サービス設定: {config['service_name']}")
        
        logger.info("✅ 強化版決算サービステスト完了")
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_earnings_service())