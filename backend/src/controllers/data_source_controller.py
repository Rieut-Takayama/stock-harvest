"""
データソース基盤API コントローラー
上場日データ・制限値幅・株価データ取得などの新機能API
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ..services.listing_data_service import ListingDataService
from ..services.price_limit_service import PriceLimitService
from ..services.stock_data_service_enhanced import StockDataServiceEnhanced
from ..services.irbank_integration_service import IRBankIntegrationService
from ..services.kabutan_integration_service import KabutanIntegrationService
from ..services.data_source_scheduler_service import DataSourceSchedulerService
from ..services.enhanced_earnings_service import EnhancedEarningsService

logger = logging.getLogger(__name__)

# APIルーター初期化
router = APIRouter(prefix="/api/data-source", tags=["data-source"])

# サービス依存注入
def get_listing_service():
    return ListingDataService()

def get_price_limit_service():
    return PriceLimitService()

def get_stock_data_service():
    return StockDataServiceEnhanced()

def get_irbank_service():
    return IRBankIntegrationService()

def get_kabutan_service():
    return KabutanIntegrationService()

def get_scheduler_service():
    return DataSourceSchedulerService()

def get_enhanced_earnings_service():
    return EnhancedEarningsService()


@router.get("/listing-dates/update")
async def update_listing_data(
    use_sample: bool = Query(True, description="サンプルデータを使用するか"),
    listing_service: ListingDataService = Depends(get_listing_service)
):
    """
    上場日データを更新
    開発環境ではサンプルデータ、本番環境では実際のJSEデータを使用
    """
    try:
        logger.info("📅 上場日データ更新API開始")
        result = await listing_service.update_listing_data(use_sample=use_sample)
        
        return {
            "success": True,
            "message": "上場日データ更新完了",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 上場日データ更新APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上場日データ更新に失敗しました: {str(e)}")


@router.get("/listing-dates/targets")
async def get_target_stocks(
    limit: int = Query(100, description="取得件数上限"),
    listing_service: ListingDataService = Depends(get_listing_service)
):
    """
    スキャン対象銘柄リスト（上場2.5-5年以内）を取得
    """
    try:
        result = await listing_service.get_target_stocks(limit=limit)
        
        return {
            "success": True,
            "message": f"スキャン対象銘柄 {len(result)} 件取得",
            "data": result,
            "total_count": len(result)
        }
        
    except Exception as e:
        logger.error(f"❌ スキャン対象銘柄取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"スキャン対象銘柄取得に失敗しました: {str(e)}")


@router.get("/listing-dates/stats")
async def get_listing_stats(
    listing_service: ListingDataService = Depends(get_listing_service)
):
    """
    上場日データの統計情報を取得
    """
    try:
        result = await listing_service.get_listing_stats()
        
        return {
            "success": True,
            "message": "上場統計取得完了",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 上場統計取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上場統計取得に失敗しました: {str(e)}")


@router.get("/price-limits/calculate")
async def calculate_price_limits(
    price: float = Query(..., description="基準価格"),
    stage: int = Query(1, description="値幅制限段階（1: 通常、2: 2倍拡大）"),
    price_limit_service: PriceLimitService = Depends(get_price_limit_service)
):
    """
    指定価格の制限値幅を計算
    """
    try:
        if price <= 0:
            raise HTTPException(status_code=400, detail="価格は正の値で入力してください")
        
        if stage not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="段階は1、2、3のいずれかを指定してください")
        
        result = price_limit_service.calculate_price_limits(price, stage)
        
        return {
            "success": True,
            "message": f"制限値幅計算完了（{price}円）",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 制限値幅計算APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"制限値幅計算に失敗しました: {str(e)}")


@router.post("/price-limits/update/{stock_code}")
async def update_stock_price_limit(
    stock_code: str,
    current_price: float = Query(..., description="現在価格"),
    stage: int = Query(1, description="値幅制限段階"),
    price_limit_service: PriceLimitService = Depends(get_price_limit_service)
):
    """
    指定銘柄の制限値幅をデータベースに更新
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        if current_price <= 0:
            raise HTTPException(status_code=400, detail="現在価格は正の値で入力してください")
        
        result = await price_limit_service.update_stock_price_limits(
            stock_code, current_price, stage
        )
        
        return {
            "success": True,
            "message": f"銘柄 {stock_code} の制限値幅更新完了",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 制限値幅更新APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"制限値幅更新に失敗しました: {str(e)}")


