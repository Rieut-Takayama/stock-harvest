import { createTheme } from '@mui/material/styles';
import { naturalLightPalette, stockColors } from './palette';
import { naturalLightTypography, stockTypography } from './typography';
import { naturalLightComponents } from './components';

/**
 * Stock Harvest AI - ナチュラルライトテーマ
 * 
 * 自然の緑を基調とした穏やかで落ち着いたデザインテーマ
 * - メインカラー: #38a169 (成長の緑)
 * - 特徴: 自然な色合いでリラックス効果
 * - 対象: リラックスした環境での投資判断
 * - 背景: ソフトなシャドウで上品な印象
 * 
 * @version 1.0.0
 * @author Stock Harvest AI Development Team
 */

// ベーステーマ作成（パレットとタイポグラフィ）
const baseTheme = createTheme({
  palette: {
    ...naturalLightPalette,
    // カスタム株式カラーを拡張
    stock: stockColors,
  },
  typography: {
    ...naturalLightTypography,
    // カスタム株式タイポグラフィを追加
    ...stockTypography,
  },
  spacing: 8, // デフォルトのspacing単位
  
  // カスタムブレイクポイント
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
  
  // シャドウの定義（ナチュラルライト向けにソフトに調整）
  shadows: [
    'none',
    '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
    '0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.08)',
    '0 8px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08)',
    '0 12px 32px rgba(0, 0, 0, 0.15), 0 6px 12px rgba(0, 0, 0, 0.1)',
    '0 16px 40px rgba(0, 0, 0, 0.18), 0 8px 16px rgba(0, 0, 0, 0.12)',
    '0 20px 48px rgba(0, 0, 0, 0.20), 0 10px 20px rgba(0, 0, 0, 0.14)',
    '0 24px 56px rgba(0, 0, 0, 0.22), 0 12px 24px rgba(0, 0, 0, 0.16)',
    '0 28px 64px rgba(0, 0, 0, 0.24), 0 14px 28px rgba(0, 0, 0, 0.18)',
    '0 32px 72px rgba(0, 0, 0, 0.26), 0 16px 32px rgba(0, 0, 0, 0.20)',
    '0 36px 80px rgba(0, 0, 0, 0.28), 0 18px 36px rgba(0, 0, 0, 0.22)',
    '0 40px 88px rgba(0, 0, 0, 0.30), 0 20px 40px rgba(0, 0, 0, 0.24)',
    '0 44px 96px rgba(0, 0, 0, 0.32), 0 22px 44px rgba(0, 0, 0, 0.26)',
    '0 48px 104px rgba(0, 0, 0, 0.34), 0 24px 48px rgba(0, 0, 0, 0.28)',
    '0 52px 112px rgba(0, 0, 0, 0.36), 0 26px 52px rgba(0, 0, 0, 0.30)',
    '0 56px 120px rgba(0, 0, 0, 0.38), 0 28px 56px rgba(0, 0, 0, 0.32)',
    '0 60px 128px rgba(0, 0, 0, 0.40), 0 30px 60px rgba(0, 0, 0, 0.34)',
    '0 64px 136px rgba(0, 0, 0, 0.42), 0 32px 64px rgba(0, 0, 0, 0.36)',
    '0 68px 144px rgba(0, 0, 0, 0.44), 0 34px 68px rgba(0, 0, 0, 0.38)',
    '0 72px 152px rgba(0, 0, 0, 0.46), 0 36px 72px rgba(0, 0, 0, 0.40)',
    '0 76px 160px rgba(0, 0, 0, 0.48), 0 38px 76px rgba(0, 0, 0, 0.42)',
    '0 80px 168px rgba(0, 0, 0, 0.50), 0 40px 80px rgba(0, 0, 0, 0.44)',
    '0 84px 176px rgba(0, 0, 0, 0.52), 0 42px 84px rgba(0, 0, 0, 0.46)',
    '0 88px 184px rgba(0, 0, 0, 0.54), 0 44px 88px rgba(0, 0, 0, 0.48)',
    '0 92px 192px rgba(0, 0, 0, 0.56), 0 46px 92px rgba(0, 0, 0, 0.50)',
  ],
  
  // zIndexの設定
  zIndex: {
    mobileStepper: 1000,
    fab: 1050,
    speedDial: 1050,
    appBar: 1100,
    drawer: 1200,
    modal: 1300,
    snackbar: 1400,
    tooltip: 1500,
  },
  
  // 形状の設定
  shape: {
    borderRadius: 8, // デフォルトのborderRadius
  },
  
  // トランジションの設定
  transitions: {
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
    },
  },
});

// コンポーネントオーバーライドを含む最終テーマ作成
export const naturalLightTheme = createTheme(baseTheme, {
  components: naturalLightComponents,
});

// テーマのデフォルトエクスポート
export default naturalLightTheme;

/**
 * テーマ情報とメタデータ
 */
export const themeInfo = {
  name: 'Natural Light Theme',
  displayName: 'ナチュラルライト',
  description: '自然の緑を基調とした穏やかで落ち着いたデザインテーマ',
  version: '1.0.0',
  author: 'Stock Harvest AI Development Team',
  colors: {
    primary: '#38a169',
    secondary: '#4caf50', 
    background: '#f8fffe',
    surface: '#ffffff',
  },
  features: [
    '自然な色合いでリラックス効果',
    'ソフトなシャドウで上品な印象',
    '長時間利用でも目に優しい配色',
    'リラックスした投資環境を演出',
    '株式データの可読性重視',
  ],
  target: 'リラックスした環境での投資判断',
  createdAt: new Date().toISOString(),
};

/**
 * カスタムフックとユーティリティ
 */

// テーマ使用状況の型定義
export type StockHarvestTheme = typeof naturalLightTheme;

// カスタムブレイクポイント使用フック
export const useThemeBreakpoints = () => {
  return naturalLightTheme.breakpoints;
};

// カスタムカラー取得ユーティリティ
export const getStockColor = (type: 'positive' | 'negative' | 'neutral') => {
  return stockColors[type];
};

// チャートカラー取得ユーティリティ
export const getChartColors = () => {
  return {
    line: stockColors.chart.line,
    area: stockColors.chart.area,
    grid: stockColors.chart.grid,
    volume: stockColors.chart.volume,
  };
};

// 統計カードスタイル取得ユーティリティ
export const getStatCardStyles = () => {
  return {
    backgroundColor: stockColors.statCard.background,
    border: `1px solid ${stockColors.statCard.border}`,
    borderRadius: naturalLightTheme.shape.borderRadius,
    padding: naturalLightTheme.spacing(2),
  };
};

/**
 * TypeScript型拡張のエクスポート
 */
export type { StockHarvestTheme as Theme };
export { stockColors, stockTypography };