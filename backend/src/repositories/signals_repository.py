"""
手動決済シグナル - リポジトリ層
Stock Harvest AI プロジェクト
"""

import asyncio
import asyncpg
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..database.config import database
from ..database.tables import manual_signals


class SignalsRepository:
    """手動決済シグナルのデータベース操作を担当するリポジトリ"""

    async def create_signal(
        self,
        signal_id: str,
        signal_type: str,
        stock_code: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        新しい手動決済シグナルを作成
        
        Args:
            signal_id: シグナルID
            signal_type: シグナルタイプ ("stop_loss" または "take_profit")
            stock_code: 銘柄コード（オプション）
            reason: シグナル実行理由（オプション）
            
        Returns:
            作成されたシグナル情報
        """
        query = """
            INSERT INTO manual_signals 
            (id, signal_type, stock_code, reason, status, created_at, updated_at)
            VALUES (:signal_id, :signal_type, :stock_code, :reason, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING *
        """
        
        row = await database.fetch_one(
            query, {
                "signal_id": signal_id,
                "signal_type": signal_type, 
                "stock_code": stock_code,
                "reason": reason
            }
        )
        
        if row:
            return dict(row)
        else:
            raise Exception("Failed to create manual signal")

    async def update_signal_status(
        self,
        signal_id: str,
        status: str,
        executed_at: Optional[datetime] = None,
        affected_positions: Optional[int] = None,
        execution_result: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        シグナルの実行状況を更新
        
        Args:
            signal_id: シグナルID
            status: 新しいステータス
            executed_at: 実行時刻
            affected_positions: 影響を受けたポジション数
            execution_result: 実行結果詳細
            error_message: エラーメッセージ
            
        Returns:
            更新されたシグナル情報
        """
        query = """
            UPDATE manual_signals 
            SET status = :status,
                executed_at = :executed_at,
                affected_positions = :affected_positions,
                execution_result = :execution_result,
                error_message = :error_message,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :signal_id
            RETURNING *
        """
        
        # JSONをJSONBに変換する際の処理
        import json
        execution_result_json = json.dumps(execution_result) if execution_result else None
        
        row = await database.fetch_one(
            query, {
                "signal_id": signal_id,
                "status": status,
                "executed_at": executed_at,
                "affected_positions": affected_positions,
                "execution_result": execution_result_json,
                "error_message": error_message
            }
        )
        
        if row:
            return dict(row)
        else:
            raise Exception(f"Manual signal with ID {signal_id} not found")

    async def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        IDによるシグナル情報取得
        
        Args:
            signal_id: シグナルID
            
        Returns:
            シグナル情報（見つからない場合はNone）
        """
        query = "SELECT * FROM manual_signals WHERE id = :signal_id"
        row = await database.fetch_one(query, {"signal_id": signal_id})
        
        if row:
            return dict(row)
        return None

    async def get_recent_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        最近のシグナル履歴を取得
        
        Args:
            limit: 取得件数制限
            
        Returns:
            シグナル履歴のリスト
        """
        query = """
            SELECT * FROM manual_signals 
            ORDER BY created_at DESC 
            LIMIT :limit
        """
        rows = await database.fetch_all(query, {"limit": limit})
        
        return [dict(row) for row in rows]

    async def get_pending_signals(self) -> List[Dict[str, Any]]:
        """
        実行待ちのシグナルを取得
        
        Returns:
            実行待ちシグナルのリスト
        """
        query = """
            SELECT * FROM manual_signals 
            WHERE status = 'pending'
            ORDER BY created_at ASC
        """
        rows = await database.fetch_all(query)
        
        return [dict(row) for row in rows]