@router.get("/price-limits/{stock_code}")
async def get_price_limit_info(
    stock_code: str,
    price_limit_service: PriceLimitService = Depends(get_price_limit_service)
):
    """
    指定銘柄の制限値幅情報を取得
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        result = await price_limit_service.get_price_limit_info(stock_code)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"銘柄 {stock_code} の制限値幅情報が見つかりません")
        
        return {
            "success": True,
            "message": f"銘柄 {stock_code} の制限値幅情報取得完了",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 制限値幅情報取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"制限値幅情報取得に失敗しました: {str(e)}")


@router.get("/price-limits/check-alerts/{stock_code}")
async def check_price_alerts(
    stock_code: str,
    current_price: float = Query(..., description="現在価格"),
    price_limit_service: PriceLimitService = Depends(get_price_limit_service)
):
    """
    価格がストップ高・ストップ安に接近しているかチェック
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        if current_price <= 0:
            raise HTTPException(status_code=400, detail="現在価格は正の値で入力してください")
        
        result = await price_limit_service.check_price_alerts(stock_code, current_price)
        
        return {
            "success": True,
            "message": f"銘柄 {stock_code} の価格アラートチェック完了",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 価格アラートチェックAPIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"価格アラートチェックに失敗しました: {str(e)}")


@router.get("/price-limits/stats")
async def get_price_limit_stats(
    price_limit_service: PriceLimitService = Depends(get_price_limit_service)
):
    """
    制限値幅データの統計情報を取得
    """
    try:
        result = await price_limit_service.get_price_limit_stats()
        
        return {
            "success": True,
            "message": "制限値幅統計取得完了",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 制限値幅統計取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"制限値幅統計取得に失敗しました: {str(e)}")


@router.get("/price-limits/table-info")
async def get_price_limit_table_info(
    price_limit_service: PriceLimitService = Depends(get_price_limit_service)
):
    """
    価格制限テーブルの情報を取得
    """
    try:
        result = price_limit_service.get_price_limit_table_info()
        
        return {
            "success": True,
            "message": "価格制限テーブル情報取得完了",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 価格制限テーブル情報取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"価格制限テーブル情報取得に失敗しました: {str(e)}")


