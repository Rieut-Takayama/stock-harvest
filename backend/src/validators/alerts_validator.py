"""
アラート関連のバリデーション
入力データの検証ルールを定義
"""

from typing import Dict, Any, Tuple
from ..lib.logger import logger


class AlertsValidator:
    """アラート関連のバリデーター"""

    @staticmethod
    def validate_alert_form_data(form_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        アラートフォームデータのバリデーション

        Args:
            form_data: フォームデータ

        Returns:
            Tuple[bool, str]: (バリデーション成功, エラーメッセージ)
        """
        try:
            logger.debug("アラートフォームデータバリデーション開始", {"form_data": form_data})

            # 必須フィールドチェック
            required_fields = ['alertType', 'stockCode']
            for field in required_fields:
                if field not in form_data or not form_data[field]:
                    error_msg = f"{field}は必須です"
                    logger.warning("必須フィールドエラー", {"field": field})
                    return False, error_msg

            # アラートタイプのバリデーション
            alert_type = form_data['alertType']
            if alert_type not in ['price', 'logic']:
                error_msg = "アラートタイプは'price'または'logic'のみ許可されます"
                logger.warning("アラートタイプエラー", {"alertType": alert_type})
                return False, error_msg

            # 銘柄コードのバリデーション
            stock_code = form_data['stockCode']
            if not stock_code.isdigit():
                error_msg = "銘柄コードは数字のみ許可されます"
                logger.warning("銘柄コードエラー", {"stockCode": stock_code})
                return False, error_msg

            if len(stock_code) < 4 or len(stock_code) > 10:
                error_msg = "銘柄コードは4〜10文字である必要があります"
                logger.warning("銘柄コード長さエラー", {"stockCode": stock_code})
                return False, error_msg

            # 価格アラートの場合、targetPriceが必須
            if alert_type == 'price':
                target_price = form_data.get('targetPrice')
                if target_price is None:
                    error_msg = "価格到達アラートの場合、目標価格は必須です"
                    logger.warning("目標価格エラー", {"alertType": alert_type})
                    return False, error_msg

                # 価格のバリデーション
                try:
                    price_float = float(target_price)
                    if price_float <= 0:
                        error_msg = "目標価格は正の数値である必要があります"
                        logger.warning("目標価格範囲エラー", {"targetPrice": target_price})
                        return False, error_msg
                except (ValueError, TypeError):
                    error_msg = "目標価格は有効な数値である必要があります"
                    logger.warning("目標価格型エラー", {"targetPrice": target_price})
                    return False, error_msg

            logger.debug("アラートフォームデータバリデーション成功")
            return True, ""

        except Exception as e:
            logger.error("アラートバリデーションエラー", {"error": str(e)})
            return False, f"バリデーションエラー: {str(e)}"

    @staticmethod
    def validate_alert_condition(alert_type: str, condition: Dict[str, Any]) -> Tuple[bool, str]:
        """
        アラート条件のバリデーション

        Args:
            alert_type: アラートタイプ
            condition: アラート条件

        Returns:
            Tuple[bool, str]: (バリデーション成功, エラーメッセージ)
        """
        try:
            logger.debug("アラート条件バリデーション開始", {
                "alertType": alert_type,
                "condition": condition
            })

            if alert_type == 'price':
                # 価格アラートの条件チェック
                if 'targetPrice' not in condition:
                    error_msg = "価格アラートにはtargetPriceが必要です"
                    logger.warning("価格条件エラー", {"condition": condition})
                    return False, error_msg

                if 'priceDirection' not in condition:
                    error_msg = "価格アラートにはpriceDirectionが必要です"
                    logger.warning("価格方向エラー", {"condition": condition})
                    return False, error_msg

                if condition['priceDirection'] not in ['above', 'below']:
                    error_msg = "priceDirectionは'above'または'below'のみ許可されます"
                    logger.warning("価格方向値エラー", {"priceDirection": condition['priceDirection']})
                    return False, error_msg

            elif alert_type == 'logic':
                # ロジックアラートの条件チェック
                if 'logic' not in condition:
                    error_msg = "ロジックアラートにはlogicが必要です"
                    logger.warning("ロジック条件エラー", {"condition": condition})
                    return False, error_msg

                if condition['logic'] not in ['logic_a', 'logic_b']:
                    error_msg = "logicは'logic_a'または'logic_b'のみ許可されます"
                    logger.warning("ロジック値エラー", {"logic": condition['logic']})
                    return False, error_msg

            logger.debug("アラート条件バリデーション成功")
            return True, ""

        except Exception as e:
            logger.error("アラート条件バリデーションエラー", {"error": str(e)})
            return False, f"条件バリデーションエラー: {str(e)}"

    @staticmethod
    def validate_line_config(config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        LINE通知設定のバリデーション

        Args:
            config: LINE通知設定

        Returns:
            Tuple[bool, str]: (バリデーション成功, エラーメッセージ)
        """
        try:
            logger.debug("LINE通知設定バリデーション開始", {"config": config})

            # isConnectedフィールドチェック
            if 'isConnected' not in config:
                error_msg = "isConnectedフィールドは必須です"
                logger.warning("isConnectedエラー")
                return False, error_msg

            # 接続状態がtrueの場合、tokenが必要
            if config['isConnected'] is True:
                if 'token' not in config or not config['token']:
                    error_msg = "LINE接続時にはtokenが必要です"
                    logger.warning("tokenエラー")
                    return False, error_msg

            logger.debug("LINE通知設定バリデーション成功")
            return True, ""

        except Exception as e:
            logger.error("LINE通知設定バリデーションエラー", {"error": str(e)})
            return False, f"LINE設定バリデーションエラー: {str(e)}"
