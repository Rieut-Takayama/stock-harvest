"""
シンプル化されたスキャンコントローラー
手動オンデマンド実行専用
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

router = APIRouter()

# モック データ - 実際のAPIでは実データに置き換え
MOCK_STOCKS = [
    {
        "code": "7203",
        "name": "トヨタ自動車",
        "price": 3135,
        "listing_date": "2022-04-15",
        "earnings_date": "2024-11-20",
        "profit_change": "前年-120億→今期+340億"
    },
    {
        "code": "6501", 
        "name": "日立製作所",
        "price": 4200,
        "listing_date": "2021-10-01",
        "earnings_date": "2024-11-19",
        "profit_change": "既に黒字継続中"
    },
    {
        "code": "4755",
        "name": "楽天グループ", 
        "price": 1890,
        "listing_date": "2023-03-10",
        "earnings_date": "2024-11-21",
        "profit_change": "前年-85億→今期+15億"
    }
]

def calculate_years_from_listing(listing_date_str: str) -> str:
    """上場からの経過年数を計算"""
    listing_date = datetime.strptime(listing_date_str, "%Y-%m-%d")
    now = datetime.now()
    diff_months = (now.year - listing_date.year) * 12 + (now.month - listing_date.month)
    years = diff_months // 12
    months = diff_months % 12
    return f"{years}年{months}ヶ月経過"

def get_earnings_quarter(earnings_date_str: str) -> str:
    """決算四半期を取得"""
    earnings_date = datetime.strptime(earnings_date_str, "%Y-%m-%d")
    month = earnings_date.month
    if month <= 3:
        return "Q4"
    elif month <= 6:
        return "Q1" 
    elif month <= 9:
        return "Q2"
    else:
        return "Q3"

@router.get("/logic-a-enhanced")
async def get_logic_a_results():
    """
    ロジックA強化版: ストップ高張り付き精密検出
    """
    try:
        results = []
        
        # ロジックA該当銘柄を検出（モックデータ）
        for stock in MOCK_STOCKS:
            # 上場2年半以内の条件をチェック
            listing_date = datetime.strptime(stock["listing_date"], "%Y-%m-%d")
            years_since_listing = (datetime.now() - listing_date).days / 365.25
            
            if years_since_listing <= 5.0:  # 上場5年以内
                # ロジックAスコア計算
                score = 50
                if years_since_listing <= 2.5:
                    score += 10  # 上場2.5年以内ボーナス
                
                # 詳細根拠データ作成
                prev_price = stock["price"] - int(stock["price"] * 0.1)  # 前日価格（-10%想定）
                stop_high_price = stock["price"]
                
                logic_a_details = {
                    "score": score,
                    "listingDate": stock["listing_date"],
                    "earningsDate": stock["earnings_date"], 
                    "stopHighDate": (datetime.strptime(stock["earnings_date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "prevPrice": prev_price,
                    "stopHighPrice": stop_high_price,
                    "isFirstTime": True,
                    "noConsecutive": True,
                    "noLongTail": True
                }
                
                result = {
                    "code": stock["code"],
                    "name": stock["name"],
                    "score": score,
                    "logicA": logic_a_details
                }
                results.append(result)
        
        # スコア順でソート
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "success": True,
            "results": results,
            "scan_time": datetime.now().isoformat(),
            "total_scanned": 3800,
            "matches_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"ロジックAスキャンエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ロジックAスキャンに失敗しました: {str(e)}")

@router.get("/logic-b-enhanced") 
async def get_logic_b_results():
    """
    ロジックB強化版: 黒字転換銘柄精密検出
    """
    try:
        results = []
        
        # ロジックB該当銘柄を検出（モックデータ）
        for stock in MOCK_STOCKS:
            # 黒字転換条件をチェック
            if "前年" in stock["profit_change"] and "今期" in stock["profit_change"]:
                # ロジックBスコア計算  
                score = 50
                
                # 出来高急増ボーナス
                volume_ratio = round(random.uniform(1.5, 3.0), 1)
                if volume_ratio >= 2.0:
                    score += 10
                
                # 詳細根拠データ作成
                ma_break_date = (datetime.strptime(stock["earnings_date"], "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
                
                logic_b_details = {
                    "score": score,
                    "profitChange": stock["profit_change"],
                    "blackInkDate": stock["earnings_date"],
                    "maBreakDate": ma_break_date,
                    "volumeRatio": volume_ratio
                }
                
                result = {
                    "code": stock["code"],
                    "name": stock["name"], 
                    "score": score,
                    "logicB": logic_b_details
                }
                results.append(result)
        
        # スコア順でソート
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "success": True,
            "results": results,
            "scan_time": datetime.now().isoformat(),
            "total_scanned": 3800,
            "matches_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"ロジックBスキャンエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ロジックBスキャンに失敗しました: {str(e)}")

@router.get("/combined-analysis")
async def get_combined_analysis():
    """
    総合判断: ロジックA+B統合分析
    """
    try:
        results = []
        
        # 各ロジックの結果を取得
        logic_a_response = await get_logic_a_results()
        logic_b_response = await get_logic_b_results()
        
        logic_a_results = {r["code"]: r for r in logic_a_response["results"]}
        logic_b_results = {r["code"]: r for r in logic_b_response["results"]}
        
        # 全銘柄コードを収集
        all_codes = set(logic_a_results.keys()) | set(logic_b_results.keys())
        
        for code in all_codes:
            logic_a = logic_a_results.get(code)
            logic_b = logic_b_results.get(code) 
            
            # 総合スコア計算
            total_score = 0
            result = {
                "code": code,
                "name": logic_a["name"] if logic_a else logic_b["name"],
                "score": 0
            }
            
            if logic_a:
                result["logicA"] = logic_a["logicA"]
                total_score += logic_a["score"]
            
            if logic_b:
                result["logicB"] = logic_b["logicB"]
                total_score += logic_b["score"]
            
            # 両方該当の場合はボーナス
            if logic_a and logic_b:
                total_score += 20  # 両方該当ボーナス
            
            result["score"] = total_score
            results.append(result)
        
        # 総合スコア順でソート
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "success": True,
            "results": results,
            "scan_time": datetime.now().isoformat(),
            "total_scanned": 3800,
            "matches_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"総合判断スキャンエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"総合判断スキャンに失敗しました: {str(e)}")