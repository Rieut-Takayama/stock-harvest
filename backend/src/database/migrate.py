"""
データベースマイグレーション実行スクリプト
"""

import asyncio
from .config import engine, metadata, connect_db, disconnect_db
from .tables import (
    system_info, faq, contact_inquiries, alerts, line_notification_config,
    scan_executions, scan_results, stock_master, manual_signals,
    listing_dates, price_limits, stock_data_cache, stock_filters,
    trading_signals, signal_executions, signal_performance, alert_history,
    earnings_schedule, trading_history, stock_archive, manual_scores, discord_config
)

async def create_tables():
    """テーブルを作成"""
    try:
        # メタデータからテーブルを作成
        metadata.create_all(bind=engine)
        # Database tables created successfully
        return True
    except Exception as e:
        # Failed to create tables
        return False

async def seed_initial_data():
    """初期データを投入"""
    try:
        # データベースに接続
        from .config import database
        
        # システム情報の初期データ
        system_data = {
            "id": 1,
            "version": "v1.0.0",
            "status": "healthy",
            "active_alerts": 0,
            "total_users": 1,
            "database_status": "connected",
            "status_display": "正常稼働中"
        }
        
        # 既存レコードがあるかチェック
        existing_system = await database.fetch_one("SELECT id FROM system_info WHERE id = 1")
        if not existing_system:
            await database.execute(
                "INSERT INTO system_info (id, version, status, active_alerts, total_users, database_status, status_display) VALUES (:id, :version, :status, :active_alerts, :total_users, :database_status, :status_display)",
                system_data
            )
            # System info data seeded
        
        # FAQの初期データ
        faq_data = [
            {
                "id": "faq-001",
                "category": "スキャン機能",
                "question": "ロジックスキャンはどのくらいの頻度で実行されますか？",
                "answer": "ロジックスキャンは平日の取引時間中、15分間隔で全銘柄を対象に実行されます。リアルタイムでの検出を目指していますが、データ取得の遅延により最大20分程度の遅れが発生する場合があります。",
                "tags": '["スキャン", "頻度", "リアルタイム"]',
                "display_order": 1
            },
            {
                "id": "faq-002", 
                "category": "アラート機能",
                "question": "アラート通知はLINE以外でも受け取れますか？",
                "answer": "現在はLINE Notifyのみに対応しています。今後、メールやSlack連携も検討予定です。",
                "tags": '["アラート", "LINE", "通知"]',
                "display_order": 2
            },
            {
                "id": "faq-003",
                "category": "ロジック説明",
                "question": "ロジックAとロジックBの違いは何ですか？",
                "answer": "ロジックAは「ストップ高張り付き銘柄」を検出し、ロジックBは「赤字→黒字転換銘柄」を検出します。どちらも独自のテクニカル分析に基づいた検出ロジックです。",
                "tags": '["ロジックA", "ロジックB", "検出条件"]',
                "display_order": 3
            },
            {
                "id": "faq-004",
                "category": "システム",
                "question": "データの更新頻度はどのくらいですか？",
                "answer": "株価データは平日の取引時間中、約15分間隔で更新されます。休日や取引時間外は更新されません。",
                "tags": '["データ更新", "頻度", "取引時間"]',
                "display_order": 4
            },
            {
                "id": "faq-005",
                "category": "トラブル",
                "question": "スキャンが実行できない場合はどうすれば良いですか？",
                "answer": "まず、システム稼働状況を確認してください。問題が続く場合は、お問い合わせフォームよりご連絡ください。平日9:00-18:00に対応いたします。",
                "tags": '["トラブル", "スキャンエラー", "サポート"]',
                "display_order": 5
            }
        ]
        
        # 既存のFAQレコードをチェック
        for faq_item in faq_data:
            existing_faq = await database.fetch_one("SELECT id FROM faq WHERE id = :id", {"id": faq_item["id"]})
            if not existing_faq:
                await database.execute(
                    """INSERT INTO faq (id, category, question, answer, tags, display_order) 
                       VALUES (:id, :category, :question, :answer, :tags, :display_order)""",
                    faq_item
                )
        
        # FAQ initial data seeded
        
        # LINE通知設定の初期データ
        line_config_data = {
            "id": 1,
            "is_connected": False,
            "status": "disconnected",
            "notification_count": 0,
            "error_count": 0
        }
        
        # 既存のLINE設定レコードをチェック
        existing_line_config = await database.fetch_one("SELECT id FROM line_notification_config WHERE id = 1")
        if not existing_line_config:
            await database.execute(
                """INSERT INTO line_notification_config (id, is_connected, status, notification_count, error_count) 
                   VALUES (:id, :is_connected, :status, :notification_count, :error_count)""",
                line_config_data
            )
            # LINE notification config initialized
        
        # 上場日データの初期データ（サンプル）
        sample_listing_data = [
            {
                'stock_code': '7203',
                'listing_date': '1949-05-16',
                'market': 'Prime',
                'sector': '自動車',
                'company_name': 'トヨタ自動車',
                'years_since_listing': 74.5,
                'is_target': False,
                'data_source': 'sample'
            },
            {
                'stock_code': '4477',
                'listing_date': '2019-10-25',
                'market': 'Growth',
                'sector': 'インターネット',
                'company_name': 'BASE',
                'years_since_listing': 4.1,
                'is_target': True,
                'data_source': 'sample'
            },
            {
                'stock_code': '4490',
                'listing_date': '2020-03-19',
                'market': 'Growth',
                'sector': 'インターネット',
                'company_name': 'ビザスク',
                'years_since_listing': 3.7,
                'is_target': True,
                'data_source': 'sample'
            }
        ]
        
        # 上場日データの投入
        for listing_item in sample_listing_data:
            existing_listing = await database.fetch_one(
                "SELECT stock_code FROM listing_dates WHERE stock_code = :stock_code", 
                {"stock_code": listing_item["stock_code"]}
            )
            if not existing_listing:
                await database.execute(
                    """INSERT INTO listing_dates 
                       (stock_code, listing_date, market, sector, company_name, years_since_listing, is_target, data_source) 
                       VALUES (:stock_code, :listing_date, :market, :sector, :company_name, :years_since_listing, :is_target, :data_source)""",
                    listing_item
                )
        
        # 制限値幅データの初期サンプル
        sample_price_limit_data = [
            {
                'stock_code': '7203',
                'current_price': 2900,
                'upper_limit': 3400,
                'lower_limit': 2400,
                'limit_stage': 1,
                'market_cap_range': 'Large',
                'price_range': '1,000-5,000円',
                'calculation_method': 'standard'
            },
            {
                'stock_code': '4477',
                'current_price': 420,
                'upper_limit': 500,
                'lower_limit': 340,
                'limit_stage': 1,
                'market_cap_range': 'Small',
                'price_range': '100-500円',
                'calculation_method': 'standard'
            }
        ]
        
        # 制限値幅データの投入
        for price_item in sample_price_limit_data:
            existing_price = await database.fetch_one(
                "SELECT stock_code FROM price_limits WHERE stock_code = :stock_code", 
                {"stock_code": price_item["stock_code"]}
            )
            if not existing_price:
                await database.execute(
                    """INSERT INTO price_limits 
                       (stock_code, current_price, upper_limit, lower_limit, limit_stage, market_cap_range, price_range, calculation_method) 
                       VALUES (:stock_code, :current_price, :upper_limit, :lower_limit, :limit_stage, :market_cap_range, :price_range, :calculation_method)""",
                    price_item
                )
        
        # 銘柄フィルタの初期データ
        filter_data = [
            {
                'id': 'filter-listing-period',
                'filter_name': '上場2.5-5年以内',
                'filter_type': 'listing_period',
                'criteria': '{"min_years": 2.5, "max_years": 5.0}',
                'description': '上場から2.5年以上5年以内の銘柄を対象',
                'is_active': True,
                'target_count': 100
            },
            {
                'id': 'filter-growth-market',
                'filter_name': 'グロース市場銘柄',
                'filter_type': 'market',
                'criteria': '{"markets": ["Growth"]}',
                'description': 'グロース市場上場の銘柄のみを対象',
                'is_active': True,
                'target_count': 50
            }
        ]
        
        # フィルタデータの投入
        for filter_item in filter_data:
            existing_filter = await database.fetch_one(
                "SELECT id FROM stock_filters WHERE id = :id", 
                {"id": filter_item["id"]}
            )
            if not existing_filter:
                await database.execute(
                    """INSERT INTO stock_filters 
                       (id, filter_name, filter_type, criteria, description, is_active, target_count) 
                       VALUES (:id, :filter_name, :filter_type, :criteria, :description, :is_active, :target_count)""",
                    filter_item
                )
        
        # Discord通知設定の初期データ
        discord_config_data = {
            "id": 1,
            "webhook_url": None,
            "is_enabled": False,
            "channel_name": None,
            "server_name": None,
            "notification_types": '["logic_a", "logic_b"]',
            "notification_format": "standard",
            "rate_limit_per_hour": 60,
            "notification_count_today": 0,
            "total_notifications_sent": 0,
            "error_count": 0,
            "connection_status": "disconnected"
        }
        
        # 既存のDiscord設定レコードをチェック
        existing_discord_config = await database.fetch_one("SELECT id FROM discord_config WHERE id = 1")
        if not existing_discord_config:
            await database.execute(
                """INSERT INTO discord_config (id, webhook_url, is_enabled, channel_name, server_name, notification_types, notification_format, rate_limit_per_hour, notification_count_today, total_notifications_sent, error_count, connection_status) 
                   VALUES (:id, :webhook_url, :is_enabled, :channel_name, :server_name, :notification_types, :notification_format, :rate_limit_per_hour, :notification_count_today, :total_notifications_sent, :error_count, :connection_status)""",
                discord_config_data
            )
            # Discord notification config initialized
        
        # 決算スケジュールのサンプルデータ
        sample_earnings_data = [
            {
                'id': 'earnings-7203-2024-Q3',
                'stock_code': '7203',
                'stock_name': 'トヨタ自動車',
                'fiscal_year': 2024,
                'fiscal_quarter': 'Q3',
                'scheduled_date': '2024-02-01 15:30:00',
                'earnings_status': 'announced',
                'revenue_estimate': 9500000,
                'profit_estimate': 850000,
                'revenue_actual': 9800000,
                'profit_actual': 920000,
                'profit_previous': 750000,
                'is_black_ink_conversion': False,
                'data_source': 'sample'
            },
            {
                'id': 'earnings-4477-2024-Q4',
                'stock_code': '4477',
                'stock_name': 'BASE',
                'fiscal_year': 2024,
                'fiscal_quarter': 'Q4',
                'scheduled_date': '2024-02-15 15:30:00',
                'earnings_status': 'announced',
                'revenue_estimate': 12000,
                'profit_estimate': -500,
                'revenue_actual': 13500,
                'profit_actual': 200,
                'profit_previous': -800,
                'is_black_ink_conversion': True,
                'is_target_for_logic_b': True,
                'data_source': 'sample'
            }
        ]
        
        # 決算データの投入
        for earnings_item in sample_earnings_data:
            existing_earnings = await database.fetch_one(
                "SELECT id FROM earnings_schedule WHERE id = :id", 
                {"id": earnings_item["id"]}
            )
            if not existing_earnings:
                await database.execute(
                    """INSERT INTO earnings_schedule 
                       (id, stock_code, stock_name, fiscal_year, fiscal_quarter, scheduled_date, earnings_status, revenue_estimate, profit_estimate, revenue_actual, profit_actual, profit_previous, is_black_ink_conversion, is_target_for_logic_b, data_source) 
                       VALUES (:id, :stock_code, :stock_name, :fiscal_year, :fiscal_quarter, :scheduled_date, :earnings_status, :revenue_estimate, :profit_estimate, :revenue_actual, :profit_actual, :profit_previous, :is_black_ink_conversion, :is_target_for_logic_b, :data_source)""",
                    earnings_item
                )
        
        # Initial data seeded for all new tables
        
        return True
    except Exception as e:
        # Failed to seed initial data
        return False

async def migrate():
    """マイグレーション実行"""
    # Starting database migration
    
    # データベース接続
    if not await connect_db():
        return False
    
    try:
        # テーブル作成
        if not await create_tables():
            return False
        
        # 初期データ投入
        if not await seed_initial_data():
            return False
        
        # Database migration completed successfully
        return True
    finally:
        await disconnect_db()

if __name__ == "__main__":
    asyncio.run(migrate())