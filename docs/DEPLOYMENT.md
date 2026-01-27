# デプロイ設定

## 推奨構成（2026-01-21時点）

- **フロントエンド**: Vercel（無料プランで十分）
- **バックエンド**: Railway（無料$5クレジット）
- **データベース**: Neon PostgreSQL（無料プラン0.5GB）

## 代替構成

- **フロントエンド**: Netlify（Vercelの代替）
- **バックエンド**: Render（Railwayの代替）

## 設定ファイル一覧

| ファイル | プラットフォーム | 用途 |
|---------|--------------|------|
| vercel.json | Vercel | フロントエンドデプロイ |
| netlify.toml | Netlify | フロントエンド代替 |
| railway.json | Railway | バックエンドデプロイ |
| render.yaml | Render | バックエンド代替 |

## 環境変数設定

全プラットフォーム共通で以下の環境変数が必要です:

### バックエンド
- `DATABASE_URL`: PostgreSQL接続文字列（Neon提供）
- `LINE_NOTIFY_TOKEN`: LINE通知用トークン（オプション）
- `OPENAI_API_KEY`: OpenAI APIキー（オプション）

### フロントエンド
- `VITE_API_BASE_URL`: バックエンドAPIのURL（例: https://api.example.com）

## デプロイ手順（Vercel + Railway）

### 1. フロントエンド（Vercel）

1. Vercelアカウント作成: https://vercel.com/signup
2. GitHubリポジトリ連携
3. プロジェクト設定:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. 環境変数設定:
   - `VITE_API_BASE_URL`: バックエンドURL
5. デプロイ

### 2. バックエンド（Railway）

1. Railwayアカウント作成: https://railway.app/
2. GitHubリポジトリ連携
3. プロジェクト設定:
   - Root Directory: `backend`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. 環境変数設定:
   - `DATABASE_URL`: Neon PostgreSQL接続文字列
   - `LINE_NOTIFY_TOKEN`: LINEトークン
5. デプロイ

### 3. データベース（Neon PostgreSQL）

1. Neonアカウント作成: https://neon.tech/
2. プロジェクト作成
3. データベース接続文字列をコピー
4. Railwayの環境変数`DATABASE_URL`に設定

## ローカル開発環境

### 環境変数設定

`.env.local` ファイルをプロジェクトルートに作成:

```env
# バックエンド
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
LINE_NOTIFY_TOKEN=your_line_token_here
OPENAI_API_KEY=your_openai_key_here

# フロントエンド
VITE_API_BASE_URL=http://localhost:8432
```

### 起動コマンド

```bash
# バックエンド起動
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8432

# フロントエンド起動
cd frontend
npm run dev  # ポート: 3247
```

## トラブルシューティング

### Vercel: ビルドエラー
- Node.jsバージョンを18.x以上に設定
- `vercel.json`の`framework`設定を確認

### Railway: 起動エラー
- `Procfile`または`railway.json`のコマンドを確認
- 環境変数`DATABASE_URL`が正しく設定されているか確認

### Neon: 接続エラー
- SSL接続を有効化: `?sslmode=require`
- IPアドレス制限を確認

---

## 本番環境デプロイ実績（2026-01-27）

### デプロイ完了

**本番環境URL:**
- フロントエンド: https://frontend-kkmg5cxlo-rieuts-projects.vercel.app
- バックエンド: https://stock-harvest-backend.onrender.com
- データベース: Neon PostgreSQL (ap-southeast-1)

**使用プラットフォーム:**
- フロントエンド: Vercel（無料プラン）
- バックエンド: Render（無料プラン）
- データベース: Neon PostgreSQL（無料プラン）

**完了日時:** 2026-01-27 19:15

### デプロイ時の注意事項

**依存関係の追加が必要:**
以下のパッケージがrequirements.txtに不足していたため追加:
- `aiohttp==3.9.1` (非同期HTTP通信)
- `email-validator==2.1.0` (Pydantic EmailStr用)
- `apscheduler==3.10.4` (バッチスケジューラ)

**Python バージョン:**
- Render free tierでは Python 3.11.9 を使用
- `runtime.txt` で明示的に指定が必要
- Python 3.13.x は依存関係のビルドエラーが発生

**環境変数設定（Render）:**
- `CORS_ORIGIN`: フロントエンドURL
- `FRONTEND_URL`: フロントエンドURL
- `DATABASE_URL`: Neon接続文字列
- `JWT_SECRET`, `SESSION_SECRET`: 認証用シークレット
- `PYTHON_VERSION=3.11.9`: Python バージョン指定

**環境変数設定（Vercel）:**
- `VITE_API_BASE_URL`: バックエンドURL

**データベース初期化:**
デプロイ後、以下のコマンドで初期化:
```bash
cd backend
DATABASE_URL="<production_url>" python3 -m src.database.migrate
```

---

作成日: 2026-01-21
最終更新: 2026-01-27
