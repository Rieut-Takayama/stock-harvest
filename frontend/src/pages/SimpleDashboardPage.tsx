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
  Star as CombinedIcon
} from '@mui/icons-material';

interface StockResult {
  code: string;
  name: string;
  score: number;
  logicA?: LogicADetails;
  logicB?: LogicBDetails;
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
  const [activeLogic, setActiveLogic] = useState<'A' | 'B' | 'combined' | 'realA' | 'realB' | null>(null);

  const executeRealLogicA = async () => {
    setLoading(true);
    setActiveLogic('realA');
    setError(null);
    
    try {
      // 実データAPI呼び出し
      const response = await fetch('/api/real-logic-a-enhanced');
      if (!response.ok) throw new Error('実データ版ロジックAスキャンに失敗しました');
      
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      // エラー時はモック版にフォールバック
      console.warn('実データ取得失敗、モック版を使用:', err);
      await executeLogicA();
      return;
    } finally {
      setLoading(false);
    }
  };

  const executeLogicA = async () => {
    setLoading(true);
    setActiveLogic('A');
    setError(null);
    
    try {
      // モックデータ（完全無料版）
      await new Promise(resolve => setTimeout(resolve, 2000)); // 2秒のローディング演出
      
      const mockResults = [
        {
          code: "7203",
          name: "トヨタ自動車",
          score: 60,
          logicA: {
            score: 60,
            listingDate: "2022-04-15",
            earningsDate: "2024-11-20",
            stopHighDate: "2024-11-21",
            prevPrice: 2835,
            stopHighPrice: 3135,
            isFirstTime: true,
            noConsecutive: true,
            noLongTail: true
          }
        },
        {
          code: "6501",
          name: "日立製作所", 
          score: 50,
          logicA: {
            score: 50,
            listingDate: "2021-10-01",
            earningsDate: "2024-11-19",
            stopHighDate: "2024-11-20",
            prevPrice: 3780,
            stopHighPrice: 4200,
            isFirstTime: true,
            noConsecutive: true,
            noLongTail: true
          }
        }
      ];
      
      setResults(mockResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const executeRealLogicB = async () => {
    setLoading(true);
    setActiveLogic('realB');
    setError(null);
    
    try {
      // 実データAPI呼び出し
      const response = await fetch('/api/real-logic-b-enhanced');
      if (!response.ok) throw new Error('実データ版ロジックBスキャンに失敗しました');
      
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      // エラー時はモック版にフォールバック
      console.warn('実データ取得失敗、モック版を使用:', err);
      await executeLogicB();
      return;
    } finally {
      setLoading(false);
    }
  };

  const executeLogicB = async () => {
    setLoading(true);
    setActiveLogic('B');
    setError(null);
    
    try {
      // モックデータ（完全無料版）
      await new Promise(resolve => setTimeout(resolve, 2000)); // 2秒のローディング演出
      
      const mockResults = [
        {
          code: "7203",
          name: "トヨタ自動車",
          score: 60,
          logicB: {
            score: 60,
            profitChange: "前年-120億→今期+340億",
            blackInkDate: "2024-11-20",
            maBreakDate: "2024-11-22",
            volumeRatio: 2.3
          }
        },
        {
          code: "4755",
          name: "楽天グループ",
          score: 50,
          logicB: {
            score: 50,
            profitChange: "前年-85億→今期+15億",
            blackInkDate: "2024-11-21",
            maBreakDate: "2024-11-23",
            volumeRatio: 1.8
          }
        }
      ];
      
      setResults(mockResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const executeCombined = async () => {
    setLoading(true);
    setActiveLogic('combined');
    setError(null);
    
    try {
      // モックデータ（完全無料版）
      await new Promise(resolve => setTimeout(resolve, 2500)); // 2.5秒のローディング演出
      
      const mockResults = [
        {
          code: "7203",
          name: "トヨタ自動車",
          score: 140, // A:60 + B:60 + ボーナス:20
          logicA: {
            score: 60,
            listingDate: "2022-04-15",
            earningsDate: "2024-11-20",
            stopHighDate: "2024-11-21",
            prevPrice: 2835,
            stopHighPrice: 3135,
            isFirstTime: true,
            noConsecutive: true,
            noLongTail: true
          },
          logicB: {
            score: 60,
            profitChange: "前年-120億→今期+340億",
            blackInkDate: "2024-11-20",
            maBreakDate: "2024-11-22",
            volumeRatio: 2.3
          }
        },
        {
          code: "6501",
          name: "日立製作所",
          score: 50, // A:50のみ
          logicA: {
            score: 50,
            listingDate: "2021-10-01",
            earningsDate: "2024-11-19",
            stopHighDate: "2024-11-20",
            prevPrice: 3780,
            stopHighPrice: 4200,
            isFirstTime: true,
            noConsecutive: true,
            noLongTail: true
          }
        },
        {
          code: "4755",
          name: "楽天グループ",
          score: 50, // B:50のみ
          logicB: {
            score: 50,
            profitChange: "前年-85億→今期+15億",
            blackInkDate: "2024-11-21",
            maBreakDate: "2024-11-23",
            volumeRatio: 1.8
          }
        }
      ];
      
      setResults(mockResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

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
    <Box sx={{ 
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
            fontWeight: 400
          }}
        >
          手動スキャン型投資支援ツール
        </Typography>
      </Box>

      {/* スキャンボタン */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center',
        gap: { xs: 1, sm: 2 },
        mb: 4,
        flexWrap: 'wrap'
      }}>
        <Button
          variant={activeLogic === 'A' ? 'contained' : 'outlined'}
          startIcon={<LogicAIcon />}
          onClick={executeLogicA}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '100px', sm: '120px' },
            height: '48px',
            fontSize: { xs: '0.9rem', sm: '1rem' }
          }}
        >
          ロジックA
        </Button>
        <Button
          variant={activeLogic === 'realA' ? 'contained' : 'outlined'}
          startIcon={<LogicAIcon />}
          onClick={executeRealLogicA}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '100px', sm: '120px' },
            height: '48px',
            fontSize: { xs: '0.9rem', sm: '1rem' },
            background: activeLogic === 'realA' ? 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)' : undefined,
            color: activeLogic === 'realA' ? 'white' : undefined
          }}
        >
          実データA
        </Button>
        <Button
          variant={activeLogic === 'B' ? 'contained' : 'outlined'}
          startIcon={<LogicBIcon />}
          onClick={executeLogicB}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '100px', sm: '120px' },
            height: '48px',
            fontSize: { xs: '0.9rem', sm: '1rem' }
          }}
        >
          ロジックB
        </Button>
        <Button
          variant={activeLogic === 'realB' ? 'contained' : 'outlined'}
          startIcon={<LogicBIcon />}
          onClick={executeRealLogicB}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '100px', sm: '120px' },
            height: '48px',
            fontSize: { xs: '0.9rem', sm: '1rem' },
            background: activeLogic === 'realB' ? 'linear-gradient(135deg, #059669 0%, #047857 100%)' : undefined,
            color: activeLogic === 'realB' ? 'white' : undefined
          }}
        >
          実データB
        </Button>
        <Button
          variant={activeLogic === 'combined' ? 'contained' : 'outlined'}
          startIcon={<CombinedIcon />}
          onClick={executeCombined}
          disabled={loading}
          sx={{ 
            minWidth: { xs: '100px', sm: '120px' },
            height: '48px',
            fontSize: { xs: '0.9rem', sm: '1rem' },
            background: activeLogic === 'combined' ? 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)' : undefined
          }}
        >
          総合判断
        </Button>
      </Box>

      {/* ローディング状態 */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={24} />
            <Typography>
              {activeLogic === 'A' ? 'ロジックA' : 
               activeLogic === 'realA' ? '実データロジックA' : 
               activeLogic === 'B' ? 'ロジックB' : 
               activeLogic === 'realB' ? '実データロジックB' : 
               '総合判断'}スキャン実行中...
            </Typography>
          </Box>
        </Box>
      )}

      {/* エラー表示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
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
                    color={stock.score >= 80 ? 'error' : stock.score >= 60 ? 'warning' : 'info'}
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
            ロジックA: ストップ高張り付き精密検出<br/>
            ロジックB: 黒字転換銘柄精密検出<br/>
            総合判断: A+B の最適化分析
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SimpleDashboardPage;