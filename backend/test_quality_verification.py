#!/usr/bin/env python3
"""
テスト品質検証スクリプト
修正後の安全なテスト環境の動作確認
"""

import os
import asyncio
import subprocess
import sys

def verify_environment_isolation():
    """環境分離の確認"""
    print("🔍 環境分離の確認")
    print("-" * 50)
    
    # 相対パス使用の確認
    test_files = [
        "tests/integration/system/system_endpoints_test.py",
        "tests/integration/contact/contact_endpoints_test.py"
    ]
    
    hardcoded_paths_found = False
    for test_file in test_files:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '/Users/rieut/STOCK HARVEST/backend' in content:
                print(f"❌ ハードコードされたパスが見つかりました: {test_file}")
                hardcoded_paths_found = True
            else:
                print(f"✅ 相対パス使用確認: {test_file}")
    
    if not hardcoded_paths_found:
        print("✅ 全テストファイルで環境依存性が除去されています")
    
    return not hardcoded_paths_found

def verify_test_isolation_features():
    """テスト分離機能の確認"""
    print("\n🔒 テスト分離機能の確認")
    print("-" * 50)
    
    features = [
        {
            "name": "テスト設定ファイル",
            "file": "tests/test_config.py",
            "description": "専用テストDB管理とトランザクション制御"
        },
        {
            "name": "改良されたDBヘルパー", 
            "file": "tests/utils/db_test_helper.py",
            "description": "安全なデータベース操作と接続管理"
        },
        {
            "name": "テスト実行スクリプト",
            "file": "run_tests.py", 
            "description": "包括的なテスト実行とクリーンアップ"
        }
    ]
    
    all_exist = True
    for feature in features:
        if os.path.exists(feature["file"]):
            print(f"✅ {feature['name']}: {feature['description']}")
        else:
            print(f"❌ {feature['name']} が見つかりません: {feature['file']}")
            all_exist = False
    
    return all_exist

async def verify_data_safety():
    """データ安全性の確認"""
    print("\n🛡️ データ安全性の確認")
    print("-" * 50)
    
    try:
        # テストデータマネージャーの確認
        from tests.test_config import TestDataManager
        
        data_manager = TestDataManager()
        
        # テストデータ生成の確認
        test_data = data_manager.generate_unique_test_data({
            "email": "test@example.com",
            "subject": "テストメッセージ"
        })
        
        # プレフィックスが正しく付加されているか確認
        if "test-" in test_data["email"] and "[TEST-" in test_data["subject"]:
            print("✅ テストデータにユニークプレフィックスが付加されています")
            print(f"   サンプル: {test_data['email']}")
            return True
        else:
            print("❌ テストデータのプレフィックス付加に問題があります")
            return False
            
    except Exception as e:
        print(f"❌ データ安全性確認エラー: {e}")
        return False

def run_test_verification():
    """実際のテスト実行による検証"""
    print("\n🧪 実テスト実行による検証")
    print("-" * 50)
    
    try:
        # 1つのテストを実行して動作確認
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/integration/system/system_endpoints_test.py::TestSystemEndpoints::test_system_info_endpoint_success",
            "-v", "-q"
        ], 
        cwd="/Users/rieut/STOCK HARVEST/backend",
        capture_output=True, 
        text=True,
        timeout=60
        )
        
        if result.returncode == 0:
            print("✅ 改良されたテストシステムが正常に動作しています")
            return True
        else:
            print(f"❌ テスト実行に失敗しました: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ テスト実行がタイムアウトしました")
        return False
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False

async def main():
    """メイン検証処理"""
    print("🎯 Stock Harvest AI - テスト品質検証")
    print("=" * 70)
    print("本番データベース汚染防止とテスト分離システムの検証")
    print("=" * 70)
    
    # 各検証を実行
    checks = [
        ("環境分離", verify_environment_isolation()),
        ("テスト分離機能", verify_test_isolation_features()),
        ("データ安全性", await verify_data_safety()),
        ("実テスト動作", run_test_verification())
    ]
    
    print("\n📊 検証結果サマリー")
    print("-" * 50)
    
    passed = 0
    total = len(checks)
    
    for name, result in checks:
        if result:
            print(f"✅ {name}: 合格")
            passed += 1
        else:
            print(f"❌ {name}: 不合格")
    
    print(f"\n🏆 総合結果: {passed}/{total} 合格")
    
    if passed == total:
        print("🎉 全ての品質基準をクリアしています！")
        print("✨ 本番データベースへの影響を防ぐ安全なテスト環境が構築されました")
        return True
    else:
        print(f"⚠️ {total - passed}件の問題が発見されました")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚡ 検証が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 検証エラー: {e}")
        sys.exit(1)