"""
お問い合わせ関連のサービス層
ビジネスロジックを担当
"""

from typing import List, Dict, Any
import logging
from ..repositories.contact_repository import ContactRepository

logger = logging.getLogger(__name__)

class ContactService:
    
    def __init__(self):
        self.contact_repo = ContactRepository()
    
    async def get_faq_list(self) -> List[Dict[str, Any]]:
        """
        FAQ一覧を取得（ビジネスロジック付き）
        """
        try:
            logger.info("🔍 FAQサービス開始")
            
            # リポジトリからFAQ一覧を取得
            faq_list = await self.contact_repo.get_all_faq()
            
            # ビジネスルール: カテゴリごとのソートを追加
            sorted_faq = sorted(faq_list, key=lambda x: (
                self._get_category_priority(x["category"]),
                x.get("display_order", 999),
                x["id"]
            ))
            
            logger.info(f"✅ FAQ一覧取得完了: {len(sorted_faq)}件")
            return sorted_faq
            
        except Exception as e:
            logger.error(f"❌ FAQサービスエラー: {e}")
            raise
    
    def _get_category_priority(self, category: str) -> int:
        """
        カテゴリの表示優先順位を決定
        """
        priority_map = {
            "スキャン機能": 1,
            "ロジック説明": 2,
            "アラート機能": 3,
            "システム": 4,
            "トラブル": 5
        }
        return priority_map.get(category, 999)
    
    async def submit_contact_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        お問い合わせフォーム処理（ビジネスロジック付き）
        """
        try:
            logger.info("📧 お問い合わせサービス開始")
            
            # ビジネスルール: お問い合わせ内容の前処理
            processed_data = self._preprocess_form_data(form_data)
            
            # リポジトリに保存
            result = await self.contact_repo.save_contact_inquiry(processed_data)
            
            # ビジネスルール: 優先度に応じた追加処理
            await self._handle_priority_logic(processed_data)
            
            logger.info(f"✅ お問い合わせ処理完了: {result['inquiry_id']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ お問い合わせサービスエラー: {e}")
            raise
    
    def _preprocess_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        フォームデータの前処理
        """
        processed = form_data.copy()
        
        # 件名の自動調整
        subject = processed["subject"].strip()
        if not subject.startswith("[" + processed["type"].upper() + "]"):
            processed["subject"] = f"[{processed['type'].upper()}] {subject}"
        
        # 内容の整形
        processed["content"] = processed["content"].strip()
        
        # 優先度の自動調整
        if "緊急" in subject or "エラー" in subject or "障害" in subject:
            processed["priority"] = "high"
        
        return processed
    
    async def _handle_priority_logic(self, form_data: Dict[str, Any]) -> None:
        """
        優先度に応じた追加処理
        """
        try:
            if form_data["priority"] == "high":
                logger.info(f"🚨 高優先度お問い合わせ: {form_data['subject']}")
                # 将来的にはSlack通知やメール送信を実装
            
            # お問い合わせタイプ別の処理
            if form_data["type"] == "bug":
                logger.info("🐛 バグレポート受信 - 開発チームに通知")
            elif form_data["type"] == "feature":
                logger.info("💡 機能要望受信 - プロダクトチームに転送")
                
        except Exception as e:
            logger.warning(f"⚠️ 優先度処理でエラー（処理は継続）: {e}")