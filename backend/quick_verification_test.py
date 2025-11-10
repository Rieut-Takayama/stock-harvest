#!/usr/bin/env python3
"""
Quick Verification Test
軽微修正後の迅速検証テスト
"""

import asyncio
import httpx
import json
import time

BASE_URL = "http://localhost:8432"
TEST_TIMEOUT = 30.0

async def quick_verification():
    """迅速検証テスト実行"""
    print("🔍 Quick Verification Test - 軽微修正後検証")
    print("=" * 50)
    
    results = {'passed': 0, 'total': 0, 'details': []}
    
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        
        # 1. 全主要エンドポイントのクイックテスト
        test_endpoints = [
            ('GET', '/api/system/info', None, 'システム情報'),
            ('GET', '/api/system/status', None, 'システムステータス'), 
            ('GET', '/api/alerts', None, 'アラート一覧'),
            ('GET', '/api/contact/faq', None, 'FAQ一覧'),
            ('POST', '/api/contact/submit', {
                'type': 'general', 'subject': 'クイックテスト', 
                'content': '検証用', 'email': 'quick@test.com', 'priority': 'medium'
            }, 'お問い合わせ'),
            ('POST', '/api/signals/manual-execute', {
                'type': 'stop_loss', 'stockCode': '7203', 'reason': '検証用決済'
            }, '手動決済'),
            ('GET', '/api/charts/data/7203?timeframe=1d&period=5d', None, 'チャートデータ'),
        ]
        
        for method, endpoint, data, description in test_endpoints:
            results['total'] += 1
            try:
                start_time = time.time()
                
                if method == 'GET':
                    response = await client.get(f"{BASE_URL}{endpoint}")
                elif method == 'POST':
                    response = await client.post(
                        f"{BASE_URL}{endpoint}", 
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )
                
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 201]:
                    results['passed'] += 1
                    status = "✅ PASS"
                    details = f"{response_time:.1f}ms"
                else:
                    status = "❌ FAIL"
                    details = f"HTTP {response.status_code}"
                    
                results['details'].append({
                    'description': description,
                    'status': status,
                    'details': details
                })
                
                print(f"{description}: {status} ({details})")
                
            except Exception as e:
                status = "❌ ERROR"
                results['details'].append({
                    'description': description,
                    'status': status,
                    'details': str(e)
                })
                print(f"{description}: {status} ({e})")
        
        # 2. エンドポイント間連携テスト
        results['total'] += 1
        try:
            print("\n🔗 エンドポイント間連携テスト")
            
            # チャートデータ取得 → 手動決済の流れ
            chart_response = await client.get(f"{BASE_URL}/api/charts/data/7203")
            assert chart_response.status_code == 200
            
            chart_data = chart_response.json()
            current_price = chart_data.get('currentPrice', {}).get('price', 3000)
            
            execute_response = await client.post(
                f"{BASE_URL}/api/signals/manual-execute",
                json={
                    'type': 'take_profit',
                    'stockCode': '7203', 
                    'reason': f'連携テスト用決済: {current_price}円'
                }
            )
            assert execute_response.status_code == 200
            
            results['passed'] += 1
            print("エンドポイント間連携: ✅ PASS")
            
        except Exception as e:
            print(f"エンドポイント間連携: ❌ FAIL ({e})")
        
        # 3. 結果サマリー
        success_rate = (results['passed'] / results['total']) * 100
        print("\n" + "=" * 50)
        print(f"🎯 クイック検証結果: {results['passed']}/{results['total']} PASSED ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🏆 品質レベル: EXCELLENT - 本番投入準備完了")
        elif success_rate >= 80:
            print("✨ 品質レベル: GOOD - 本番投入可能")
        elif success_rate >= 70:
            print("👍 品質レベル: ACCEPTABLE - 条件付き本番投入可")
        else:
            print("⚠️ 品質レベル: NEEDS_IMPROVEMENT - 追加修正必要")
            
        return success_rate >= 80

async def main():
    """メイン実行"""
    success = await quick_verification()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n{'🎉 SUCCESS' if result else '❌ FAILED'}: Quick Verification {'完了' if result else '要改善'}")
    exit(0 if result else 1)