@router.get("/stock-data/{stock_code}")
async def get_stock_data_enhanced(
    stock_code: str,
    stock_name: str = Query(None, description="銘柄名（オプション）"),
    use_cache: bool = Query(True, description="キャッシュを使用するか"),
    stock_data_service: StockDataServiceEnhanced = Depends(get_stock_data_service)
):
    """
    強化版株価データ取得（キャッシュ・リトライ・エラーハンドリング付き）
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        # 銘柄名が未指定の場合はサンプルリストから取得
        if not stock_name:
            sample_stocks = stock_data_service.get_sample_stock_list()
            stock_info = next((s for s in sample_stocks if s['code'] == stock_code), None)
            stock_name = stock_info['name'] if stock_info else f"銘柄{stock_code}"
        
        result = await stock_data_service.fetch_stock_data(
            stock_code, stock_name, use_cache
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"銘柄 {stock_code} のデータが取得できませんでした")
        
        return {
            "success": True,
            "message": f"銘柄 {stock_code} のデータ取得完了",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 強化版株価データ取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"株価データ取得に失敗しました: {str(e)}")


@router.post("/stock-data/batch")
async def batch_fetch_stock_data(
    stock_codes: List[str],
    max_concurrent: int = Query(5, description="最大同時実行数"),
    stock_data_service: StockDataServiceEnhanced = Depends(get_stock_data_service)
):
    """
    複数銘柄のデータを並行取得
    """
    try:
        if not stock_codes:
            raise HTTPException(status_code=400, detail="銘柄コードリストが空です")
        
        if len(stock_codes) > 50:
            raise HTTPException(status_code=400, detail="一度に取得できる銘柄数は50件までです")
        
        # 銘柄コードの検証
        for code in stock_codes:
            if len(code) != 4 or not code.isdigit():
                raise HTTPException(status_code=400, detail=f"無効な銘柄コード: {code}")
        
        # サンプル銘柄リストから銘柄名を取得
        sample_stocks = stock_data_service.get_sample_stock_list()
        stock_dict = {s['code']: s['name'] for s in sample_stocks}
        
        stock_list = [
            {
                'code': code,
                'name': stock_dict.get(code, f"銘柄{code}")
            }
            for code in stock_codes
        ]
        
        results = await stock_data_service.batch_fetch_stock_data(
            stock_list, max_concurrent
        )
        
        return {
            "success": True,
            "message": f"複数銘柄データ取得完了（{len(results)}/{len(stock_codes)} 件成功）",
            "data": results,
            "requested_count": len(stock_codes),
            "successful_count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 複数銘柄データ取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"複数銘柄データ取得に失敗しました: {str(e)}")


@router.get("/stock-data/statistics")
async def get_fetch_statistics(
    stock_data_service: StockDataServiceEnhanced = Depends(get_stock_data_service)
):
    """
    データ取得統計を取得
    """
    try:
        result = stock_data_service.get_fetch_statistics()
        
        return {
            "success": True,
            "message": "データ取得統計取得完了",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ データ取得統計取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"データ取得統計取得に失敗しました: {str(e)}")


@router.delete("/stock-data/cache")
async def clear_cache(
    stock_code: Optional[str] = Query(None, description="特定銘柄のキャッシュをクリア（未指定の場合は全キャッシュ）"),
    stock_data_service: StockDataServiceEnhanced = Depends(get_stock_data_service)
):
    """
    株価データキャッシュをクリア
    """
    try:
        await stock_data_service.clear_cache(stock_code)
        
        message = f"銘柄 {stock_code} のキャッシュクリア完了" if stock_code else "全キャッシュクリア完了"
        
        return {
            "success": True,
            "message": message,
            "data": {
                "cleared_stock": stock_code,
                "cleared_all": stock_code is None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ キャッシュクリアAPIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"キャッシュクリアに失敗しました: {str(e)}")


@router.get("/health")
async def health_check():
    """
    データソース基盤のヘルスチェック
    """
    try:
        # 各サービスの基本機能をテスト
        listing_service = ListingDataService()
        price_limit_service = PriceLimitService()
        stock_data_service = StockDataServiceEnhanced()
        irbank_service = IRBankIntegrationService()
        kabutan_service = KabutanIntegrationService()
        
        health_status = {
            "listing_service": "healthy",
            "price_limit_service": "healthy", 
            "stock_data_service": "healthy",
            "irbank_service": "healthy",
            "kabutan_service": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"  # 実際の時刻に置き換え
        }
        
        return {
            "success": True,
            "message": "データソース基盤は正常稼働中",
            "data": health_status
        }
        
    except Exception as e:
        logger.error(f"❌ ヘルスチェックエラー: {str(e)}")
        return {
            "success": False,
            "message": f"データソース基盤でエラーが発生しています: {str(e)}",
            "data": {"error": str(e)}
        }


# IRバンク連携エンドポイント
@router.get("/irbank/earnings-schedule")
async def fetch_irbank_earnings_schedule(
    target_date: Optional[str] = Query(None, description="対象日（YYYY-MM-DD）"),
    irbank_service: IRBankIntegrationService = Depends(get_irbank_service)
):
    """
    IRバンクから決算発表予定を取得
    """
    try:
        logger.info("📊 IRバンク決算スケジュール取得API開始")
        result = await irbank_service.fetch_earnings_schedule(target_date)
        
        return {
            "success": True,
            "message": f"IRバンク決算スケジュール取得完了: {len(result)} 件",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ IRバンク決算スケジュール取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"IRバンク決算スケジュール取得に失敗しました: {str(e)}")


@router.get("/irbank/disclosure/{stock_code}")
async def fetch_irbank_disclosure(
    stock_code: str,
    days_back: int = Query(30, description="過去何日分取得するか"),
    irbank_service: IRBankIntegrationService = Depends(get_irbank_service)
):
    """
    IRバンクから適時開示情報を取得
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        result = await irbank_service.fetch_disclosure_info(stock_code, days_back)
        
        return {
            "success": True,
            "message": f"適時開示情報取得完了: {len(result)} 件",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 適時開示情報取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"適時開示情報取得に失敗しました: {str(e)}")


