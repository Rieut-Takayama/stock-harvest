"""
お問い合わせ関連のリポジトリ層
データベースアクセスを担当
"""

from datetime import datetime
from typing import List, Dict, Any
import uuid
import json
from ..database.config import database
from ..lib.logger import logger, PerformanceTracker

class ContactRepository:
    
    async def get_all_faq(self) -> List[Dict[str, Any]]:
        """
        FAQ一覧を取得
        """
        tracker = PerformanceTracker("FAQ DB取得", logger)

        try:
            logger.info("FAQ一覧取得開始")

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
                        logger.warning("FAQ タグJSONデコード失敗", {
                            "faq_id": row['id']
                        })
                        tags = []

                faq_item = {
                    "id": row["id"],
                    "category": row["category"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "tags": tags
                }
                faq_list.append(faq_item)

            tracker.end({"count": len(faq_list)})
            logger.info("FAQ一覧取得成功", {"count": len(faq_list)})

            return faq_list

        except Exception as e:
            logger.error("FAQ一覧取得エラー", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    async def save_contact_inquiry(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        お問い合わせ内容を保存
        """
        tracker = PerformanceTracker("問合せ DB保存", logger)

        try:
            logger.info("問合せ保存開始")

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

            tracker.end({"inquiry_id": inquiry_id})
            logger.info("問合せ保存成功", {
                "inquiry_id": inquiry_id,
                "type": form_data["type"]
            })

            return result

        except Exception as e:
            logger.error("問合せ保存エラー", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    async def get_inquiry_by_id(self, inquiry_id: str) -> Dict[str, Any]:
        """
        お問い合わせIDで詳細を取得（将来的な管理機能用）
        """
        tracker = PerformanceTracker("問合せ詳細取得", logger)

        try:
            logger.info("問合せ詳細取得開始", {"inquiry_id": inquiry_id})

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

                tracker.end({"inquiry_id": inquiry_id, "found": True})
                logger.info("問合せ詳細取得成功", {"inquiry_id": inquiry_id})

                return inquiry
            else:
                tracker.end({"inquiry_id": inquiry_id, "found": False})
                logger.warning("問合せが見つかりません", {"inquiry_id": inquiry_id})

                return None

        except Exception as e:
            logger.error("問合せ詳細取得エラー", {
                "inquiry_id": inquiry_id,
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise