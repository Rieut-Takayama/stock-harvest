from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter()

@router.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """ダッシュボード統計情報"""
    return {
        "total_stocks_monitored": 3800,
        "active_alerts": random.randint(5, 15),
        "todays_matches": {
            "logic_a": random.randint(2, 8),
            "logic_b": random.randint(1, 6),
            "total": random.randint(3, 14)
        },
        "performance_today": {
            "scans_completed": random.randint(50, 100),
            "avg_scan_time": "2.3秒",
            "success_rate": "99.2%",
            "data_freshness": "20分遅延"
        },
        "market_status": {
            "session": "午前取引" if datetime.now().hour < 12 else "午後取引",
            "nikkei_change": f"{random.uniform(-1.5, 2.0):.2f}%",
            "volume_surge_alerts": random.randint(0, 3)
        },
        "last_updated": datetime.now().isoformat()
    }

@router.get("/api/dashboard/recent-matches")  
async def get_recent_matches():
    """最近の合致銘柄"""
    sample_matches = [
        {
            "code": "7203",
            "name": "トヨタ自動車",
            "logic": "A強化版",
            "score": 85,
            "entry_price": 2150,
            "target_price": 2666,
            "detected_at": datetime.now().isoformat()
        },
        {
            "code": "6758", 
            "name": "ソニーグループ",
            "logic": "B強化版",
            "score": 78,
            "entry_price": 12480,
            "target_price": 15600,
            "detected_at": datetime.now().isoformat()
        },
        {
            "code": "9984",
            "name": "ソフトバンクグループ",
            "logic": "A強化版", 
            "score": 82,
            "entry_price": 6290,
            "target_price": 7799,
            "detected_at": datetime.now().isoformat()
        }
    ]
    return {"matches": sample_matches}