"""
FAQシードデータ投入スクリプト
API仕様書(docs/api-specs/contact-support-api.md)に基づくFAQデータをデータベースに投入
"""

import asyncio
import sys
import json
from datetime import datetime

sys.path.append('.')

from src.database.config import database, connect_db, disconnect_db
from src.lib.logger import logger

# Stock Harvest AI用のFAQデータ
FAQ_DATA = [
    {
        "id": "1",
        "category": "スキャン機能",
        "question": "ロジックスキャンはどのくらいの頻度で実行されますか?",
        "answer": "ロジックスキャンは平日の取引時間中、15分間隔で全銘柄を対象に実行されます。市場終了後の15時30分に最終スキャンが実行され、その日の総合結果がまとめられます。",
        "tags": ["スキャン", "実行頻度", "自動実行"],
        "display_order": 1
    },
    {
        "id": "2",
        "category": "ロジック説明",
        "question": "ストップ高張り付きロジック(Logic A)とは何ですか?",
        "answer": "ストップ高張り付きロジックは、以下5つの条件をすべて満たす超希少な銘柄パターンを検知します:\n1. ストップ高価格に到達(終値=ストップ高価格)\n2. 始値=終値(張り付き状態)\n3. 安値が終値の1%未満\n4. 上場5年未満の銘柄\n5. 四半期決算発表の翌営業日\n\n月間0-3銘柄程度の極めて稀な現象です。",
        "tags": ["ロジックA", "ストップ高", "条件", "決算"],
        "display_order": 2
    },
    {
        "id": "3",
        "category": "ロジック説明",
        "question": "赤字→黒字転換ロジック(Logic B)とは何ですか?",
        "answer": "赤字→黒字転換ロジックは、前四半期まで赤字だった企業が当四半期で黒字に転換し、決算発表日に特定の価格変動パターンを示した銘柄を検知します。\n\n条件:\n- 前四半期の営業利益が赤字\n- 当四半期の営業利益が黒字\n- 決算発表日の株価動向が特定パターンに該当\n- 上場5年未満の小型成長株\n\n業績急回復の初期段階を捉えるロジックです。",
        "tags": ["ロジックB", "赤字黒字転換", "決算", "業績"],
        "display_order": 3
    },
    {
        "id": "4",
        "category": "アラート機能",
        "question": "アラート通知はどのように設定しますか?",
        "answer": "アラート通知は2種類あります:\n\n1. **価格到達アラート**: 指定した銘柄が目標価格に到達したら通知\n2. **ロジック発動アラート**: 特定のロジック(A/B)で銘柄が検知されたら通知\n\nLINE Notify連携により、リアルタイムで通知を受け取ることができます。設定は「システム設定・管理」ページから行えます。",
        "tags": ["アラート", "通知", "LINE", "設定"],
        "display_order": 4
    },
    {
        "id": "5",
        "category": "アラート機能",
        "question": "LINE通知の設定方法を教えてください",
        "answer": "LINE通知の設定手順:\n\n1. LINE Notifyの公式サイトにアクセス(https://notify-bot.line.me/)\n2. 「マイページ」から「トークンを発行する」を選択\n3. 通知を受け取りたいトークルームを選択してトークン発行\n4. 発行されたトークンをStock Harvest AIの「システム設定・管理」ページで登録\n\nトークンは安全に保管し、外部に漏らさないでください。",
        "tags": ["LINE", "通知設定", "トークン"],
        "display_order": 5
    },
    {
        "id": "6",
        "category": "システム",
        "question": "データソースはどこから取得していますか?",
        "answer": "Stock Harvest AIは以下のデータソースを使用しています:\n\n- **株価データ**: Yahoo Finance API(20分遅延データ)\n- **決算情報**: IRBank、Kabutan等の公開データ\n- **上場情報**: 各証券取引所の公開データ\n\nデータは毎日自動的に更新され、最新の市場状況を反映します。",
        "tags": ["データソース", "Yahoo Finance", "決算情報"],
        "display_order": 6
    },
    {
        "id": "7",
        "category": "システム",
        "question": "検知された銘柄の信頼性はどのくらいですか?",
        "answer": "Stock Harvest AIは統計的に優位性のあるパターンを検知するツールであり、投資助言ではありません。\n\n重要な注意点:\n- 検知された銘柄が必ず上昇するわけではありません\n- 過去の統計パターンに基づく検索ツールです\n- 投資判断は必ずご自身の責任で行ってください\n- リスク管理(損切り・資金管理)を徹底してください\n\nあくまで投資判断の補助ツールとしてご活用ください。",
        "tags": ["信頼性", "リスク", "免責事項"],
        "display_order": 7
    },
    {
        "id": "8",
        "category": "トラブル",
        "question": "スキャンが実行されていないようです",
        "answer": "スキャンが実行されていない場合、以下を確認してください:\n\n1. **時間帯の確認**: スキャンは平日の取引時間中のみ実行されます\n2. **システム稼働状況**: トップページの「システム情報」でステータスを確認\n3. **データベース接続**: 「システム設定・管理」ページで接続状態を確認\n\n問題が解決しない場合は、お問い合わせフォームからご連絡ください。",
        "tags": ["トラブル", "スキャン", "エラー"],
        "display_order": 8
    },
    {
        "id": "9",
        "category": "トラブル",
        "question": "CSV出力が正常に動作しません",
        "answer": "CSV出力のトラブルシューティング:\n\n1. **ブラウザの確認**: Chrome、Firefox、Safariの最新版を推奨\n2. **ポップアップブロック**: ブラウザのポップアップブロックを無効化\n3. **ダウンロードフォルダ**: ブラウザのダウンロード設定を確認\n4. **データの有無**: 抽出結果が0件の場合はCSV出力できません\n\n問題が続く場合は、お問い合わせフォームから詳細をご連絡ください。",
        "tags": ["トラブル", "CSV", "エクスポート"],
        "display_order": 9
    },
    {
        "id": "10",
        "category": "システム",
        "question": "システムの利用料金はかかりますか?",
        "answer": "Stock Harvest AIは個人利用向けのツールとして開発されています。\n\n現在の利用条件:\n- 基本機能は無料で利用可能\n- 外部API(Yahoo Finance)の制限により、1日のリクエスト数に上限あり\n- LINE通知機能は無料(LINE Notify利用)\n\n将来的に機能拡張や商用利用オプションを追加する可能性がありますが、現時点では個人利用は無料です。",
        "tags": ["料金", "無料", "利用条件"],
        "display_order": 10
    }
]


