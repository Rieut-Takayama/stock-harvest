import React from 'react';
import type { ReactNode } from 'react';
import {
  Box,
  Chip,
  Typography,
  Paper
} from '@mui/material';

interface StockItem {
  code: string;
  name: string;
  status: string;
}

interface TopStocksProps {
  stocks?: StockItem[];
  children?: ReactNode;
}

export const TopStocks: React.FC<TopStocksProps> = ({
  children
}) => {
  return (
    <Paper sx={{ p: 3, borderRadius: 2, backgroundColor: 'white' }}>
      {/* ロジック検出結果ヘッダー */}
      <Typography variant="h5" sx={{ 
        mb: 3,
        fontWeight: 600,
        color: '#2d3748',
        textAlign: 'center'
      }}>
        ロジックA強化版 検出結果
      </Typography>

      {/* 検出結果テーブル */}
      <Box sx={{ mb: 3, overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8fffe' }}>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>銘柄コード</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>銘柄名</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>現在価格</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>変動率</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>シグナル</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e2e8f0', fontWeight: 600 }}>評価</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                <Typography sx={{ fontWeight: 600, color: '#38a169' }}>1234</Typography>
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>テクノロジー株式会社</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#38a169' }}>¥1,450</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#38a169' }}>+5.2%</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                <Chip label="買い" size="small" sx={{ backgroundColor: '#38a169', color: 'white', fontSize: '12px', fontWeight: 600 }} />
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>-</td>
            </tr>
            <tr>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                <Typography sx={{ fontWeight: 600, color: '#38a169' }}>5678</Typography>
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>グロース企業</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#38a169' }}>¥890</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#38a169' }}>+3.8%</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                <Chip label="注視" size="small" sx={{ backgroundColor: '#d69e2e', color: 'white', fontSize: '12px', fontWeight: 600 }} />
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>A+</td>
            </tr>
            <tr>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                <Typography sx={{ fontWeight: 600, color: '#38a169' }}>9012</Typography>
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>新興IT企業</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#e53e3e' }}>¥2,180</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0', color: '#e53e3e' }}>-1.2%</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>
                <Chip label="注視" size="small" sx={{ backgroundColor: '#d69e2e', color: 'white', fontSize: '12px', fontWeight: 600 }} />
              </td>
              <td style={{ padding: '12px', borderBottom: '1px solid #e2e8f0' }}>B</td>
            </tr>
          </tbody>
        </table>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', color: '#718096', fontSize: '14px' }}>
        最終更新: 2025-12-07 14:30
      </Box>

      {/* 子コンポーネント（手動スコア評価など）を表示 */}
      {children}
    </Paper>
  );
};

export default TopStocks;