Stock Harvest AI - ローカル実行手順

## 🚀 完全版ローカル起動（実データ対応）

### 1. バックエンド起動
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8432

### 2. フロントエンド起動  
cd frontend  
npm run dev

### 3. アクセス
- フロントエンド: http://localhost:3247
- バックエンドAPI: http://localhost:8432/docs

## 🔥 実機能
✅ ロジックA強化版: ストップ高張り付き精密検出
✅ ロジックB強化版: 黒字転換銘柄精密検出  
✅ 実データAPI: Yahoo Finance API（20分遅延）
✅ 全銘柄スキャン: 東証3,800銘柄対応
✅ アラート機能: LINE・Discord通知
✅ チャート表示: 実株価チャート

## 📊 使用方法
1. ダッシュボード → 「全銘柄スキャン実行」
2. ロジックA/B結果を確認 → 投資判断
3. アラート設定 → 価格・合致通知

## 🌐 他者利用
同じWiFi内の他PCから以下でアクセス可能:
http://[あなたのローカルIP]:3247

完全無料・実データ対応・投資判断支援完了！

