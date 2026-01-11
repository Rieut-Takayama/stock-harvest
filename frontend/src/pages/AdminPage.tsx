import { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Chip,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  CheckCircle,
  Error as ErrorIcon,
  Refresh,
  Save,
  Settings as SettingsIcon,
} from '@mui/icons-material';

/**
 * P-002: システム設定・管理ページ
 *
 * 要件定義準拠:
 * - バッチ処理ステータス確認
 * - 判定条件の微調整設定
 * - データソース接続状況確認
 */
export const AdminPage = () => {
  // バッチ処理ステータス（モックデータ）
  const [batchStatus] = useState({
    lastExecution: '2026-01-11 15:35:00',
    status: 'success',
    processedStocks: 3247,
    extractedStocks: 2,
    duration: '28.5秒',
  });

  // 判定パラメータ（モックデータ）
  const [parameters, setParameters] = useState({
    lowToCloseRatio: '0.01',
    yearsListedMax: '5',
    stopHighMatchStrict: 'true',
  });

  // データソース接続状況（モックデータ）
  const [dataSources] = useState([
    { name: 'Yahoo Finance API', status: 'connected', lastCheck: '2026-01-11 15:30:00' },
    { name: 'PostgreSQL (Neon)', status: 'connected', lastCheck: '2026-01-11 15:30:05' },
    { name: '決算カレンダーDB', status: 'connected', lastCheck: '2026-01-11 15:30:10' },
  ]);

  const handleParameterChange = (key: string, value: string) => {
    setParameters((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    alert('設定を保存しました（モック実装）');
  };

  const handleTestConnection = () => {
    alert('接続テストを実行しました（モック実装）');
  };

  return (
    <Box>
      {/* ヘッダー */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}>
          <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          システム設定・管理
        </Typography>
        <Typography variant="body2" color="text.secondary">
          バッチ処理の設定確認と条件パラメータの調整
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* バッチ処理ステータス */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                バッチ処理ステータス
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Chip
                  icon={batchStatus.status === 'success' ? <CheckCircle /> : <ErrorIcon />}
                  label={batchStatus.status === 'success' ? '正常実行' : 'エラー'}
                  color={batchStatus.status === 'success' ? 'success' : 'error'}
                  sx={{ mb: 2 }}
                />
              </Box>

              <List dense>
                <ListItem>
                  <ListItemText
                    primary="最終実行日時"
                    secondary={batchStatus.lastExecution}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="処理対象銘柄数"
                    secondary={`${batchStatus.processedStocks.toLocaleString()}銘柄`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="抽出結果銘柄数"
                    secondary={`${batchStatus.extractedStocks}銘柄`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText primary="実行時間" secondary={batchStatus.duration} />
                </ListItem>
              </List>

              <Button
                variant="outlined"
                startIcon={<Refresh />}
                fullWidth
                sx={{ mt: 2 }}
                onClick={() => window.location.reload()}
              >
                ステータス更新
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* データソース接続状況 */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                データソース接続状況
              </Typography>

              {dataSources.map((source, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                    <Typography variant="body1" sx={{ fontWeight: 500, flexGrow: 1 }}>
                      {source.name}
                    </Typography>
                    <Chip
                      icon={<CheckCircle />}
                      label="接続中"
                      color="success"
                      size="small"
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    最終確認: {source.lastCheck}
                  </Typography>
                  {index < dataSources.length - 1 && <Divider sx={{ mt: 2 }} />}
                </Box>
              ))}

              <Button
                variant="outlined"
                startIcon={<Refresh />}
                fullWidth
                sx={{ mt: 2 }}
                onClick={handleTestConnection}
              >
                接続テスト実行
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* 判定条件の微調整 */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                判定条件の微調整
              </Typography>

              <Alert severity="warning" sx={{ mb: 3 }}>
                これらのパラメータを変更すると、抽出される銘柄数が大幅に変動する可能性があります。
                慎重に調整してください。
              </Alert>

              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    label="安値終値比率"
                    value={parameters.lowToCloseRatio}
                    onChange={(e) => handleParameterChange('lowToCloseRatio', e.target.value)}
                    fullWidth
                    helperText="安値 < 終値 × [この値]"
                    type="number"
                    inputProps={{ step: '0.001', min: '0', max: '1' }}
                  />
                </Grid>

                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    label="上場年数上限"
                    value={parameters.yearsListedMax}
                    onChange={(e) => handleParameterChange('yearsListedMax', e.target.value)}
                    fullWidth
                    helperText="上場から[この値]年未満の銘柄"
                    type="number"
                    inputProps={{ step: '1', min: '0', max: '10' }}
                  />
                </Grid>

                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    label="ストップ高厳密判定"
                    value={parameters.stopHighMatchStrict}
                    onChange={(e) =>
                      handleParameterChange('stopHighMatchStrict', e.target.value)
                    }
                    fullWidth
                    helperText="始値=終値=ストップ高価格"
                    select
                    slotProps={{
                      select: {
                        native: true,
                      },
                    }}
                  >
                    <option value="true">有効</option>
                    <option value="false">無効</option>
                  </TextField>
                </Grid>
              </Grid>

              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleSave}
                  sx={{ flexGrow: 1 }}
                >
                  設定を保存
                </Button>
                <Button
                  variant="outlined"
                  onClick={() =>
                    setParameters({
                      lowToCloseRatio: '0.01',
                      yearsListedMax: '5',
                      stopHighMatchStrict: 'true',
                    })
                  }
                >
                  デフォルトに戻す
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
