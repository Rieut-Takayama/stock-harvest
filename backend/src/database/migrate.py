"""
データベースマイグレーション実行スクリプト
"""

import asyncio
from .config import engine, metadata, connect_db, disconnect_db
from .tables import system_info, faq, contact_inquiries, alerts, line_notification_config

async def create_tables():
    """テーブルを作成"""
    try:
        # メタデータからテーブルを作成
        metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
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
            print("✅ System info data seeded")
        
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
        
        print("✅ FAQ initial data seeded")
        
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
            print("✅ LINE notification config initialized")
        
        return True
    except Exception as e:
        print(f"❌ Failed to seed initial data: {e}")
        return False

async def migrate():
    """マイグレーション実行"""
    print("🔄 Starting database migration...")
    
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
        
        print("✅ Database migration completed successfully")
        return True
    finally:
        await disconnect_db()

if __name__ == "__main__":
    asyncio.run(migrate())