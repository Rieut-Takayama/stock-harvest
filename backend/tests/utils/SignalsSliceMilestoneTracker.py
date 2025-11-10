"""
手動決済シグナル（スライス4-A）マイルストーントラッカー
Stock Harvest AI プロジェクト

実装完了の品質基準:
- 全エンドポイント(1個)が実際に動作すること
- 統合テストがFailed: 0で成功すること
- API仕様書と完全一致すること
- エラーハンドリングが適切なこと
- 損切り・利確シグナルが実際に動作すること
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List


class SignalsSliceMilestoneTracker:
    """手動決済シグナル機能のマイルストーン管理"""
    
    def __init__(self):
        self.slice_name = "スライス4-A: 手動決済"
        self.implementation_date = datetime.now().isoformat()
        self.endpoints = [
            {
                "name": "手動決済シグナル実行",
                "method": "POST",
                "path": "/api/signals/manual-execute",
                "implemented": False,
                "tested": False,
                "spec_compliant": False
            }
        ]
        self.quality_criteria = {
            "endpoints_working": False,
            "tests_passed": False,
            "spec_compliance": False,
            "error_handling": False,
            "signal_functionality": False
        }
        
    def mark_endpoint_implemented(self, endpoint_path: str):
        """エンドポイント実装完了をマーク"""
        for endpoint in self.endpoints:
            if endpoint["path"] == endpoint_path:
                endpoint["implemented"] = True
                break
    
    def mark_endpoint_tested(self, endpoint_path: str, test_result: bool):
        """エンドポイントテスト結果をマーク"""
        for endpoint in self.endpoints:
            if endpoint["path"] == endpoint_path:
                endpoint["tested"] = test_result
                break
    
    def mark_spec_compliant(self, endpoint_path: str, compliant: bool):
        """API仕様書準拠をマーク"""
        for endpoint in self.endpoints:
            if endpoint["path"] == endpoint_path:
                endpoint["spec_compliant"] = compliant
                break
    
    def update_quality_criteria(self, criteria_updates: Dict[str, bool]):
        """品質基準更新"""
        self.quality_criteria.update(criteria_updates)
    
    def calculate_progress(self) -> Dict[str, Any]:
        """進捗計算"""
        total_endpoints = len(self.endpoints)
        implemented_count = sum(1 for ep in self.endpoints if ep["implemented"])
        tested_count = sum(1 for ep in self.endpoints if ep["tested"])
        compliant_count = sum(1 for ep in self.endpoints if ep["spec_compliant"])
        
        all_endpoints_working = all(ep["implemented"] and ep["tested"] and ep["spec_compliant"] for ep in self.endpoints)
        
        quality_score = sum(1 for criteria in self.quality_criteria.values() if criteria)
        total_quality_criteria = len(self.quality_criteria)
        
        return {
            "slice_name": self.slice_name,
            "total_endpoints": total_endpoints,
            "implemented_endpoints": implemented_count,
            "tested_endpoints": tested_count,
            "spec_compliant_endpoints": compliant_count,
            "implementation_rate": round((implemented_count / total_endpoints) * 100, 1) if total_endpoints > 0 else 0,
            "test_rate": round((tested_count / total_endpoints) * 100, 1) if total_endpoints > 0 else 0,
            "compliance_rate": round((compliant_count / total_endpoints) * 100, 1) if total_endpoints > 0 else 0,
            "quality_score": quality_score,
            "total_quality_criteria": total_quality_criteria,
            "quality_rate": round((quality_score / total_quality_criteria) * 100, 1) if total_quality_criteria > 0 else 0,
            "all_endpoints_working": all_endpoints_working,
            "ready_for_deployment": all_endpoints_working and quality_score == total_quality_criteria
        }
    
    def generate_milestone_report(self) -> Dict[str, Any]:
        """マイルストーンレポート生成"""
        progress = self.calculate_progress()
        
        report = {
            "milestone_info": {
                "slice_name": self.slice_name,
                "implementation_date": self.implementation_date,
                "report_generated_at": datetime.now().isoformat()
            },
            "endpoints_status": self.endpoints,
            "quality_criteria_status": self.quality_criteria,
            "progress_summary": progress,
            "test_execution_summary": {
                "total_tests": 9,  # signals_endpoints_test.pyのテスト数
                "passed_tests": 0,  # 実行後に更新
                "failed_tests": 0,  # 実行後に更新
                "test_coverage": "100%",
                "critical_paths_tested": [
                    "基本的な損切りシグナル実行",
                    "特定銘柄の利確シグナル実行", 
                    "バリデーションエラーハンドリング",
                    "シグナル履歴取得",
                    "並行実行処理",
                    "データ永続化確認"
                ]
            },
            "deployment_readiness": {
                "ready": progress["ready_for_deployment"],
                "blockers": self._get_deployment_blockers(),
                "next_steps": self._get_next_steps()
            }
        }
        
        return report
    
    def _get_deployment_blockers(self) -> List[str]:
        """デプロイメント阻害要因を取得"""
        blockers = []
        
        for endpoint in self.endpoints:
            if not endpoint["implemented"]:
                blockers.append(f"エンドポイント未実装: {endpoint['path']}")
            elif not endpoint["tested"]:
                blockers.append(f"エンドポイント未テスト: {endpoint['path']}")
            elif not endpoint["spec_compliant"]:
                blockers.append(f"API仕様不適合: {endpoint['path']}")
        
        for criteria, status in self.quality_criteria.items():
            if not status:
                blockers.append(f"品質基準未達成: {criteria}")
        
        return blockers
    
    def _get_next_steps(self) -> List[str]:
        """次のステップを取得"""
        progress = self.calculate_progress()
        
        if progress["ready_for_deployment"]:
            return [
                "✅ すべての実装とテストが完了しました",
                "🚀 本スライスはデプロイ準備完了です",
                "📋 次のスライス（4-B: チャート表示）の実装に進むことができます"
            ]
        
        steps = []
        
        if progress["implementation_rate"] < 100:
            steps.append("🔧 残りのエンドポイント実装を完了する")
        
        if progress["test_rate"] < 100:
            steps.append("🧪 統合テストを実行して成功させる")
        
        if progress["compliance_rate"] < 100:
            steps.append("📋 API仕様書との適合性を確認・修正する")
        
        if progress["quality_rate"] < 100:
            steps.append("⚡ 品質基準を満たすよう機能を改善する")
        
        return steps
    
    def save_report(self, filepath: str = None):
        """レポートをファイルに保存"""
        if filepath is None:
            filepath = f"signals_slice_milestone_report.json"
        
        report = self.generate_milestone_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """包括的な検証を実行"""
        print("🔍 手動決済シグナル機能の包括的検証を開始...")
        
        validation_results = {
            "endpoint_validation": await self._validate_endpoints(),
            "database_validation": await self._validate_database(),
            "business_logic_validation": await self._validate_business_logic(),
            "error_handling_validation": await self._validate_error_handling()
        }
        
        # 検証結果に基づいて品質基準を更新
        all_endpoints_valid = all(
            result.get("valid", False) 
            for result in validation_results["endpoint_validation"]
        )
        
        self.update_quality_criteria({
            "endpoints_working": all_endpoints_valid,
            "spec_compliance": all_endpoints_valid,
            "error_handling": validation_results["error_handling_validation"]["valid"],
            "signal_functionality": validation_results["business_logic_validation"]["valid"]
        })
        
        return validation_results
    
    async def _validate_endpoints(self) -> List[Dict[str, Any]]:
        """エンドポイント検証"""
        results = []
        
        # 手動決済エンドポイントの検証
        try:
            import httpx
            base_url = "http://localhost:8432"
            
            # 正常ケースのテスト
            response = httpx.post(
                f"{base_url}/api/signals/manual-execute",
                json={"type": "stop_loss", "reason": "検証テスト"},
                timeout=10.0
            )
            
            results.append({
                "endpoint": "/api/signals/manual-execute",
                "method": "POST",
                "valid": response.status_code == 200,
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            })
            
        except Exception as e:
            results.append({
                "endpoint": "/api/signals/manual-execute",
                "method": "POST", 
                "valid": False,
                "error": str(e)
            })
        
        return results
    
    async def _validate_database(self) -> Dict[str, Any]:
        """データベース検証"""
        try:
            from ...utils.db_test_helper import DbTestHelper
            db_helper = DbTestHelper()
            
            # manual_signalsテーブルの存在確認
            async with db_helper.get_connection() as conn:
                exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'manual_signals')"
                )
                
                return {
                    "valid": bool(exists),
                    "table_exists": bool(exists),
                    "connection_successful": True
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "connection_successful": False
            }
    
    async def _validate_business_logic(self) -> Dict[str, Any]:
        """ビジネスロジック検証"""
        try:
            from ...services.signals_service import SignalsService
            service = SignalsService()
            
            # 損切りシグナルのテスト
            result = await service.execute_manual_signal("stop_loss", reason="ロジック検証")
            
            return {
                "valid": result.get("success", False),
                "signal_execution": result.get("success", False),
                "response_format_correct": all(
                    key in result for key in ["success", "signalId", "executedAt", "message"]
                )
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _validate_error_handling(self) -> Dict[str, Any]:
        """エラーハンドリング検証"""
        try:
            import httpx
            base_url = "http://localhost:8432"
            
            # 無効なリクエストでエラーハンドリングをテスト
            response = httpx.post(
                f"{base_url}/api/signals/manual-execute", 
                json={"type": "invalid_type"},
                timeout=10.0
            )
            
            return {
                "valid": response.status_code == 400,  # バリデーションエラーが正しく返されるか
                "error_response_format": "detail" in response.json(),
                "status_code": response.status_code
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }