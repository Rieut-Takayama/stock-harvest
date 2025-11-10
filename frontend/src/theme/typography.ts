// MUI v7対応のタイポグラフィ設定

/**
 * ナチュラルライトテーマ - タイポグラフィ設定
 * 読みやすく、長時間の利用でも目に優しいフォント設定
 * 株式データの可読性を重視した設計
 */
export const naturalLightTypography = {
  // フォントファミリー設定
  fontFamily: [
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    'Roboto',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"',
  ].join(','),
  
  // 基本フォントサイズ
  fontSize: 14,
  fontWeightLight: 300,
  fontWeightRegular: 400,
  fontWeightMedium: 500,
  fontWeightBold: 700,
  
  // 見出しスタイル
  h1: {
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
    color: '#2d3748',
    letterSpacing: '-0.025em',
    marginBottom: '1rem',
  },
  
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
    color: '#2d3748',
    letterSpacing: '-0.015em',
    marginBottom: '0.875rem',
  },
  
  h3: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.4,
    color: '#2d3748',
    letterSpacing: '-0.01em',
    marginBottom: '0.75rem',
  },
  
  h4: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
    color: '#2d3748',
    letterSpacing: '-0.005em',
    marginBottom: '0.625rem',
  },
  
  h5: {
    fontSize: '1.125rem',
    fontWeight: 600,
    lineHeight: 1.5,
    color: '#2d3748',
    marginBottom: '0.5rem',
  },
  
  h6: {
    fontSize: '1rem',
    fontWeight: 600,
    lineHeight: 1.5,
    color: '#2d3748',
    marginBottom: '0.5rem',
  },
  
  // サブタイトル
  subtitle1: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.6,
    color: '#4a5568',
    letterSpacing: '0.00938em',
  },
  
  subtitle2: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.6,
    color: '#4a5568',
    letterSpacing: '0.00714em',
  },
  
  // 本文テキスト
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.7,
    color: '#2d3748',
    letterSpacing: '0.00938em',
  },
  
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.6,
    color: '#4a5568',
    letterSpacing: '0.00714em',
  },
  
  // ボタンテキスト
  button: {
    fontSize: '0.875rem',
    fontWeight: 600,
    lineHeight: 1.5,
    textTransform: 'none' as const, // 日本語対応でtextTransformを無効化
    letterSpacing: '0.02857em',
  },
  
  // キャプション
  caption: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 1.4,
    color: '#718096',
    letterSpacing: '0.03333em',
  },
  
  // オーバーライン
  overline: {
    fontSize: '0.625rem',
    fontWeight: 600,
    lineHeight: 1.5,
    color: '#a0aec0',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.08333em',
  },
};

/**
 * 株式データ表示用カスタムタイポグラフィ
 */
export const stockTypography = {
  // 株価表示用
  stockPrice: {
    fontSize: '1.25rem',
    fontWeight: 700,
    lineHeight: 1.2,
    fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
    letterSpacing: '0.025em',
  },
  
  // 変動率表示用
  stockChange: {
    fontSize: '0.875rem',
    fontWeight: 600,
    lineHeight: 1.4,
    fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
  },
  
  // 銘柄コード表示用
  stockCode: {
    fontSize: '0.875rem',
    fontWeight: 600,
    lineHeight: 1.4,
    fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
    letterSpacing: '0.05em',
  },
  
  // 統計数値表示用
  statValue: {
    fontSize: '1.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
    fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
  },
  
  // ラベル表示用
  statLabel: {
    fontSize: '0.75rem',
    fontWeight: 500,
    lineHeight: 1.4,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.08333em',
    color: '#718096',
  },
  
  // ダッシュボードタイトル
  dashboardTitle: {
    fontSize: '1.875rem',
    fontWeight: 700,
    lineHeight: 1.2,
    color: '#38a169',
    letterSpacing: '-0.025em',
  },
};

// MUI v7対応 - TypeScript型拡張
declare module '@mui/material/styles' {
  interface TypographyVariants {
    stockPrice: React.CSSProperties;
    stockChange: React.CSSProperties;
    stockCode: React.CSSProperties;
    statValue: React.CSSProperties;
    statLabel: React.CSSProperties;
    dashboardTitle: React.CSSProperties;
  }

  interface TypographyVariantsOptions {
    stockPrice?: React.CSSProperties;
    stockChange?: React.CSSProperties;
    stockCode?: React.CSSProperties;
    statValue?: React.CSSProperties;
    statLabel?: React.CSSProperties;
    dashboardTitle?: React.CSSProperties;
  }
}

// MUI v7対応 - Typography Component Props拡張
declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    stockPrice: true;
    stockChange: true;
    stockCode: true;
    statValue: true;
    statLabel: true;
    dashboardTitle: true;
  }
}