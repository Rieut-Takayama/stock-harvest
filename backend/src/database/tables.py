"""
データベーステーブル定義
Stock Harvest AI プロジェクト用
"""

from sqlalchemy import Table, Column, Integer, String, Text, Boolean, DateTime, Numeric, JSON
from sqlalchemy.sql import func
from .config import metadata

# システム情報テーブル
system_info = Table(
    'system_info',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('version', String(50), nullable=False, default='v1.0.0'),
    Column('status', String(20), nullable=False, default='healthy'),
    Column('last_scan_at', DateTime, nullable=True),
    Column('active_alerts', Integer, default=0),
    Column('total_users', Integer, default=0),
    Column('database_status', String(20), default='connected'),
    Column('last_updated', DateTime, server_default=func.now(), onupdate=func.now()),
    Column('status_display', String(100), default='正常稼働中'),
    Column('metadata_info', JSON, nullable=True)  # 追加のシステム情報用
)

# FAQ テーブル
faq = Table(
    'faq',
    metadata,
    Column('id', String(50), primary_key=True),
    Column('category', String(100), nullable=False),
    Column('question', Text, nullable=False),
    Column('answer', Text, nullable=False),
    Column('tags', JSON, nullable=True),  # 配列型でタグを保存
    Column('display_order', Integer, default=0),
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# アラート管理テーブル
alerts = Table(
    'alerts',
    metadata,
    Column('id', String(50), primary_key=True),  # "alert-" + ユニークID形式
    Column('stock_code', String(10), nullable=False),  # 銘柄コード（例: "7203"）
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('type', String(20), nullable=False),  # "price" または "logic"
    Column('condition', JSON, nullable=False),  # アラート条件（JSON形式）
    Column('is_active', Boolean, default=True),  # アラート有効フラグ
    Column('line_notification_enabled', Boolean, default=True),  # LINE通知有効フラグ
    Column('triggered_count', Integer, default=0),  # 発動回数
    Column('last_triggered_at', DateTime, nullable=True),  # 最後の発動時刻
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# LINE通知設定テーブル
line_notification_config = Table(
    'line_notification_config',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('is_connected', Boolean, default=False),  # LINE連携状態
    Column('token', String(255), nullable=True),  # LINEトークン（暗号化保存推奨）
    Column('status', String(20), default='disconnected'),  # "connected", "disconnected", "error"
    Column('last_notification_at', DateTime, nullable=True),  # 最後の通知送信時刻
    Column('notification_count', Integer, default=0),  # 通知送信回数
    Column('error_count', Integer, default=0),  # エラー発生回数
    Column('last_error_message', Text, nullable=True),  # 最後のエラーメッセージ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# お問い合わせテーブル（将来のお問い合わせ履歴管理用）
contact_inquiries = Table(
    'contact_inquiries',
    metadata,
    Column('id', String(50), primary_key=True),
    Column('type', String(20), nullable=False),  # 'technical', 'feature', 'bug', 'other'
    Column('subject', String(200), nullable=False),
    Column('content', Text, nullable=False),
    Column('email', String(255), nullable=False),
    Column('priority', String(10), default='medium'),  # 'low', 'medium', 'high'
    Column('status', String(20), default='open'),  # 'open', 'in_progress', 'closed'
    Column('created_at', DateTime, server_default=func.now()),
    Column('response_at', DateTime, nullable=True),
    Column('resolved_at', DateTime, nullable=True)
)

# スキャン実行履歴テーブル
scan_executions = Table(
    'scan_executions',
    metadata,
    Column('id', String(50), primary_key=True),  # "scan_" + タイムスタンプ形式
    Column('status', String(20), nullable=False, default='running'),  # "running", "completed", "failed"
    Column('progress', Integer, default=0),  # 進捗率 (0-100)
    Column('total_stocks', Integer, default=0),  # 総銘柄数
    Column('processed_stocks', Integer, default=0),  # 処理済み銘柄数
    Column('current_stock', String(10), nullable=True),  # 現在処理中の銘柄コード
    Column('estimated_time', Integer, nullable=True),  # 推定残り時間(秒)
    Column('message', String(255), default='スキャン実行中...'),  # ステータスメッセージ
    Column('logic_a_count', Integer, default=0),  # ロジックA検出数
    Column('logic_b_count', Integer, default=0),  # ロジックB検出数
    Column('error_message', Text, nullable=True),  # エラーメッセージ
    Column('started_at', DateTime, server_default=func.now()),
    Column('completed_at', DateTime, nullable=True)
)

# スキャン結果テーブル
scan_results = Table(
    'scan_results',
    metadata,
    Column('id', String(50), primary_key=True),
    Column('scan_id', String(50), nullable=False),  # scan_executions.idへの外部キー
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('price', Numeric(10, 2), nullable=False),  # 現在価格
    Column('change', Numeric(10, 2), nullable=False),  # 価格変動
    Column('change_rate', Numeric(5, 2), nullable=False),  # 変動率(%)
    Column('volume', Integer, nullable=False),  # 出来高
    Column('logic_type', String(10), nullable=False),  # "logic_a" または "logic_b"
    Column('technical_signals', JSON, nullable=True),  # テクニカル指標データ
    Column('market_cap', Numeric(20, 2), nullable=True),  # 時価総額
    Column('detected_at', DateTime, server_default=func.now())
)

# 銘柄マスタテーブル（yfinanceから取得した銘柄情報キャッシュ用）
stock_master = Table(
    'stock_master',
    metadata,
    Column('code', String(10), primary_key=True),  # 銘柄コード
    Column('name', String(100), nullable=False),  # 銘柄名
    Column('market', String(20), nullable=True),  # 市場（東証1部、2部等）
    Column('sector', String(100), nullable=True),  # 業種
    Column('is_active', Boolean, default=True),  # スキャン対象フラグ
    Column('last_updated', DateTime, server_default=func.now(), onupdate=func.now()),
    Column('metadata_info', JSON, nullable=True)  # 追加情報
)

# 手動決済シグナルテーブル
manual_signals = Table(
    'manual_signals',
    metadata,
    Column('id', String(50), primary_key=True),  # "signal-" + タイムスタンプ形式
    Column('signal_type', String(20), nullable=False),  # "stop_loss" または "take_profit"
    Column('stock_code', String(10), nullable=True),  # 銘柄コード（全体シグナルの場合null）
    Column('reason', Text, nullable=True),  # シグナル実行理由
    Column('status', String(20), default='pending'),  # "pending", "executed", "failed", "cancelled"
    Column('executed_at', DateTime, nullable=True),  # シグナル実行時刻
    Column('affected_positions', Integer, nullable=True),  # 影響を受けたポジション数
    Column('execution_result', JSON, nullable=True),  # 実行結果の詳細
    Column('error_message', Text, nullable=True),  # エラーメッセージ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# 上場日管理テーブル
listing_dates = Table(
    'listing_dates',
    metadata,
    Column('stock_code', String(10), primary_key=True),  # 銘柄コード
    Column('listing_date', DateTime, nullable=False),  # 上場日
    Column('market', String(20), nullable=False),  # 上場市場（Prime, Standard, Growth）
    Column('sector', String(100), nullable=True),  # 業種
    Column('company_name', String(200), nullable=False),  # 会社名
    Column('years_since_listing', Numeric(5, 2), nullable=True),  # 上場からの年数
    Column('is_target', Boolean, default=False),  # スキャン対象フラグ（2.5～5年以内）
    Column('data_source', String(50), default='jse'),  # データソース（jse: 日本取引所グループ）
    Column('last_updated', DateTime, server_default=func.now(), onupdate=func.now()),
    Column('created_at', DateTime, server_default=func.now()),
    Column('metadata_info', JSON, nullable=True)  # 追加情報（業績データ等）
)

# 制限値幅管理テーブル
price_limits = Table(
    'price_limits',
    metadata,
    Column('stock_code', String(10), primary_key=True),  # 銘柄コード
    Column('current_price', Numeric(10, 2), nullable=False),  # 基準価格
    Column('upper_limit', Numeric(10, 2), nullable=False),  # ストップ高価格
    Column('lower_limit', Numeric(10, 2), nullable=False),  # ストップ安価格
    Column('limit_stage', Integer, default=1),  # 値幅制限段階（1: 通常、2: 拡大等）
    Column('market_cap_range', String(20), nullable=True),  # 時価総額レンジ（Large, Mid, Small）
    Column('price_range', String(20), nullable=True),  # 価格帯（100円未満、100-500円等）
    Column('last_price_update', DateTime, nullable=True),  # 最終価格更新日時
    Column('calculation_method', String(50), default='standard'),  # 計算方式
    Column('is_suspended', Boolean, default=False),  # 売買停止フラグ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now()),
    Column('metadata_info', JSON, nullable=True)  # 計算詳細等の追加情報
)

# 株価データキャッシュテーブル（パフォーマンス最適化用）
stock_data_cache = Table(
    'stock_data_cache',
    metadata,
    Column('stock_code', String(10), primary_key=True),  # 銘柄コード
    Column('cache_date', DateTime, nullable=False),  # キャッシュ日付
    Column('price_data', JSON, nullable=False),  # 株価データ（OHLCV）
    Column('technical_indicators', JSON, nullable=True),  # テクニカル指標データ
    Column('volume_data', JSON, nullable=True),  # 出来高関連データ
    Column('fundamental_data', JSON, nullable=True),  # ファンダメンタル情報
    Column('data_quality', String(20), default='good'),  # データ品質（good, poor, missing）
    Column('fetch_attempts', Integer, default=1),  # 取得試行回数
    Column('last_error', Text, nullable=True),  # 最後のエラーメッセージ
    Column('expires_at', DateTime, nullable=False),  # キャッシュ有効期限
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# 銘柄フィルタ設定テーブル
stock_filters = Table(
    'stock_filters',
    metadata,
    Column('id', String(50), primary_key=True),  # フィルタID
    Column('filter_name', String(100), nullable=False),  # フィルタ名
    Column('filter_type', String(30), nullable=False),  # 'listing_period', 'market_cap', 'sector', 'custom'
    Column('criteria', JSON, nullable=False),  # フィルタ条件（JSON形式）
    Column('is_active', Boolean, default=True),  # アクティブフラグ
    Column('description', Text, nullable=True),  # フィルタ説明
    Column('target_count', Integer, nullable=True),  # 対象銘柄数（推定）
    Column('last_applied', DateTime, nullable=True),  # 最後の適用日時
    Column('created_by', String(50), default='system'),  # 作成者
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# 売買シグナル履歴テーブル
trading_signals = Table(
    'trading_signals',
    metadata,
    Column('id', String(50), primary_key=True),  # "signal-" + タイムスタンプ形式
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('signal_type', String(20), nullable=False),  # "BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"
    Column('signal_strength', Numeric(5, 1), nullable=False),  # シグナル強度（0-100）
    Column('confidence', Numeric(5, 3), nullable=False),  # 信頼度（0-1）
    Column('current_price', Numeric(10, 2), nullable=False),  # 現在価格
    Column('entry_price', Numeric(10, 2), nullable=True),  # エントリー推奨価格
    Column('profit_target', Numeric(10, 2), nullable=True),  # 利確目標価格
    Column('stop_loss', Numeric(10, 2), nullable=True),  # 損切り価格
    Column('risk_reward_ratio', Numeric(5, 2), nullable=True),  # リスク・リワード比率
    Column('recommended_shares', Integer, nullable=True),  # 推奨株数
    Column('position_value', Numeric(15, 2), nullable=True),  # ポジション価値
    Column('portfolio_exposure', Numeric(5, 4), nullable=True),  # ポートフォリオ露出度
    Column('component_scores', JSON, nullable=True),  # 構成要素スコア（ロジック、テクニカル等）
    Column('risk_assessment', JSON, nullable=True),  # リスク評価詳細
    Column('execution_notes', JSON, nullable=True),  # 実行時の注意事項
    Column('logic_results', JSON, nullable=True),  # ロジック検出結果詳細
    Column('technical_analysis', JSON, nullable=True),  # テクニカル分析結果
    Column('timeframe_analysis', JSON, nullable=True),  # マルチタイムフレーム分析
    Column('status', String(20), default='active'),  # "active", "executed", "cancelled", "expired"
    Column('is_executable', Boolean, default=False),  # 実行可能フラグ
    Column('expires_at', DateTime, nullable=True),  # シグナル有効期限
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# シグナル実行履歴テーブル
signal_executions = Table(
    'signal_executions',
    metadata,
    Column('id', String(50), primary_key=True),  # "execution-" + タイムスタンプ形式
    Column('signal_id', String(50), nullable=False),  # trading_signals.idへの外部キー
    Column('execution_type', String(20), nullable=False),  # "entry", "exit", "stop_loss", "take_profit"
    Column('executed_price', Numeric(10, 2), nullable=False),  # 実行価格
    Column('executed_shares', Integer, nullable=False),  # 実行株数
    Column('execution_cost', Numeric(15, 2), nullable=False),  # 実行コスト（手数料含む）
    Column('market_price', Numeric(10, 2), nullable=False),  # 実行時の市場価格
    Column('slippage', Numeric(10, 2), default=0),  # スリッページ（実行価格 - 想定価格）
    Column('execution_method', String(30), default='manual'),  # "manual", "auto", "stop_order"
    Column('execution_notes', Text, nullable=True),  # 実行時のメモ
    Column('profit_loss', Numeric(15, 2), nullable=True),  # 損益（決済時のみ）
    Column('profit_loss_rate', Numeric(5, 2), nullable=True),  # 損益率（決済時のみ）
    Column('holding_period', Integer, nullable=True),  # 保有期間（日数、決済時のみ）
    Column('status', String(20), default='completed'),  # "completed", "failed", "partial"
    Column('error_message', Text, nullable=True),  # エラーメッセージ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# シグナルパフォーマンス統計テーブル
signal_performance = Table(
    'signal_performance',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date', DateTime, nullable=False),  # 統計対象日
    Column('total_signals', Integer, default=0),  # 総シグナル数
    Column('buy_signals', Integer, default=0),  # 買いシグナル数
    Column('sell_signals', Integer, default=0),  # 売りシグナル数
    Column('executed_signals', Integer, default=0),  # 実行されたシグナル数
    Column('successful_trades', Integer, default=0),  # 成功取引数（利益が出た取引）
    Column('failed_trades', Integer, default=0),  # 失敗取引数（損失が出た取引）
    Column('win_rate', Numeric(5, 2), default=0),  # 勝率（%）
    Column('average_profit', Numeric(15, 2), default=0),  # 平均利益
    Column('average_loss', Numeric(15, 2), default=0),  # 平均損失
    Column('total_profit_loss', Numeric(15, 2), default=0),  # 総損益
    Column('max_profit', Numeric(15, 2), default=0),  # 最大利益
    Column('max_loss', Numeric(15, 2), default=0),  # 最大損失
    Column('max_drawdown', Numeric(5, 2), default=0),  # 最大ドローダウン（%）
    Column('profit_factor', Numeric(5, 2), default=0),  # プロフィットファクター
    Column('sharpe_ratio', Numeric(5, 3), nullable=True),  # シャープレシオ
    Column('average_holding_period', Numeric(5, 1), nullable=True),  # 平均保有期間（日）
    Column('signal_accuracy', Numeric(5, 2), default=0),  # シグナル精度（予想方向の的中率）
    Column('risk_adjusted_return', Numeric(5, 3), nullable=True),  # リスク調整後リターン
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# アラート履歴テーブル
alert_history = Table(
    'alert_history',
    metadata,
    Column('id', String(50), primary_key=True),  # "alert_history-" + タイムスタンプ形式
    Column('alert_id', String(50), nullable=False),  # alerts.idへの外部キー
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('alert_type', String(20), nullable=False),  # "price", "logic", "signal"
    Column('trigger_condition', JSON, nullable=False),  # 発動条件詳細
    Column('trigger_value', Numeric(10, 2), nullable=False),  # 発動時の値（価格等）
    Column('market_data', JSON, nullable=True),  # 発動時の市場データ
    Column('notification_sent', Boolean, default=False),  # 通知送信フラグ
    Column('notification_method', String(20), nullable=True),  # "line", "email", "push"
    Column('notification_status', String(20), default='pending'),  # "pending", "sent", "failed"
    Column('notification_error', Text, nullable=True),  # 通知エラーメッセージ
    Column('user_response', String(20), nullable=True),  # "acknowledged", "dismissed", "acted"
    Column('response_at', DateTime, nullable=True),  # ユーザー反応時刻
    Column('is_critical', Boolean, default=False),  # 重要アラートフラグ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# 決算スケジュールテーブル（四半期別）
earnings_schedule = Table(
    'earnings_schedule',
    metadata,
    Column('id', String(50), primary_key=True),  # "earnings-" + 銘柄コード + 決算期形式
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('fiscal_year', Integer, nullable=False),  # 会計年度
    Column('fiscal_quarter', String(10), nullable=False),  # 四半期 ('Q1', 'Q2', 'Q3', 'Q4', 'FY')
    Column('scheduled_date', DateTime, nullable=True),  # 決算発表予定日
    Column('actual_date', DateTime, nullable=True),  # 決算発表実績日
    Column('announcement_time', String(20), nullable=True),  # 発表時間帯 ('pre_market', 'after_market', 'trading_hours')
    Column('earnings_status', String(20), default='scheduled'),  # "scheduled", "announced", "delayed", "cancelled"
    Column('revenue_estimate', Numeric(20, 2), nullable=True),  # 売上予想（百万円）
    Column('profit_estimate', Numeric(20, 2), nullable=True),  # 経常利益予想（百万円）
    Column('revenue_actual', Numeric(20, 2), nullable=True),  # 売上実績（百万円）
    Column('profit_actual', Numeric(20, 2), nullable=True),  # 経常利益実績（百万円）
    Column('profit_previous', Numeric(20, 2), nullable=True),  # 前年同期経常利益（百万円）
    Column('is_black_ink_conversion', Boolean, default=False),  # 黒字転換フラグ
    Column('forecast_revision', JSON, nullable=True),  # 業績予想修正情報
    Column('earnings_summary', Text, nullable=True),  # 決算要旨・コメント
    Column('data_source', String(50), default='manual'),  # データソース ('irbank', 'kabutan', 'manual', 'api')
    Column('last_updated_from_source', DateTime, nullable=True),  # 外部ソースから最後更新日時
    Column('next_earnings_date', DateTime, nullable=True),  # 次回決算予定日（自動計算）
    Column('is_target_for_logic_b', Boolean, default=False),  # ロジックB対象フラグ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now()),
    Column('metadata_info', JSON, nullable=True)  # 追加情報（IRバンク・カブタン連携データ等）
)

# 売買履歴管理テーブル
trading_history = Table(
    'trading_history',
    metadata,
    Column('id', String(50), primary_key=True),  # "trade-" + タイムスタンプ形式
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('trade_type', String(10), nullable=False),  # "BUY", "SELL"
    Column('logic_type', String(20), nullable=True),  # "logic_a", "logic_b", "manual"
    Column('entry_price', Numeric(10, 2), nullable=False),  # エントリー価格
    Column('exit_price', Numeric(10, 2), nullable=True),  # 決済価格（売却時のみ）
    Column('quantity', Integer, nullable=False),  # 取引株数
    Column('total_cost', Numeric(15, 2), nullable=False),  # 総コスト（手数料含む）
    Column('commission', Numeric(10, 2), default=0),  # 手数料
    Column('profit_loss', Numeric(15, 2), nullable=True),  # 損益（決済時のみ）
    Column('profit_loss_rate', Numeric(5, 2), nullable=True),  # 損益率（決済時のみ）
    Column('holding_period', Integer, nullable=True),  # 保有期間（日数、決済時のみ）
    Column('trade_date', DateTime, nullable=False),  # 取引日時
    Column('settlement_date', DateTime, nullable=True),  # 決済日時
    Column('order_method', String(30), nullable=False),  # "market", "limit", "stop", "ifdoco"
    Column('target_profit', Numeric(10, 2), nullable=True),  # 利確目標価格
    Column('stop_loss', Numeric(10, 2), nullable=True),  # 損切り価格
    Column('risk_reward_ratio', Numeric(5, 2), nullable=True),  # リスクリワード比率
    Column('signal_id', String(50), nullable=True),  # 関連シグナルID（trading_signals.id）
    Column('scan_result_id', String(50), nullable=True),  # 関連スキャン結果ID（scan_results.id）
    Column('entry_reason', Text, nullable=True),  # エントリー理由
    Column('exit_reason', String(50), nullable=True),  # 決済理由 ("profit_target", "stop_loss", "manual", "time_limit")
    Column('market_conditions', JSON, nullable=True),  # 取引時の市場条件
    Column('performance_analysis', JSON, nullable=True),  # パフォーマンス分析結果
    Column('status', String(20), default='open'),  # "open", "closed", "cancelled"
    Column('notes', Text, nullable=True),  # 取引メモ
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# 銘柄アーカイブテーブル（過去合致銘柄の履歴保存）
stock_archive = Table(
    'stock_archive',
    metadata,
    Column('id', String(50), primary_key=True),  # "archive-" + タイムスタンプ形式
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('logic_type', String(20), nullable=False),  # "logic_a", "logic_b"
    Column('detection_date', DateTime, nullable=False),  # 検出日時
    Column('scan_id', String(50), nullable=False),  # scan_executions.idへの外部キー
    Column('price_at_detection', Numeric(10, 2), nullable=False),  # 検出時価格
    Column('volume_at_detection', Integer, nullable=False),  # 検出時出来高
    Column('market_cap_at_detection', Numeric(20, 2), nullable=True),  # 検出時時価総額
    Column('technical_signals_snapshot', JSON, nullable=True),  # 検出時テクニカル指標
    Column('logic_specific_data', JSON, nullable=True),  # ロジック固有データ（上場日、決算情報等）
    Column('performance_after_1d', Numeric(5, 2), nullable=True),  # 1日後パフォーマンス（%）
    Column('performance_after_1w', Numeric(5, 2), nullable=True),  # 1週間後パフォーマンス（%）
    Column('performance_after_1m', Numeric(5, 2), nullable=True),  # 1ヶ月後パフォーマンス（%）
    Column('max_gain', Numeric(5, 2), nullable=True),  # 最大利益（%）
    Column('max_loss', Numeric(5, 2), nullable=True),  # 最大損失（%）
    Column('outcome_classification', String(20), nullable=True),  # "success", "failure", "neutral", "pending"
    Column('manual_score', String(5), nullable=True),  # 手動スコア ('S', 'A+', 'A', 'B', 'C')
    Column('manual_score_reason', Text, nullable=True),  # 手動スコア理由
    Column('trade_execution', JSON, nullable=True),  # 実際の売買実行情報
    Column('lessons_learned', Text, nullable=True),  # 学習事項・改善点
    Column('market_conditions_snapshot', JSON, nullable=True),  # 検出時の市場全体状況
    Column('follow_up_notes', Text, nullable=True),  # フォローアップメモ
    Column('archive_status', String(20), default='active'),  # "active", "archived", "deleted"
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# 手動スコア評価テーブル（S,A+,A,B,C評価保存）
manual_scores = Table(
    'manual_scores',
    metadata,
    Column('id', String(50), primary_key=True),  # "score-" + タイムスタンプ形式
    Column('stock_code', String(10), nullable=False),  # 銘柄コード
    Column('stock_name', String(100), nullable=False),  # 銘柄名
    Column('score', String(5), nullable=False),  # スコア ('S', 'A+', 'A', 'B', 'C')
    Column('logic_type', String(20), nullable=False),  # "logic_a", "logic_b"
    Column('scan_result_id', String(50), nullable=True),  # 関連スキャン結果ID
    Column('evaluation_reason', Text, nullable=False),  # 評価理由
    Column('evaluated_by', String(100), default='user'),  # 評価者
    Column('evaluated_at', DateTime, server_default=func.now()),  # 評価日時
    Column('confidence_level', String(20), nullable=True),  # 確信度 ('high', 'medium', 'low')
    Column('price_at_evaluation', Numeric(10, 2), nullable=True),  # 評価時価格
    Column('market_context', JSON, nullable=True),  # 評価時の市場状況
    Column('ai_score_before', String(5), nullable=True),  # AI計算スコア（評価前）
    Column('ai_score_after', String(5), nullable=True),  # AI計算スコア（評価後）
    Column('score_change_history', JSON, nullable=True),  # スコア変更履歴
    Column('follow_up_required', Boolean, default=False),  # フォローアップ要否
    Column('follow_up_date', DateTime, nullable=True),  # フォローアップ予定日
    Column('performance_validation', JSON, nullable=True),  # パフォーマンス検証結果
    Column('tags', JSON, nullable=True),  # タグ（カテゴリ分類用）
    Column('is_learning_case', Boolean, default=False),  # 学習事例フラグ
    Column('status', String(20), default='active'),  # "active", "archived", "superseded"
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)

# Discord通知設定テーブル（WebhookURL管理）
discord_config = Table(
    'discord_config',
    metadata,
    Column('id', Integer, primary_key=True),  # 単一レコード想定
    Column('webhook_url', String(500), nullable=True),  # Discord WebhookURL
    Column('is_enabled', Boolean, default=False),  # Discord通知有効フラグ
    Column('channel_name', String(100), nullable=True),  # チャンネル名（表示用）
    Column('server_name', String(100), nullable=True),  # サーバー名（表示用）
    Column('notification_types', JSON, nullable=True),  # 通知タイプ設定 ['logic_a', 'logic_b', 'alerts', 'signals']
    Column('mention_role', String(100), nullable=True),  # メンション対象ロール
    Column('notification_format', String(20), default='standard'),  # "standard", "compact", "detailed"
    Column('rate_limit_per_hour', Integer, default=60),  # 1時間あたりの通知制限数
    Column('last_notification_at', DateTime, nullable=True),  # 最後の通知送信時刻
    Column('notification_count_today', Integer, default=0),  # 本日の通知送信回数
    Column('total_notifications_sent', Integer, default=0),  # 総通知送信回数
    Column('error_count', Integer, default=0),  # エラー発生回数
    Column('last_error_message', Text, nullable=True),  # 最後のエラーメッセージ
    Column('last_error_at', DateTime, nullable=True),  # 最後のエラー発生時刻
    Column('connection_status', String(20), default='disconnected'),  # "connected", "disconnected", "error"
    Column('webhook_test_result', JSON, nullable=True),  # WebhookURL接続テスト結果
    Column('custom_message_template', Text, nullable=True),  # カスタムメッセージテンプレート
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)