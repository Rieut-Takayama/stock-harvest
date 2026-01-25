import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Alert
} from '@mui/material';
import {
  TrendingUp as LogicAIcon,
  AccountBalance as LogicBIcon,
  Star as CombinedIcon,
  Computer as TechIcon,
  AccountBalance as FinanceIcon,
  Factory as ManufacturingIcon,
  ShoppingCart as ConsumerIcon,
  Business as InfraIcon
} from '@mui/icons-material';

interface StockResult {
  code: string;
  name: string;
  score: number;
  logicA?: LogicADetails;
  logicB?: LogicBDetails;
  bonuses?: string[];
  priority_level?: string;
  sector?: string;
  category?: string;  // '惜しい銘柄'等
  near_miss_reasons?: string[];  // 惜しい銘柄の理由
  analysis_summary?: {
    logic_a_score: number;
    logic_b_score: number;
    total_conditions_met: number;
  };
}

interface LogicADetails {
  score: number;
  listingDate: string;
  earningsDate: string;
  stopHighDate: string;
  prevPrice: number;
  stopHighPrice: number;
  isFirstTime: boolean;
  noConsecutive: boolean;
  noLongTail: boolean;
}

interface LogicBDetails {
  score: number;
  profitChange: string;
  blackInkDate: string;
  maBreakDate: string;
  volumeRatio: number;
}