async def seed_faq_data() -> None:
    """
    FAQデータをデータベースに投入
    """
    try:
        logger.info("FAQシードデータ投入開始")

        # データベース接続
        await connect_db()

        # 既存のFAQデータを確認
        existing_count_result = await database.fetch_one("SELECT COUNT(*) as count FROM faq")
        existing_count = existing_count_result["count"] if existing_count_result else 0

        if existing_count > 0:
            logger.info(f"既存のFAQデータが{existing_count}件存在します")
            user_input = input(f"既存のFAQデータ({existing_count}件)を削除して再投入しますか? (yes/no): ")

            if user_input.lower() == 'yes':
                await database.execute("DELETE FROM faq")
                logger.info("既存のFAQデータを削除しました")
            else:
                logger.info("FAQデータの投入をキャンセルしました")
                await disconnect_db()
                return

        # FAQデータを投入
        insert_query = """
        INSERT INTO faq
        (id, category, question, answer, tags, display_order, is_active, created_at, updated_at)
        VALUES
        (:id, :category, :question, :answer, :tags, :display_order, :is_active, :created_at, :updated_at)
        """

        current_time = datetime.now()
        inserted_count = 0

        for faq_item in FAQ_DATA:
            values = {
                "id": faq_item["id"],
                "category": faq_item["category"],
                "question": faq_item["question"],
                "answer": faq_item["answer"],
                "tags": json.dumps(faq_item["tags"], ensure_ascii=False),
                "display_order": faq_item["display_order"],
                "is_active": True,
                "created_at": current_time,
                "updated_at": current_time
            }

            await database.execute(insert_query, values)
            inserted_count += 1
            logger.info(f"FAQ投入: [{faq_item['category']}] {faq_item['question'][:30]}...")

        logger.info(f"✅ FAQシードデータ投入完了: {inserted_count}件")

        # 投入結果の確認
        result = await database.fetch_all("SELECT id, category, question FROM faq WHERE is_active = true ORDER BY display_order")

        print("\n📚 投入されたFAQデータ:")
        print("=" * 80)
        for row in result:
            print(f"  [{row['category']:12}] {row['question'][:60]}")
        print("=" * 80)
        print(f"\n✅ 合計: {len(result)}件のFAQデータが正常に投入されました\n")

        # データベース切断
        await disconnect_db()

    except Exception as e:
        logger.error(f"❌ FAQシードデータ投入エラー: {e}")
        await disconnect_db()
        raise


if __name__ == "__main__":
    print("🌱 Stock Harvest AI - FAQシードデータ投入スクリプト")
    print("=" * 80)
    asyncio.run(seed_faq_data())
