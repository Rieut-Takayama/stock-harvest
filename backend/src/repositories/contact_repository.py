"""
お問い合わせ関連のリポジトリ層
データベースアクセスを担当
"""

from datetime import datetime
from typing import List, Dict, Any
import uuid
import json
from ..database.config import database
import logging

logger = logging.getLogger(__name__)

class ContactRepository:
    
    async def get_all_faq(self) -> List[Dict[str, Any]]:
        """
        FAQ一覧を取得
        """
        try:
            logger.info("📚 FAQ一覧取得開始")
            
            query = """
            SELECT id, category, question, answer, tags, display_order
            FROM faq 
            WHERE is_active = true
            ORDER BY display_order ASC, created_at ASC
            """
            
            results = await database.fetch_all(query)
            
            faq_list = []
            for row in results:
                # タグのJSONデコード
                tags = []
                if row["tags"]:
                    try:
                        tags = json.loads(row["tags"])
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ FAQ ID {row['id']}: タグのJSONデコードに失敗")
                        tags = []
                
                faq_item = {
                    "id": row["id"],
                    "category": row["category"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "tags": tags
                }
                faq_list.append(faq_item)
            
            logger.info(f"✅ FAQ一覧取得成功: {len(faq_list)}件")
            return faq_list
            
        except Exception as e:
            logger.error(f"❌ FAQ一覧取得エラー: {e}")
            raise
    
    async def save_contact_inquiry(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        お問い合わせ内容を保存
        """
        try:
            logger.info("💾 お問い合わせ保存開始")
            
            # ユニークIDを生成
            inquiry_id = f"inq-{uuid.uuid4().hex[:12]}"
            current_time = datetime.now()
            
            query = """
            INSERT INTO contact_inquiries 
            (id, type, subject, content, email, priority, status, created_at)
            VALUES 
            (:id, :type, :subject, :content, :email, :priority, :status, :created_at)
            """
            
            values = {
                "id": inquiry_id,
                "type": form_data["type"],
                "subject": form_data["subject"],
                "content": form_data["content"],
                "email": form_data["email"],
                "priority": form_data["priority"],
                "status": "open",
                "created_at": current_time
            }
            
            await database.execute(query, values)
            
            result = {
                "inquiry_id": inquiry_id,
                "submitted_at": current_time.isoformat(),
                "status": "saved"
            }
            
            logger.info(f"✅ お問い合わせ保存成功: {inquiry_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ お問い合わせ保存エラー: {e}")
            raise
    
    async def get_inquiry_by_id(self, inquiry_id: str) -> Dict[str, Any]:
        """
        お問い合わせIDで詳細を取得（将来的な管理機能用）
        """
        try:
            logger.info(f"🔍 お問い合わせ詳細取得: {inquiry_id}")
            
            query = """
            SELECT id, type, subject, content, email, priority, status,
                   created_at, response_at, resolved_at
            FROM contact_inquiries
            WHERE id = :inquiry_id
            """
            
            result = await database.fetch_one(query, {"inquiry_id": inquiry_id})
            
            if result:
                inquiry = {
                    "id": result["id"],
                    "type": result["type"],
                    "subject": result["subject"],
                    "content": result["content"],
                    "email": result["email"],
                    "priority": result["priority"],
                    "status": result["status"],
                    "createdAt": result["created_at"].isoformat(),
                    "responseAt": result["response_at"].isoformat() if result["response_at"] else None,
                    "resolvedAt": result["resolved_at"].isoformat() if result["resolved_at"] else None
                }
                
                logger.info(f"✅ お問い合わせ詳細取得成功: {inquiry_id}")
                return inquiry
            else:
                logger.warning(f"⚠️ お問い合わせが見つかりません: {inquiry_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ お問い合わせ詳細取得エラー: {e}")
            raise