export const SimpleDashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<StockResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeLogic, setActiveLogic] = useState<'A' | 'B' | 'combined' | 'sectorTech' | 'sectorFinance' | 'sectorManufacturing' | 'sectorConsumer' | 'sectorInfra' | null>(null);
  // Future use: Smart schedule info will be used once API endpoint is implemented
  // @ts-expect-error - Unused variable will be used in future implementation
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [scheduleInfo, setScheduleInfo] = useState<{
    scan_recommended: boolean;
    current_status: { message: string };
    next_target: { days_until: number; date: string };
  } | null>(null);
  
  // スマートスケジュール情報取得
  // 注: このAPIエンドポイントは現在未実装のため、コメントアウト
  // React.useEffect(() => {
  //   const checkSchedule = async () => {
  //     try {
  //       const response = await fetch('/api/smart-schedule-scanner');
  //       if (response.ok) {
  //         const data = await response.json();
  //         setScheduleInfo(data);
  //       } else if (response.status === 404) {
  //         // エンドポイントが未実装の場合は無視
  //       } else {
  //         throw new Error(`HTTP ${response.status}`);
  //       }
  //     } catch {
  //       // ネットワークエラーやJSON parseエラーの場合は無視（E2Eテストでエラーになるのを防ぐ）
  //     }
  //   };
  //   checkSchedule();
  // }, []);

  const executeLogicA = async () => {
    setLoading(true);
    setActiveLogic('A');
    setError(null);

    try {
      const response = await fetch('/api/scan/logic-a-enhanced');
      if (!response.ok) throw new Error('ロジックAスキャンに失敗しました');

      const data = await response.json();

      if (data.results && data.results.length > 0) {
        setResults(data.results);
        setError(null);
      } else {
        const scanned = data.total_scanned || data.processed_count || '不明';
        const detailedMsg = data.detailed_message || `${scanned}銘柄をスキャンしましたが、条件に合致する銘柄が見つかりませんでした`;
        setError(detailedMsg);
        setResults([]);
      }
    } catch (err) {
      console.error('🔥 ロジックAエラー:', err);
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const executeLogicB = async () => {
    setLoading(true);
    setActiveLogic('B');
    setError(null);

    try {
      const response = await fetch('/api/scan/logic-b-enhanced');
      if (!response.ok) throw new Error('ロジックBスキャンに失敗しました');

      const data = await response.json();

      if (data.results && data.results.length > 0) {
        setResults(data.results);
        setError(null);
      } else {
        const scanned = data.total_scanned || data.processed_count || '不明';
        const detailedMsg = data.detailed_message || `${scanned}銘柄をスキャンしましたが、条件に合致する銘柄が見つかりませんでした`;
        setError(detailedMsg);
        setResults([]);
      }
    } catch (err) {
      console.error('🔥 ロジックBエラー:', err);
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const executeCombined = async () => {
    setLoading(true);
    setActiveLogic('combined');
    setError(null);

    try {
      const response = await fetch('/api/scan/combined-analysis');
      if (!response.ok) throw new Error('総合判断スキャンに失敗しました');

      const data = await response.json();

      if (data.results && data.results.length > 0) {
        setResults(data.results);
        setError(null);
      } else {
        const scanned = data.total_scanned || data.processed_count || '不明';
        setError(`📊 総合判断スキャン結果\n\n✅ スキャン完了: ${scanned}銘柄を処理\n🚫 条件合致: 0銘柄\n\n📋 総合判断条件:\n• ロジックAまたはロジックBの全条件を満たす\n• 両ロジック合致で最優先銘柄\n• リアルタイム総合分析\n\n🔍 参考: ロジックA/B個別スキャンで詳細確認`);
        setResults([]);
      }
    } catch (err) {
      console.error('🔥 総合判断エラー:', err);
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const executeSectorScan = async (sector: string, apiEndpoint: string) => {
    setLoading(true);
    setActiveLogic(sector as 'A' | 'B' | 'combined' | 'sectorTech' | 'sectorFinance' | 'sectorManufacturing' | 'sectorConsumer' | 'sectorInfra');
    setError(null);
    
    try {
      // セクター別実データAPI呼び出し
      const response = await fetch(apiEndpoint);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ ${sector}エラー詳細:`, errorText);
        throw new Error(`${sector}セクタースキャンに失敗しました (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      if (data.results && data.results.length > 0) {
        // 通常の結果 + 惜しい銘柄をまとめて表示
        let allResults = [...data.results];
        if (data.near_miss_stocks && data.near_miss_stocks.length > 0) {
          allResults = [...allResults, ...data.near_miss_stocks];
        }
        setResults(allResults);
      } else if (data.near_miss_stocks && data.near_miss_stocks.length > 0) {
        // 条件合致なし、惜しい銘柄のみ
        setResults(data.near_miss_stocks);
      } else {
        const scanned = data.total_scanned || data.processed_count || '不明';
        setError(`${sector}: ${scanned}銘柄をスキャンしましたが、条件に合致する銘柄が見つかりませんでした`);
        setResults([]);
      }
    } catch (err) {
      console.error(`🔥 ${sector}エラー:`, err);
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const executeTechSector = () => executeSectorScan('sectorTech', '/api/sector-scan-tech');
  const executeFinanceSector = () => executeSectorScan('sectorFinance', '/api/sector-scan-finance');
  const executeManufacturingSector = () => executeSectorScan('sectorManufacturing', '/api/sector-scan-manufacturing');
  const executeConsumerSector = () => executeSectorScan('sectorConsumer', '/api/sector-scan-consumer');
  const executeInfraSector = () => executeSectorScan('sectorInfra', '/api/sector-scan-infrastructure');
  const executeTestSector = () => executeSectorScan('test', '/api/test-sector');

  const renderLogicADetails = (details: LogicADetails) => (
    <Box sx={{ mt: 2, p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#2563eb' }}>
        🔍 ロジックA該当 ({details.score}pt)
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        <Typography variant="body2">
          ✓ 上場日: {details.listingDate} ({calculateYearsFromListing(details.listingDate)})
        </Typography>
        <Typography variant="body2">
          ✓ {getEarningsQuarter(details.earningsDate)}決算発表: {details.earningsDate}
        </Typography>
        <Typography variant="body2">
          ✓ 翌日ストップ高張付: {details.stopHighDate}
        </Typography>
        <Typography variant="body2">
          ✓ 前日終値: {details.prevPrice.toLocaleString()}円 → S高: {details.stopHighPrice.toLocaleString()}円
        </Typography>
        {details.isFirstTime && (
          <Typography variant="body2" sx={{ color: '#059669' }}>
            ✓ 上場後初回条件達成
          </Typography>
        )}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {details.noConsecutive && (
            <Typography variant="body2" sx={{ color: '#dc2626' }}>
              ✗ 2連続S高なし
            </Typography>
          )}
          {details.noLongTail && (
            <Typography variant="body2" sx={{ color: '#dc2626' }}>
              ✗ 長い下髭なし
            </Typography>
          )}
        </Box>
      </Box>
    </Box>
  );

  const renderLogicBDetails = (details: LogicBDetails) => (
    <Box sx={{ mt: 2, p: 2, bgcolor: '#f0fdf4', borderRadius: 2 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#059669' }}>
        🔍 ロジックB該当 ({details.score}pt)
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        <Typography variant="body2">
          ✓ 経常利益: {details.profitChange}
        </Typography>
        <Typography variant="body2">
          ✓ 黒字転換確定: {details.blackInkDate}
        </Typography>
        <Typography variant="body2">
          ✓ 5日線上抜け: {details.maBreakDate}
        </Typography>
        <Typography variant="body2">
          ✓ 出来高: 平均{details.volumeRatio}倍 (急増シグナル)
        </Typography>
      </Box>
    </Box>
  );

  const calculateYearsFromListing = (listingDate: string): string => {
    const listing = new Date(listingDate);
    const now = new Date();
    const diffMonths = (now.getFullYear() - listing.getFullYear()) * 12 + (now.getMonth() - listing.getMonth());
    const years = Math.floor(diffMonths / 12);
    const months = diffMonths % 12;
    return `${years}年${months}ヶ月経過`;
  };

  const getEarningsQuarter = (earningsDate: string): string => {
    const date = new Date(earningsDate);
    const month = date.getMonth() + 1;
    if (month <= 3) return 'Q4';
    if (month <= 6) return 'Q1';
    if (month <= 9) return 'Q2';
    return 'Q3';
  };

  return (
    <Box 
      component="main"
      role="main"
      data-testid="dashboard-container"
      sx={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        p: { xs: 2, sm: 3, md: 4 }
      }}>
      {/* ヘッダー */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontSize: { xs: '1.75rem', sm: '2rem', md: '2.5rem' },
            fontWeight: 700,
            color: '#1e293b',
            mb: 1
          }}
        >
          Stock Harvest AI
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            color: '#64748b', 
            fontSize: { xs: '1rem', sm: '1.1rem' },
            fontWeight: 400,
            mb: 2
          }}
        >
          手動スキャン型投資支援ツール
        </Typography>
        
        {/* スマートスケジュール情報 */}
        {scheduleInfo && (
          <Box sx={{ 
            bgcolor: scheduleInfo.scan_recommended ? '#f0f9ff' : '#fffbeb', 
            border: `1px solid ${scheduleInfo.scan_recommended ? '#0ea5e9' : '#f59e0b'}`,
            borderRadius: 2, 
            p: 2, 
            mb: 2,
            maxWidth: '700px',
            mx: 'auto'
          }}>
            <Typography variant="body2" sx={{ 
              color: scheduleInfo.scan_recommended ? '#0369a1' : '#92400e', 
              fontWeight: 600, 
              mb: 1 
            }}>
              {scheduleInfo.scan_recommended ? '🎯 決算発表集中期間' : '📅 決算発表期間外'}
            </Typography>
            <Typography variant="body2" sx={{ 
              color: scheduleInfo.scan_recommended ? '#0369a1' : '#92400e', 
              lineHeight: 1.6,
              mb: 1
            }}>
              {scheduleInfo.current_status?.message}
            </Typography>
            {scheduleInfo.scan_recommended ? (
              <Typography variant="body2" sx={{ color: '#059669', fontWeight: 600 }}>
                ✨ 推奨: 毎日のスキャンで最適な投資機会を発掘
              </Typography>
            ) : (
              <Typography variant="body2" sx={{ color: '#d97706', fontWeight: 600 }}>
                🛡️ API温存: 次の決算期間まで {scheduleInfo.next_target?.days_until}日 ({scheduleInfo.next_target?.date})
              </Typography>
            )}
          </Box>
        )}
        
        {/* 操作ガイド */}
        <Box sx={{ 
          bgcolor: '#f8fafc', 
          border: '1px solid #e2e8f0',
          borderRadius: 2, 
          p: 2, 
          mb: 2,
          maxWidth: '600px',
          mx: 'auto'
        }}>
          <Typography variant="body2" sx={{ color: '#475569', fontWeight: 600, mb: 1 }}>
            📋 使い方ガイド
          </Typography>
          <Typography variant="body2" sx={{ color: '#64748b', lineHeight: 1.6 }}>
            ① <strong>リアルタイム分析:</strong> 上段3ボタンでロジック別分析<br/>
            ② <strong>セクター分析:</strong> 下段5ボタンで業界別特化スキャン<br/>
            ③ <strong>共通条件:</strong> ①決算絡み ②時価総額500億円以下 ③出来高1000株以上/日 ④株価5000円以下<br/>
            ④ <strong>結果表示:</strong> ロジックは30秒、セクターは4分で上位投資候補銘柄を表示
          </Typography>
        </Box>
      </Box>

      {/* 基本分析ボタン */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center',
        gap: { xs: 2, sm: 3 },
        mb: 4,
        flexWrap: 'wrap'
      }}>
        <Typography variant="h6" sx={{ 
          width: '100%', 
          textAlign: 'center', 
          color: '#64748b', 
          mb: 2,
          fontSize: { xs: '1rem', sm: '1.1rem' }
        }}>
          📈 リアルタイム株式分析
        </Typography>
        
        <Button
          variant={activeLogic === 'A' ? 'contained' : 'outlined'}
          startIcon={<LogicAIcon />}
          onClick={executeLogicA}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '120px', sm: '140px' },
            height: '50px',
            fontSize: { xs: '1rem', sm: '1.1rem' },
            background: activeLogic === 'A' ? 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)' : undefined,
            color: activeLogic === 'A' ? 'white' : undefined
          }}
        >
          ロジックA
        </Button>
        <Button
          variant={activeLogic === 'B' ? 'contained' : 'outlined'}
          startIcon={<LogicBIcon />}
          onClick={executeLogicB}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '120px', sm: '140px' },
            height: '50px',
            fontSize: { xs: '1rem', sm: '1.1rem' },
            background: activeLogic === 'B' ? 'linear-gradient(135deg, #059669 0%, #047857 100%)' : undefined,
            color: activeLogic === 'B' ? 'white' : undefined
          }}
        >
          ロジックB
        </Button>
        <Button
          variant={activeLogic === 'combined' ? 'contained' : 'outlined'}
          startIcon={<CombinedIcon />}
          onClick={executeCombined}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '120px', sm: '140px' },
            height: '50px',
            fontSize: { xs: '1rem', sm: '1.1rem' },
            background: activeLogic === 'combined' ? 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)' : undefined,
            color: activeLogic === 'combined' ? 'white' : undefined
          }}
        >
          総合判断
        </Button>
      </Box>

      {/* セクター別スキャンボタン */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center',
        gap: { xs: 1, sm: 1.5 },
        mb: 4,
        flexWrap: 'wrap'
      }}>
        <Typography variant="h6" sx={{ 
          width: '100%', 
          textAlign: 'center', 
          color: '#64748b', 
          mb: 1,
          fontSize: { xs: '1rem', sm: '1.1rem' }
        }}>
          📊 セクター別特化スキャン（全９，０００銘柄から業界特化）
        </Typography>
        <Typography variant="body2" sx={{ 
          width: '100%', 
          textAlign: 'center', 
          color: '#94a3b8', 
          mb: 2,
          fontSize: '0.9rem'
        }}>
          💡 操作手順: セクターボタンをクリック → 約4分待機（全銘柄スキャン） → 結果表示
        </Typography>
        
        <Button
          variant={activeLogic === 'sectorTech' ? 'contained' : 'outlined'}
          startIcon={<TechIcon />}
          onClick={executeTechSector}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '90px', sm: '110px' },
            height: '44px',
            fontSize: { xs: '0.8rem', sm: '0.9rem' },
            background: activeLogic === 'sectorTech' ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : undefined,
            color: activeLogic === 'sectorTech' ? 'white' : undefined
          }}
        >
          テック
        </Button>
        
        <Button
          variant={activeLogic === 'sectorFinance' ? 'contained' : 'outlined'}
          startIcon={<FinanceIcon />}
          onClick={executeFinanceSector}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '90px', sm: '110px' },
            height: '44px',
            fontSize: { xs: '0.8rem', sm: '0.9rem' },
            background: activeLogic === 'sectorFinance' ? 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)' : undefined,
            color: activeLogic === 'sectorFinance' ? 'white' : undefined
          }}
        >
          金融
        </Button>
        
        <Button
          variant={activeLogic === 'sectorManufacturing' ? 'contained' : 'outlined'}
          startIcon={<ManufacturingIcon />}
          onClick={executeManufacturingSector}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '90px', sm: '110px' },
            height: '44px',
            fontSize: { xs: '0.8rem', sm: '0.9rem' },
            background: activeLogic === 'sectorManufacturing' ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' : undefined,
            color: activeLogic === 'sectorManufacturing' ? 'white' : undefined
          }}
        >
          製造業
        </Button>
        
        <Button
          variant={activeLogic === 'sectorConsumer' ? 'contained' : 'outlined'}
          startIcon={<ConsumerIcon />}
          onClick={executeConsumerSector}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '90px', sm: '110px' },
            height: '44px',
            fontSize: { xs: '0.8rem', sm: '0.9rem' },
            background: activeLogic === 'sectorConsumer' ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : undefined,
            color: activeLogic === 'sectorConsumer' ? 'white' : undefined
          }}
        >
          消費・食品
        </Button>
        
        <Button
          variant={activeLogic === 'sectorInfra' ? 'contained' : 'outlined'}
          startIcon={<InfraIcon />}
          onClick={executeInfraSector}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '90px', sm: '110px' },
            height: '44px',
            fontSize: { xs: '0.8rem', sm: '0.9rem' },
            background: activeLogic === 'sectorInfra' ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' : undefined,
            color: activeLogic === 'sectorInfra' ? 'white' : undefined
          }}
        >
          インフラ
        </Button>
        
        <Button
          variant="outlined"
          onClick={executeTestSector}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '90px', sm: '110px' },
            height: '44px',
            fontSize: { xs: '0.8rem', sm: '0.9rem' },
            borderColor: '#ef4444',
            color: '#ef4444',
            '&:hover': {
              borderColor: '#dc2626',
              backgroundColor: '#fef2f2'
            }
          }}
        >
          🧪 テスト
        </Button>
      </Box>

      {/* ローディング状態 */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={24} />
            <Typography>
              {activeLogic === 'A' ? 'ロジックA' : 
               activeLogic === 'B' ? 'ロジックB' : 
               activeLogic === 'combined' ? '総合判断' : 
               activeLogic === 'sectorTech' ? 'テック・情報通信セクター' :
               activeLogic === 'sectorFinance' ? '金融・銀行セクター' :
               activeLogic === 'sectorManufacturing' ? '製造業セクター' :
               activeLogic === 'sectorConsumer' ? '消費・食品セクター' :
               activeLogic === 'sectorInfra' ? 'インフラ・運輸セクター' :
               'テスト'}スキャン実行中...
            </Typography>
          </Box>
        </Box>
      )}

      {/* エラー・検出結果なし表示 */}
      {error && (
        <Alert severity="info" sx={{ mb: 4, textAlign: 'left' }}>
          <Typography component="pre" sx={{ 
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            lineHeight: 1.6,
            margin: 0,
            whiteSpace: 'pre-wrap'
          }}>
            {error}
          </Typography>
        </Alert>
      )}

      {/* 結果表示 */}
      {results.length > 0 && (
        <Box sx={{ maxWidth: '800px', mx: 'auto' }}>
          <Typography variant="h5" sx={{ mb: 3, textAlign: 'center', fontWeight: 600 }}>
            スキャン結果 ({results.length}銘柄)
          </Typography>
          
          {results.map((stock) => (
            <Card key={stock.code} sx={{ mb: 3, boxShadow: 3 }}>
              <CardContent>
                {/* 銘柄ヘッダー */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      📈 {stock.code} {stock.name}
                    </Typography>
                  </Box>
                  <Chip 
                    label={`総合スコア: ${stock.score}pt`}
                    color={stock.category === '惜しい銘柄' ? 'default' : stock.score >= 80 ? 'error' : stock.score >= 60 ? 'warning' : 'info'}
                    sx={{ fontWeight: 600 }}
                  />
                </Box>

                {/* ロジックA詳細 */}
                {stock.logicA && renderLogicADetails(stock.logicA)}

                {/* ロジックB詳細 */}
                {stock.logicB && renderLogicBDetails(stock.logicB)}

                {/* 総合判断の場合の特別表示 */}
                {activeLogic === 'combined' && stock.logicA && stock.logicB && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: '#fef3c7', borderRadius: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#92400e' }}>
                      ⭐ 両ロジック該当で最優先銘柄！
                    </Typography>
                  </Box>
                )}

                {/* 総合判断の詳細表示 */}
                {activeLogic === 'combined' && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: '#fffbeb', borderRadius: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#ea580c', mb: 1 }}>
                      🚀 リアルタイム総合分析結果
                    </Typography>
                    {stock.priority_level && (
                      <Chip 
                        label={`${stock.priority_level}レベル`}
                        color={stock.priority_level === '最優先' ? 'error' : 
                               stock.priority_level === '優先' ? 'warning' : 'info'}
                        sx={{ mr: 1, mb: 1 }}
                      />
                    )}
                    {stock.bonuses && stock.bonuses.length > 0 && (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                        {stock.bonuses.map((bonus, index) => (
                          <Chip 
                            key={index}
                            label={bonus}
                            size="small"
                            sx={{ 
                              backgroundColor: '#fed7aa',
                              color: '#ea580c',
                              fontSize: '0.75rem'
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    {stock.analysis_summary && (
                      <Typography variant="body2" sx={{ mt: 1, color: '#92400e' }}>
                        ロジックA: {stock.analysis_summary.logic_a_score}pt / 
                        ロジックB: {stock.analysis_summary.logic_b_score}pt / 
                        条件数: {stock.analysis_summary.total_conditions_met}個
                      </Typography>
                    )}
                  </Box>
                )}

                {/* セクター別スキャンの場合の特別表示 */}
                {(activeLogic?.startsWith('sector')) && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: '#f0f9ff', borderRadius: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#0369a1', mb: 1 }}>
                      🎯 {stock.sector}セクター分析結果
                    </Typography>
                    {stock.bonuses && stock.bonuses.length > 0 && (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                        {stock.bonuses.map((bonus, index) => (
                          <Chip 
                            key={index}
                            label={bonus}
                            size="small"
                            sx={{ 
                              backgroundColor: '#dbeafe',
                              color: '#0369a1',
                              fontSize: '0.75rem'
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    {stock.analysis_summary && (
                      <Typography variant="body2" sx={{ mt: 1, color: '#0369a1' }}>
                        セクター内ランキング | ロジックA: {stock.analysis_summary.logic_a_score}pt / 
                        ロジックB: {stock.analysis_summary.logic_b_score}pt
                      </Typography>
                    )}
                  </Box>
                )}

                {/* 惜しい銘柄の表示 */}
                {stock.category === '惜しい銘柄' && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: '#fffbf0', borderRadius: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#d97706', mb: 1 }}>
                      📊 惜しい銘柄 - 条件惜しく未達
                    </Typography>
                    {stock.near_miss_reasons && (
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {stock.near_miss_reasons.map((reason, index) => (
                          <Typography key={index} variant="body2" sx={{ color: '#92400e' }}>
                            • {reason}
                          </Typography>
                        ))}
                      </Box>
                    )}
                    <Typography variant="body2" sx={{ mt: 1, color: '#d97706', fontStyle: 'italic' }}>
                      ※ 条件を満たせば有力候補の可能性あり
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* 初回表示メッセージ */}
      {!loading && results.length === 0 && !error && (
        <Box sx={{ textAlign: 'center', mt: 8 }}>
          <Typography variant="h6" sx={{ color: '#64748b', mb: 2 }}>
            スキャンボタンを押して検索を開始してください
          </Typography>
          <Typography variant="body1" sx={{ color: '#94a3b8' }}>
            <strong>ロジックA:</strong> ストップ高張り付き精密検出<br/>
            <strong>ロジックB:</strong> 黒字転換銘柄精密検出<br/>
            <strong>総合判断:</strong> A+B の最適化分析<br/>
            <strong>セクター別:</strong> 各業界専門銘柄群を深掘り分析
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SimpleDashboardPage;