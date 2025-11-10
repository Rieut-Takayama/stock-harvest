#!/usr/bin/env python3
"""
安全なテスト実行スクリプト
本番データベースへの影響を防ぐテスト分離システムを使用
"""

import asyncio
import os
import sys
import subprocess
from typing import Optional

# プロジェクトルートを動的に取得
def get_project_root():
    """プロジェクトルートディレクトリを取得"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir

def setup_test_environment():
    """テスト実行環境をセットアップ"""
    project_root = get_project_root()
    sys.path.append(project_root)
    
    # 環境変数の確認
    env_path = os.path.join(os.path.dirname(project_root), '.env.local')
    if not os.path.exists(env_path):
        print(f"⚠️ 環境変数ファイルが見つかりません: {env_path}")
        print("   テストにはデータベース接続が必要です")
        return False
    
    print(f"✅ 環境設定確認完了")
    return True

async def run_test_with_isolation(test_path: str, description: str) -> bool:
    """分離されたテスト環境でテストを実行"""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        # テスト実行
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            test_path,
            "-v",
            "--tb=short",
            "-s"
        ], 
        cwd=get_project_root(),
        capture_output=False,  # リアルタイム出力を許可
        timeout=300  # 5分タイムアウト
        )
        
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            return True
        else:
            print(f"❌ {description} 失敗 (終了コード: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} タイムアウト")
        return False
    except Exception as e:
        print(f"💥 {description} 実行エラー: {e}")
        return False

async def cleanup_test_environment():
    """テスト環境の最終クリーンアップ"""
    try:
        # テストヘルパーのクリーンアップ関数を呼び出し
        from tests.utils.db_test_helper import cleanup_global_test_environment
        await cleanup_global_test_environment()
        print("✅ グローバルテスト環境クリーンアップ完了")
    except Exception as e:
        print(f"⚠️ クリーンアップエラー: {e}")

async def run_all_tests():
    """全テストを安全に実行"""
    print("🔬 Stock Harvest AI - 品質保証テストスイート")
    print("📋 本番データベース分離による安全なテスト実行")
    print("=" * 70)
    
    # 環境確認
    if not setup_test_environment():
        print("❌ テスト環境のセットアップに失敗しました")
        return False
    
    # 実行するテストのリスト
    test_cases = [
        {
            "path": "tests/integration/system/system_endpoints_test.py",
            "description": "システム基盤エンドポイントテスト"
        },
        {
            "path": "tests/integration/contact/contact_endpoints_test.py", 
            "description": "お問い合わせエンドポイントテスト"
        }
    ]
    
    # テスト実行統計
    passed = 0
    failed = 0
    
    try:
        # 各テストを実行
        for test_case in test_cases:
            success = await run_test_with_isolation(
                test_case["path"],
                test_case["description"]
            )
            
            if success:
                passed += 1
            else:
                failed += 1
        
        # テスト結果サマリー
        print("\n" + "=" * 70)
        print("📊 テスト結果サマリー")
        print(f"✅ 成功: {passed}")
        print(f"❌ 失敗: {failed}")
        print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "成功率: N/A")
        
        if failed == 0:
            print("\n🎉 すべてのテストが成功しました！")
            print("✨ 品質担保基準をクリアしています")
            return True
        else:
            print(f"\n⚠️ {failed}件のテストが失敗しました")
            print("🔍 失敗したテストを確認してください")
            return False
            
    except KeyboardInterrupt:
        print("\n⚡ テスト実行が中断されました")
        return False
    except Exception as e:
        print(f"\n💥 テストスイート実行エラー: {e}")
        return False
    finally:
        # 必ずクリーンアップを実行
        await cleanup_test_environment()

def main():
    """メイン実行関数"""
    print("🚀 テストスイート開始...")
    
    # APIサーバーの起動確認
    print("📡 APIサーバーの起動確認...")
    print("   FastAPIサーバーが http://localhost:8432 で起動していることを確認してください")
    print("   起動コマンド: cd backend && python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8432 --reload")
    
    # ユーザー確認を求める
    response = input("\n▶️ APIサーバーが起動していることを確認しましたか？ (y/n): ")
    if response.lower() not in ['y', 'yes', 'はい']:
        print("⏹️ APIサーバーを起動してから再実行してください")
        sys.exit(1)
    
    # 非同期テスト実行
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 致命的エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()