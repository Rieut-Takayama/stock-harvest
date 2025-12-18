"""
システム関連のバリデーター
入力データの検証ルール定義
"""

from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import re
from ..lib.logger import logger


class SystemValidator:
    """
    システム関連データのバリデーター
    """
    
    @staticmethod
    def validate_system_info(data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        システム情報データのバリデーション
        
        Args:
            data: バリデーション対象のデータ
        
        Returns:
            Tuple[bool, Optional[Dict[str, str]]]: (有効性, エラー詳細)
        """
        errors = {}
        
        try:
            # 必須フィールドのチェック
            required_fields = [
                'version', 'status', 'lastScanAt', 'activeAlerts',
                'totalUsers', 'databaseStatus', 'lastUpdated', 'statusDisplay'
            ]
            
            for field in required_fields:
                if field not in data:
                    errors[field] = f"{field}は必須フィールドです"
                elif data[field] is None:
                    errors[field] = f"{field}は空にできません"
            
            # バージョン形式のチェック
            if 'version' in data and data['version']:
                if not SystemValidator._validate_version_format(data['version']):
                    errors['version'] = "バージョンは 'v' で始まる形式である必要があります (例: v1.0.0)"
            
            # ステータス値のチェック
            if 'status' in data and data['status']:
                valid_statuses = ['healthy', 'degraded', 'down']
                if data['status'] not in valid_statuses:
                    errors['status'] = f"ステータスは {valid_statuses} のいずれかである必要があります"
            
            # データベースステータスのチェック
            if 'databaseStatus' in data and data['databaseStatus']:
                valid_db_statuses = ['connected', 'disconnected']
                if data['databaseStatus'] not in valid_db_statuses:
                    errors['databaseStatus'] = f"データベースステータスは {valid_db_statuses} のいずれかである必要があります"
            
            # 数値フィールドのチェック
            numeric_fields = ['activeAlerts', 'totalUsers']
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    if not isinstance(data[field], int) or data[field] < 0:
                        errors[field] = f"{field}は0以上の整数である必要があります"
            
            # 日時フィールドのチェック
            datetime_fields = ['lastScanAt', 'lastUpdated']
            for field in datetime_fields:
                if field in data and data[field] and data[field] != "未実行":
                    if not SystemValidator._validate_datetime_format(data[field]):
                        errors[field] = f"{field}はISO 8601形式の日時である必要があります"
            
            # ステータス表示テキストの長さチェック
            if 'statusDisplay' in data and data['statusDisplay']:
                if len(data['statusDisplay']) > 100:
                    errors['statusDisplay'] = "ステータス表示は100文字以下である必要があります"
            
            is_valid = len(errors) == 0
            logger.debug(f"システム情報バリデーション結果", {
                'is_valid': is_valid,
                'error_count': len(errors),
                'errors': errors if errors else None
            })
            
            return is_valid, errors if errors else None
            
        except Exception as e:
            logger.error(f"システム情報バリデーション中にエラーが発生", {'error': str(e)})
            return False, {'validation_error': f"バリデーション処理中にエラーが発生しました: {str(e)}"}
    
    @staticmethod
    def validate_health_check_response(data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        ヘルスチェックレスポンスのバリデーション
        
        Args:
            data: バリデーション対象のデータ
        
        Returns:
            Tuple[bool, Optional[Dict[str, str]]]: (有効性, エラー詳細)
        """
        errors = {}
        
        try:
            # 必須フィールドのチェック
            required_fields = ['healthy', 'status', 'timestamp']
            for field in required_fields:
                if field not in data:
                    errors[field] = f"{field}は必須フィールドです"
                elif data[field] is None:
                    errors[field] = f"{field}は空にできません"
            
            # healthyフィールドのブール値チェック
            if 'healthy' in data and data['healthy'] is not None:
                if not isinstance(data['healthy'], bool):
                    errors['healthy'] = "healthyはブール値である必要があります"
            
            # ステータスの妥当性チェック
            if 'status' in data and data['status']:
                valid_statuses = ['healthy', 'unhealthy']
                if data['status'] not in valid_statuses:
                    errors['status'] = f"ステータスは {valid_statuses} のいずれかである必要があります"
            
            # タイムスタンプのフォーマットチェック
            if 'timestamp' in data and data['timestamp']:
                if not SystemValidator._validate_datetime_format(data['timestamp']):
                    errors['timestamp'] = "タイムスタンプはISO 8601形式である必要があります"
            
            # チェック項目の検証
            if 'checks' in data and data['checks']:
                if not isinstance(data['checks'], dict):
                    errors['checks'] = "checksは辞書形式である必要があります"
                else:
                    for check_name, check_data in data['checks'].items():
                        check_errors = SystemValidator._validate_health_check_item(check_name, check_data)
                        if check_errors:
                            errors[f'checks.{check_name}'] = check_errors
            
            # 重要度レベルのチェック
            if 'severity' in data and data['severity']:
                valid_severities = ['info', 'warning', 'error']
                if data['severity'] not in valid_severities:
                    errors['severity'] = f"重要度は {valid_severities} のいずれかである必要があります"
            
            is_valid = len(errors) == 0
            logger.debug(f"ヘルスチェックレスポンスバリデーション結果", {
                'is_valid': is_valid,
                'error_count': len(errors),
                'errors': errors if errors else None
            })
            
            return is_valid, errors if errors else None
            
        except Exception as e:
            logger.error(f"ヘルスチェックバリデーション中にエラーが発生", {'error': str(e)})
            return False, {'validation_error': f"バリデーション処理中にエラーが発生しました: {str(e)}"}
    
    @staticmethod
    def validate_system_status_update(data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        システムステータス更新データのバリデーション
        
        Args:
            data: バリデーション対象のデータ
        
        Returns:
            Tuple[bool, Optional[Dict[str, str]]]: (有効性, エラー詳細)
        """
        errors = {}
        
        try:
            # 必須フィールドのチェック
            if 'status' not in data:
                errors['status'] = "statusは必須フィールドです"
            elif data['status'] is None:
                errors['status'] = "statusは空にできません"
            else:
                # ステータス値のチェック
                valid_statuses = ['healthy', 'degraded', 'down']
                if data['status'] not in valid_statuses:
                    errors['status'] = f"ステータスは {valid_statuses} のいずれかである必要があります"
            
            # オプションフィールドのチェック
            if 'status_display' in data and data['status_display']:
                if len(data['status_display']) > 100:
                    errors['status_display'] = "ステータス表示は100文字以下である必要があります"
            
            if 'message' in data and data['message']:
                if len(data['message']) > 500:
                    errors['message'] = "メッセージは500文字以下である必要があります"
            
            is_valid = len(errors) == 0
            logger.debug(f"システムステータス更新バリデーション結果", {
                'is_valid': is_valid,
                'error_count': len(errors),
                'errors': errors if errors else None
            })
            
            return is_valid, errors if errors else None
            
        except Exception as e:
            logger.error(f"システムステータス更新バリデーション中にエラーが発生", {'error': str(e)})
            return False, {'validation_error': f"バリデーション処理中にエラーが発生しました: {str(e)}"}
    
    @staticmethod
    def _validate_version_format(version: str) -> bool:
        """バージョンフォーマットの検証"""
        pattern = r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?$'
        return bool(re.match(pattern, version))
    
    @staticmethod
    def _validate_datetime_format(datetime_str: str) -> bool:
        """日時フォーマットの検証"""
        try:
            datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _validate_health_check_item(check_name: str, check_data: Dict[str, Any]) -> Optional[str]:
        """ヘルスチェック項目の検証"""
        try:
            # 必須フィールドのチェック
            if 'status' not in check_data:
                return "statusフィールドが必要です"
            
            if 'message' not in check_data:
                return "messageフィールドが必要です"
            
            # ステータス値のチェック
            valid_statuses = ['pass', 'fail']
            if check_data['status'] not in valid_statuses:
                return f"ステータスは {valid_statuses} のいずれかである必要があります"
            
            # レスポンス時間のチェック（オプション）
            if 'response_time' in check_data and check_data['response_time'] is not None:
                if not isinstance(check_data['response_time'], (int, float)) or check_data['response_time'] < 0:
                    return "レスポンス時間は0以上の数値である必要があります"
            
            return None
            
        except Exception as e:
            return f"ヘルスチェック項目の検証中にエラーが発生: {str(e)}"