import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Chip,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import type { ManualScoreValue } from '@/types';
import { useScoreEvaluation } from '@/hooks/useScoreEvaluation';
import { logger } from '@/lib/logger';

interface ScoreEvaluationSectionProps {
  stockCode: string;
  stockName: string;
  logicType: 'logic_a' | 'logic_b';
  onEvaluationSaved?: () => void;
}

const SCORE_OPTIONS: Array<{ 
  value: ManualScoreValue; 
  label: string;
}> = [
  { value: 'S', label: 'S' },
  { value: 'A+', label: 'A+' },
  { value: 'A', label: 'A' },
  { value: 'B', label: 'B' },
  { value: 'C', label: 'C' }
];

export const ScoreEvaluationSection: React.FC<ScoreEvaluationSectionProps> = ({
  stockCode,
  logicType,
  onEvaluationSaved
}) => {
  const {
    currentEvaluation,
    history,
    aiCalculationStatus,
    loading,
    error,
    formData,
    canSaveEvaluation,
    saveEvaluation,
    startAICalculation,
    updateFormData
  } = useScoreEvaluation(stockCode);

  // スコア選択
  const handleScoreSelect = (score: ManualScoreValue) => {
    logger.debug('Score selected', { stockCode, score });
    updateFormData({ selectedScore: score });
  };

  // 理由入力
  const handleReasonChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const reason = event.target.value;
    updateFormData({ evaluationReason: reason });
  };

  // 評価保存
  const handleSaveEvaluation = async () => {
    if (!formData.selectedScore) return;

    try {
      logger.info('Saving score evaluation', {
        stockCode,
        score: formData.selectedScore,
        logicType
      });

      await saveEvaluation(
        stockCode,
        formData.selectedScore,
        formData.evaluationReason,
        logicType
      );

      // AI計算開始
      startAICalculation(stockCode);

      onEvaluationSaved?.();

      logger.info('Score evaluation saved and AI calculation started', { stockCode });
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Failed to save score evaluation', {
        error: error.message,
        stockCode
      });
    }
  };

  // 履歴項目のレンダリング
  const renderHistoryItem = (item: typeof history[0]) => {
    const timestamp = new Date(item.changedAt).toLocaleString('ja-JP', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });

    const getScoreColor = (score: ManualScoreValue): 'success' | 'info' | 'warning' | 'error' => {
      switch (score) {
        case 'S':
        case 'A+':
          return 'success';
        case 'A':
          return 'info';
        case 'B':
          return 'warning';
        case 'C':
          return 'error';
        default:
          return 'info';
      }
    };

    return (
      <Box
        key={item.id}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          py: 1,
          px: 2,
          backgroundColor: '#f8fffe',
          borderRadius: 1,
          fontSize: '0.875rem'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          {timestamp}:
        </Typography>
        
        {item.oldScore && (
          <>
            <Chip
              label={item.oldScore}
              size="small"
              color={getScoreColor(item.oldScore)}
              sx={{ height: 20, fontSize: '0.75rem' }}
            />
            <Typography variant="body2" color="text.secondary">
              →
            </Typography>
          </>
        )}
        
        <Chip
          label={item.newScore}
          size="small"
          color={getScoreColor(item.newScore)}
          sx={{ height: 20, fontSize: '0.75rem' }}
        />
        
        <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
          {item.changeReason || '理由なし'}
        </Typography>
      </Box>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={2}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        評価データの読み込みに失敗しました: {error.message}
      </Alert>
    );
  }

  return (
    <Paper
      sx={{
        mt: 3,
        p: 3,
        backgroundColor: '#edf7ed',
        border: '1px solid #c6f6d5',
        borderRadius: 2
      }}
    >
      {/* ヘッダー */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#2d3748' }}>
          手動スコア評価
        </Typography>

        {/* AI計算中表示 */}
        {aiCalculationStatus.isCalculating && (
          <Chip
            icon={<CircularProgress size={14} sx={{ color: 'white !important' }} />}
            label="AI計算中..."
            variant="filled"
            sx={{
              backgroundColor: '#38a169',
              color: 'white',
              fontWeight: 500
            }}
          />
        )}
      </Box>

      {/* 現在の評価表示 */}
      {currentEvaluation && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            現在の評価:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={currentEvaluation.score}
              color={
                currentEvaluation.score === 'S' || currentEvaluation.score === 'A+' ? 'success' :
                currentEvaluation.score === 'A' ? 'info' :
                currentEvaluation.score === 'B' ? 'warning' : 'error'
              }
            />
            <Typography variant="body2" color="text.secondary">
              {currentEvaluation.reason}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
              {new Date(currentEvaluation.evaluatedAt).toLocaleString('ja-JP')}
            </Typography>
          </Box>
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* 評価フォーム */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 2, alignItems: 'start' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* スコア選択ボタン */}
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              スコア選択:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {SCORE_OPTIONS.map(({ value, label }) => (
                <Button
                  key={value}
                  variant={formData.selectedScore === value ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleScoreSelect(value)}
                  sx={{
                    minWidth: 50,
                    height: 36,
                    borderColor: formData.selectedScore === value ? undefined : '#e2e8f0',
                    backgroundColor: formData.selectedScore === value ? '#38a169' : 'white',
                    color: formData.selectedScore === value ? 'white' : '#2d3748',
                    '&:hover': {
                      borderColor: '#38a169',
                      backgroundColor: formData.selectedScore === value ? '#2f855a' : 'rgba(56, 161, 105, 0.04)'
                    }
                  }}
                >
                  {label}
                </Button>
              ))}
            </Box>
          </Box>

          {/* 理由入力 */}
          <TextField
            multiline
            rows={2}
            placeholder="評価理由を入力..."
            value={formData.evaluationReason}
            onChange={handleReasonChange}
            inputProps={{ maxLength: 200 }}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'white',
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#38a169'
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#38a169'
                }
              }
            }}
          />
        </Box>

        {/* 保存ボタン */}
        <Button
          variant="contained"
          onClick={handleSaveEvaluation}
          disabled={!canSaveEvaluation}
          sx={{
            backgroundColor: '#38a169',
            '&:hover': {
              backgroundColor: '#2f855a'
            },
            '&:disabled': {
              backgroundColor: '#a0aec0'
            }
          }}
        >
          保存
        </Button>
      </Box>

      {/* 履歴表示 */}
      {history.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
            最近の評価履歴
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: 1,
              maxHeight: 150,
              overflowY: 'auto',
              backgroundColor: 'white',
              borderRadius: 1,
              border: '1px solid #e2e8f0',
              p: 1
            }}
          >
            {history.map(renderHistoryItem)}
          </Box>
        </Box>
      )}
    </Paper>
  );
};