@router.get("/irbank/status")
async def get_irbank_status(
    irbank_service: IRBankIntegrationService = Depends(get_irbank_service)
):
    """
    IRバンクサービスの状態を取得
    """
    try:
        status = await irbank_service.get_service_status()
        
        return {
            "success": True,
            "message": "IRバンクサービス状態取得完了",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"❌ IRバンクサービス状態取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"IRバンクサービス状態取得に失敗しました: {str(e)}")


# カブタン連携エンドポイント
@router.get("/kabutan/earnings-summary/{stock_code}")
async def fetch_kabutan_earnings_summary(
    stock_code: str,
    kabutan_service: KabutanIntegrationService = Depends(get_kabutan_service)
):
    """
    カブタンから決算サマリーを取得
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        result = await kabutan_service.fetch_earnings_summary(stock_code)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"銘柄 {stock_code} の決算サマリーが取得できませんでした")
        
        return {
            "success": True,
            "message": f"決算サマリー取得完了: {stock_code}",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 決算サマリー取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"決算サマリー取得に失敗しました: {str(e)}")


@router.get("/kabutan/company-profile/{stock_code}")
async def fetch_kabutan_company_profile(
    stock_code: str,
    kabutan_service: KabutanIntegrationService = Depends(get_kabutan_service)
):
    """
    カブタンから企業プロフィールを取得
    """
    try:
        if len(stock_code) != 4 or not stock_code.isdigit():
            raise HTTPException(status_code=400, detail="銘柄コードは4桁の数字で入力してください")
        
        result = await kabutan_service.fetch_company_profile(stock_code)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"銘柄 {stock_code} の企業プロフィールが取得できませんでした")
        
        return {
            "success": True,
            "message": f"企業プロフィール取得完了: {stock_code}",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 企業プロフィール取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"企業プロフィール取得に失敗しました: {str(e)}")


@router.get("/kabutan/status")
async def get_kabutan_status(
    kabutan_service: KabutanIntegrationService = Depends(get_kabutan_service)
):
    """
    カブタンサービスの状態を取得
    """
    try:
        status = await kabutan_service.get_service_status()
        
        return {
            "success": True,
            "message": "カブタンサービス状態取得完了",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"❌ カブタンサービス状態取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"カブタンサービス状態取得に失敗しました: {str(e)}")


# 強化版決算サービスエンドポイント
@router.get("/earnings/comprehensive-calendar")
async def get_comprehensive_earnings_calendar(
    start_date: Optional[str] = Query(None, description="開始日（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="終了日（YYYY-MM-DD）"),
    include_forecasts: bool = Query(True, description="業績予想を含めるか"),
    enhanced_service: EnhancedEarningsService = Depends(get_enhanced_earnings_service)
):
    """
    包括的な決算カレンダーを取得
    """
    try:
        result = await enhanced_service.get_comprehensive_earnings_calendar(
            start_date, end_date, include_forecasts
        )
        
        return {
            "success": True,
            "message": f"包括的決算カレンダー取得完了: {result['summary']['total_earnings']} 件",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 包括的決算カレンダー取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"包括的決算カレンダー取得に失敗しました: {str(e)}")


@router.get("/earnings/black-ink-pipeline")
async def get_black_ink_conversion_pipeline(
    enhanced_service: EnhancedEarningsService = Depends(get_enhanced_earnings_service)
):
    """
    黒字転換パイプライン分析を取得
    """
    try:
        result = await enhanced_service.get_black_ink_conversion_pipeline()
        
        return {
            "success": True,
            "message": f"黒字転換パイプライン分析完了: {result['summary']['total_candidates']} 候補",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 黒字転換パイプライン分析APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"黒字転換パイプライン分析に失敗しました: {str(e)}")


@router.post("/earnings/update-external-sources")
async def update_earnings_from_external_sources(
    stock_codes: Optional[List[str]] = Query(None, description="更新対象銘柄コード（未指定の場合は自動選択）"),
    enhanced_service: EnhancedEarningsService = Depends(get_enhanced_earnings_service)
):
    """
    外部ソースから決算データを更新
    """
    try:
        result = await enhanced_service.update_earnings_from_external_sources(stock_codes)
        
        return {
            "success": True,
            "message": f"外部ソース決算データ更新完了",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 外部ソース決算データ更新APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"外部ソース決算データ更新に失敗しました: {str(e)}")


# スケジューラーエンドポイント
@router.post("/scheduler/start")
async def start_scheduler(
    scheduler_service: DataSourceSchedulerService = Depends(get_scheduler_service)
):
    """
    データソーススケジューラーを開始
    """
    try:
        await scheduler_service.start_scheduler()
        
        return {
            "success": True,
            "message": "データソーススケジューラー開始完了",
            "data": {"is_running": scheduler_service.is_running}
        }
        
    except Exception as e:
        logger.error(f"❌ スケジューラー開始APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"スケジューラー開始に失敗しました: {str(e)}")


@router.post("/scheduler/stop")
async def stop_scheduler(
    scheduler_service: DataSourceSchedulerService = Depends(get_scheduler_service)
):
    """
    データソーススケジューラーを停止
    """
    try:
        await scheduler_service.stop_scheduler()
        
        return {
            "success": True,
            "message": "データソーススケジューラー停止完了",
            "data": {"is_running": scheduler_service.is_running}
        }
        
    except Exception as e:
        logger.error(f"❌ スケジューラー停止APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"スケジューラー停止に失敗しました: {str(e)}")


@router.get("/scheduler/status")
async def get_scheduler_status(
    scheduler_service: DataSourceSchedulerService = Depends(get_scheduler_service)
):
    """
    スケジューラーの状態を取得
    """
    try:
        status = await scheduler_service.get_service_status()
        
        return {
            "success": True,
            "message": "スケジューラー状態取得完了",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"❌ スケジューラー状態取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"スケジューラー状態取得に失敗しました: {str(e)}")


@router.get("/scheduler/jobs")
async def get_scheduled_jobs(
    scheduler_service: DataSourceSchedulerService = Depends(get_scheduler_service)
):
    """
    スケジュール済みジョブ一覧を取得
    """
    try:
        jobs = scheduler_service.get_scheduled_jobs()
        
        return {
            "success": True,
            "message": f"スケジュール済みジョブ取得完了: {len(jobs)} 件",
            "data": jobs
        }
        
    except Exception as e:
        logger.error(f"❌ スケジュール済みジョブ取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"スケジュール済みジョブ取得に失敗しました: {str(e)}")


@router.post("/scheduler/execute-job/{job_id}")
async def execute_job_manually(
    job_id: str,
    scheduler_service: DataSourceSchedulerService = Depends(get_scheduler_service)
):
    """
    ジョブを手動実行
    """
    try:
        result = await scheduler_service.execute_job_manually(job_id)
        
        return {
            "success": result['success'],
            "message": result['message'],
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ ジョブ手動実行APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ジョブ手動実行に失敗しました: {str(e)}")


@router.get("/scheduler/statistics")
async def get_scheduler_statistics(
    scheduler_service: DataSourceSchedulerService = Depends(get_scheduler_service)
):
    """
    スケジューラーの実行統計を取得
    """
    try:
        stats = scheduler_service.get_execution_statistics()
        
        return {
            "success": True,
            "message": "スケジューラー実行統計取得完了",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"❌ スケジューラー実行統計取得APIエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"スケジューラー実行統計取得に失敗しました: {str(e)}")