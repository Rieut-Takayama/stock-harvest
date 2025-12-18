"""
外部データソース自動更新スケジューラーサービス
定期的にIRバンク・カブタン・JSE等からデータを自動取得・更新
"""

import logging
import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .irbank_integration_service import IRBankIntegrationService
from .kabutan_integration_service import KabutanIntegrationService
from .listing_data_service import ListingDataService
from .price_limit_service import PriceLimitService
from ..database.config import database
from ..database.tables import stock_master, earnings_schedule
from ..lib.logger import logger

class DataSourceSchedulerService:
    """外部データソース自動更新専門サービス"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # 各種連携サービスの初期化
        self.irbank_service = IRBankIntegrationService()
        self.kabutan_service = KabutanIntegrationService()
        self.listing_service = ListingDataService()
        self.price_limit_service = PriceLimitService()
        
        # 実行履歴と統計
        self.execution_history = []
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'last_execution_time': None,
            'last_success_time': None,
            'last_error': None
        }
        
        # 設定
        self.config = {
            'use_sample_data': True,  # 本番では False に設定
            'max_concurrent_requests': 3,
            'error_retry_attempts': 2,
            'batch_size': 10,
            'enable_weekends': False  # 土日の実行を無効化
        }
    
    def setup_schedules(self):
        """スケジュールを設定"""
        try:
            logger.info("📅 データソーススケジューラー設定開始")
            
            # 1. 上場日データ更新（週次、月曜日 6:00）
            self.scheduler.add_job(
                self._update_listing_dates,
                CronTrigger(day_of_week='mon', hour=6, minute=0),
                id='listing_dates_weekly',
                name='上場日データ週次更新',
                replace_existing=True
            )
            
            # 2. 決算スケジュール更新（日次、平日 7:00）
            self.scheduler.add_job(
                self._update_earnings_schedule,
                CronTrigger(day_of_week='mon-fri', hour=7, minute=0),
                id='earnings_schedule_daily',
                name='決算スケジュール日次更新',
                replace_existing=True
            )
            
            # 3. 制限値幅更新（平日の取引時間中、30分間隔）
            self.scheduler.add_job(
                self._update_price_limits_batch,
                CronTrigger(day_of_week='mon-fri', hour='9-15', minute='*/30'),
                id='price_limits_trading_hours',
                name='制限値幅更新（取引時間中）',
                replace_existing=True
            )
            
            # 4. IRバンク適時開示情報取得（平日 8:00, 12:00, 17:00）
            self.scheduler.add_job(
                self._fetch_disclosure_updates,
                CronTrigger(day_of_week='mon-fri', hour='8,12,17', minute=0),
                id='disclosure_updates_daily',
                name='適時開示情報更新',
                replace_existing=True
            )
            
            # 5. カブタン決算データ取得（平日 20:00）
            self.scheduler.add_job(
                self._update_earnings_data_batch,
                CronTrigger(day_of_week='mon-fri', hour=20, minute=0),
                id='earnings_data_evening',
                name='決算データ夜間更新',
                replace_existing=True
            )
            
            # 6. 統計レポート生成（日次、平日 23:00）
            self.scheduler.add_job(
                self._generate_daily_report,
                CronTrigger(day_of_week='mon-fri', hour=23, minute=0),
                id='daily_report_generation',
                name='日次統計レポート生成',
                replace_existing=True
            )
            
            # 7. ヘルスチェック（15分間隔）
            self.scheduler.add_job(
                self._health_check,
                IntervalTrigger(minutes=15),
                id='health_check_interval',
                name='ヘルスチェック',
                replace_existing=True
            )
            
            logger.info("✅ スケジューラー設定完了")
            
        except Exception as e:
            logger.error(f"❌ スケジューラー設定エラー: {str(e)}")
            raise
    
    async def start_scheduler(self):
        """スケジューラーを開始"""
        try:
            if not self.is_running:
                self.setup_schedules()
                self.scheduler.start()
                self.is_running = True
                logger.info("🚀 データソーススケジューラー開始")
                
                # 初期実行テスト
                await self._initial_health_check()
            else:
                logger.warning("⚠️ スケジューラーは既に実行中です")
                
        except Exception as e:
            logger.error(f"❌ スケジューラー開始エラー: {str(e)}")
            raise
    
    async def stop_scheduler(self):
        """スケジューラーを停止"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("🛑 データソーススケジューラー停止")
            else:
                logger.warning("⚠️ スケジューラーは実行されていません")
                
        except Exception as e:
            logger.error(f"❌ スケジューラー停止エラー: {str(e)}")
            raise
    
    async def _update_listing_dates(self):
        """上場日データを更新"""
        job_name = "上場日データ更新"
        logger.info(f"📅 {job_name} 開始")
        
        try:
            start_time = datetime.now()
            
            # 上場日データ更新実行
            result = await self.listing_service.update_listing_data(
                use_sample=self.config['use_sample_data']
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 実行履歴に記録
            self._record_execution(job_name, True, execution_time, result)
            
            logger.info(f"✅ {job_name} 完了: {result}")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(job_name, False, execution_time, None, str(e))
            logger.error(f"❌ {job_name} エラー: {str(e)}")
    
    async def _update_earnings_schedule(self):
        """決算スケジュールを更新"""
        job_name = "決算スケジュール更新"
        logger.info(f"📊 {job_name} 開始")
        
        try:
            start_time = datetime.now()
            
            # IRバンクから決算スケジュール取得
            earnings_data = await self.irbank_service.fetch_earnings_schedule()
            
            # データベースに保存
            save_result = await self.irbank_service.save_earnings_to_database(earnings_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'earnings_fetched': len(earnings_data),
                'save_result': save_result
            }
            
            self._record_execution(job_name, True, execution_time, result)
            
            logger.info(f"✅ {job_name} 完了: {len(earnings_data)} 件取得")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(job_name, False, execution_time, None, str(e))
            logger.error(f"❌ {job_name} エラー: {str(e)}")
    
    async def _update_price_limits_batch(self):
        """制限値幅をバッチ更新"""
        job_name = "制限値幅バッチ更新"
        
        # 土日は実行しない
        if not self.config['enable_weekends'] and datetime.now().weekday() >= 5:
            logger.info(f"⏭️ {job_name} スキップ（土日）")
            return
        
        logger.info(f"💰 {job_name} 開始")
        
        try:
            start_time = datetime.now()
            
            # アクティブな銘柄リストを取得
            active_stocks = await self._get_active_stocks(limit=self.config['batch_size'])
            
            # 各銘柄の現在価格を取得（サンプルデータを使用）
            stock_price_data = []
            for stock in active_stocks:
                # 実際の実装では、株価APIから現在価格を取得
                sample_price = 1000 + (hash(stock['code']) % 5000)  # サンプル価格生成
                stock_price_data.append({
                    'code': stock['code'],
                    'price': sample_price
                })
            
            # 制限値幅を一括更新
            result = await self.price_limit_service.batch_update_price_limits(stock_price_data)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self._record_execution(job_name, True, execution_time, result)
            
            logger.info(f"✅ {job_name} 完了: {result['updated'] + result['inserted']} 件更新")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(job_name, False, execution_time, None, str(e))
            logger.error(f"❌ {job_name} エラー: {str(e)}")
    
    async def _fetch_disclosure_updates(self):
        """適時開示情報を取得"""
        job_name = "適時開示情報更新"
        logger.info(f"📢 {job_name} 開始")
        
        try:
            start_time = datetime.now()
            
            # 注目銘柄リストを取得
            target_stocks = await self._get_target_stocks_for_disclosure()
            
            total_disclosures = 0
            for stock in target_stocks[:self.config['batch_size']]:
                try:
                    # IRバンクから適時開示を取得
                    disclosures = await self.irbank_service.fetch_disclosure_info(
                        stock['code'], days_back=7
                    )
                    total_disclosures += len(disclosures)
                    
                    # レート制限を考慮して少し待機
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"⚠️ {stock['code']} 適時開示取得エラー: {str(e)}")
                    continue
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'stocks_checked': len(target_stocks[:self.config['batch_size']]),
                'disclosures_found': total_disclosures
            }
            
            self._record_execution(job_name, True, execution_time, result)
            
            logger.info(f"✅ {job_name} 完了: {total_disclosures} 件取得")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(job_name, False, execution_time, None, str(e))
            logger.error(f"❌ {job_name} エラー: {str(e)}")
    
    async def _update_earnings_data_batch(self):
        """決算データをバッチ更新"""
        job_name = "決算データバッチ更新"
        logger.info(f"💼 {job_name} 開始")
        
        try:
            start_time = datetime.now()
            
            # 決算発表予定の銘柄を取得
            earnings_due_stocks = await self._get_earnings_due_stocks()
            
            total_updated = 0
            for stock in earnings_due_stocks[:self.config['batch_size']]:
                try:
                    # カブタンから決算サマリーを取得
                    earnings_summary = await self.kabutan_service.fetch_earnings_summary(stock['code'])
                    
                    if earnings_summary:
                        # データベースに保存
                        saved = await self.kabutan_service.save_earnings_to_database(earnings_summary)
                        if saved:
                            total_updated += 1
                    
                    # レート制限を考慮して待機
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"⚠️ {stock['code']} 決算データ更新エラー: {str(e)}")
                    continue
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'stocks_checked': len(earnings_due_stocks[:self.config['batch_size']]),
                'earnings_updated': total_updated
            }
            
            self._record_execution(job_name, True, execution_time, result)
            
            logger.info(f"✅ {job_name} 完了: {total_updated} 件更新")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(job_name, False, execution_time, None, str(e))
            logger.error(f"❌ {job_name} エラー: {str(e)}")
    
    async def _generate_daily_report(self):
        """日次統計レポートを生成"""
        job_name = "日次統計レポート生成"
        logger.info(f"📋 {job_name} 開始")
        
        try:
            start_time = datetime.now()
            
            # 各種統計データを収集
            listing_stats = await self.listing_service.get_listing_stats()
            price_limit_stats = await self.price_limit_service.get_price_limit_stats()
            scheduler_stats = self.get_execution_statistics()
            
            # レポート生成
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'listing_data': listing_stats,
                'price_limits': price_limit_stats,
                'scheduler_performance': scheduler_stats,
                'generated_at': datetime.now()
            }
            
            # レポートをログに出力
            logger.info(f"📊 日次レポート:\n"
                       f"  上場銘柄: {listing_stats['total_stocks']} 件\n"
                       f"  スキャン対象: {listing_stats['target_stocks']} 件\n"
                       f"  制限値幅データ: {price_limit_stats['total_stocks']} 件\n"
                       f"  スケジューラー実行回数: {scheduler_stats['total_executions']} 回\n"
                       f"  成功率: {scheduler_stats['success_rate']:.1f}%")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self._record_execution(job_name, True, execution_time, report)
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(job_name, False, execution_time, None, str(e))
            logger.error(f"❌ {job_name} エラー: {str(e)}")
    
    async def _health_check(self):
        """ヘルスチェック"""
        try:
            # 各サービスの状態確認
            irbank_status = await self.irbank_service.get_service_status()
            kabutan_status = await self.kabutan_service.get_service_status()
            
            # データベース接続確認
            db_healthy = await self._check_database_connection()
            
            # スケジューラーの状態
            scheduler_healthy = self.is_running and self.scheduler.running
            
            overall_health = all([
                irbank_status['status'] == 'active',
                kabutan_status['status'] == 'active',
                db_healthy,
                scheduler_healthy
            ])
            
            if not overall_health:
                logger.warning("⚠️ ヘルスチェック警告: 一部サービスに問題があります")
            
        except Exception as e:
            logger.error(f"❌ ヘルスチェックエラー: {str(e)}")
    
    async def _initial_health_check(self):
        """初期ヘルスチェック"""
        logger.info("🏥 初期ヘルスチェック実行")
        
        try:
            # データベース接続確認
            db_healthy = await self._check_database_connection()
            if not db_healthy:
                raise Exception("データベース接続に失敗")
            
            # 各サービスの状態確認
            irbank_status = await self.irbank_service.get_service_status()
            kabutan_status = await self.kabutan_service.get_service_status()
            
            logger.info("✅ 初期ヘルスチェック完了")
            logger.info(f"  IRバンクサービス: {irbank_status['status']}")
            logger.info(f"  カブタンサービス: {kabutan_status['status']}")
            logger.info(f"  データベース: 接続OK")
            
        except Exception as e:
            logger.error(f"❌ 初期ヘルスチェック失敗: {str(e)}")
            raise
    
    async def _get_active_stocks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """アクティブな銘柄リストを取得"""
        try:
            query = """
                SELECT stock_code as code, company_name as name
                FROM listing_dates 
                WHERE is_target = true 
                ORDER BY years_since_listing ASC 
                LIMIT :limit
            """
            
            results = await database.fetch_all(query, values={"limit": limit})
            
            return [
                {'code': row['code'], 'name': row['name']}
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ アクティブ銘柄取得エラー: {str(e)}")
            return []
    
    async def _get_target_stocks_for_disclosure(self) -> List[Dict[str, Any]]:
        """適時開示監視対象の銘柄を取得"""
        try:
            # 過去30日以内に決算発表がある、または黒字転換候補の銘柄
            query = """
                SELECT DISTINCT e.stock_code as code, e.stock_name as name
                FROM earnings_schedule e
                WHERE (
                    e.scheduled_date >= CURRENT_DATE - INTERVAL '30 days'
                    OR e.is_target_for_logic_b = true
                )
                ORDER BY e.scheduled_date ASC
            """
            
            results = await database.fetch_all(query)
            
            return [
                {'code': row['code'], 'name': row['name']}
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ 適時開示対象銘柄取得エラー: {str(e)}")
            return []
    
    async def _get_earnings_due_stocks(self) -> List[Dict[str, Any]]:
        """決算発表予定銘柄を取得"""
        try:
            # 今後7日以内に決算発表予定、または最近発表済みでデータ未取得の銘柄
            query = """
                SELECT stock_code as code, stock_name as name, scheduled_date
                FROM earnings_schedule
                WHERE (
                    scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                    OR (
                        scheduled_date >= CURRENT_DATE - INTERVAL '3 days'
                        AND earnings_status = 'scheduled'
                    )
                )
                ORDER BY scheduled_date ASC
            """
            
            results = await database.fetch_all(query)
            
            return [
                {
                    'code': row['code'], 
                    'name': row['name'],
                    'scheduled_date': row['scheduled_date']
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ 決算予定銘柄取得エラー: {str(e)}")
            return []
    
    async def _check_database_connection(self) -> bool:
        """データベース接続確認"""
        try:
            await database.fetch_one("SELECT 1 as test")
            return True
        except Exception as e:
            logger.error(f"❌ データベース接続確認エラー: {str(e)}")
            return False
    
    def _record_execution(self, job_name: str, success: bool, execution_time: float, result: Any = None, error: str = None):
        """実行履歴を記録"""
        execution_record = {
            'job_name': job_name,
            'timestamp': datetime.now(),
            'success': success,
            'execution_time': execution_time,
            'result': result,
            'error': error
        }
        
        self.execution_history.append(execution_record)
        
        # 履歴は最新100件のみ保持
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        
        # 統計を更新
        self.execution_stats['total_executions'] += 1
        if success:
            self.execution_stats['successful_executions'] += 1
            self.execution_stats['last_success_time'] = datetime.now()
        else:
            self.execution_stats['failed_executions'] += 1
            self.execution_stats['last_error'] = error
        
        self.execution_stats['last_execution_time'] = datetime.now()
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """実行統計を取得"""
        total = self.execution_stats['total_executions']
        success_rate = (self.execution_stats['successful_executions'] / total * 100) if total > 0 else 0
        
        return {
            'total_executions': total,
            'successful_executions': self.execution_stats['successful_executions'],
            'failed_executions': self.execution_stats['failed_executions'],
            'success_rate': round(success_rate, 2),
            'last_execution_time': self.execution_stats['last_execution_time'],
            'last_success_time': self.execution_stats['last_success_time'],
            'last_error': self.execution_stats['last_error']
        }
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """スケジュール済みジョブ一覧を取得"""
        if not self.is_running:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
    
    async def execute_job_manually(self, job_id: str) -> Dict[str, Any]:
        """ジョブを手動実行"""
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                return {'success': False, 'message': f'ジョブ {job_id} が見つかりません'}
            
            logger.info(f"🔧 手動実行: {job.name}")
            
            # ジョブを即座に実行
            job.modify(next_run_time=datetime.now())
            
            return {
                'success': True,
                'message': f'ジョブ {job.name} を手動実行しました',
                'job_id': job_id
            }
            
        except Exception as e:
            logger.error(f"❌ ジョブ手動実行エラー: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def get_service_status(self) -> Dict[str, Any]:
        """サービス状態を取得"""
        return {
            'service_name': 'データソーススケジューラー',
            'is_running': self.is_running,
            'scheduler_running': self.scheduler.running if self.is_running else False,
            'total_jobs': len(self.scheduler.get_jobs()) if self.is_running else 0,
            'execution_statistics': self.get_execution_statistics(),
            'configuration': self.config,
            'last_updated': datetime.now().isoformat()
        }

# グローバルインスタンス
data_source_scheduler = DataSourceSchedulerService()

# テスト用関数
async def test_scheduler():
    """スケジューラーのテスト"""
    scheduler = DataSourceSchedulerService()
    
    logger.info("=== データソーススケジューラーテスト開始 ===")
    
    try:
        # スケジューラー開始
        await scheduler.start_scheduler()
        
        # 状態確認
        status = await scheduler.get_service_status()
        logger.info(f"スケジューラー状態: {status['is_running']}")
        
        # スケジュール済みジョブ一覧
        jobs = scheduler.get_scheduled_jobs()
        logger.info(f"スケジュール済みジョブ: {len(jobs)} 件")
        
        # 少し待機
        await asyncio.sleep(5)
        
        # スケジューラー停止
        await scheduler.stop_scheduler()
        
        logger.info("✅ スケジューラーテスト完了")
        
    except Exception as e:
        logger.error(f"❌ スケジューラーテストエラー: {str(e)}")
        await scheduler.stop_scheduler()

if __name__ == "__main__":
    asyncio.run(test_scheduler())