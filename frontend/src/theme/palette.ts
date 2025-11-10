import type { PaletteOptions } from '@mui/material/styles';

/**
 * ナチュラルライトテーマ - カラーパレット定義
 * 自然の緑を基調とした穏やかで落ち着いたデザイン
 * 長時間の分析作業でもストレスを感じにくい配色
 */
export const naturalLightPalette: PaletteOptions = {
  mode: 'light',
  
  // プライマリカラー: 成長の緑
  primary: {
    main: '#38a169',      // メインの緑色
    light: '#68d391',     // ライトグリーン（ボタンホバー、アクセント用）
    dark: '#2f855a',      // ダークグリーン（フォーカス状態用）
    contrastText: '#ffffff',
  },
  
  // セカンダリカラー: 自然の調和
  secondary: {
    main: '#4caf50',      // 既存設定との互換性を保持
    light: '#81c784',
    dark: '#388e3c',
    contrastText: '#ffffff',
  },
  
  // エラーカラー: 損失を表現
  error: {
    main: '#e53e3e',      // 落ち着いた赤（下落表示）
    light: '#fc8181',
    dark: '#c53030',
    contrastText: '#ffffff',
  },
  
  // 警告カラー: 注意喚起
  warning: {
    main: '#d69e2e',      // 自然なオレンジ
    light: '#f6e05e',
    dark: '#b7791f',
    contrastText: '#1a202c',
  },
  
  // 情報カラー: データ表示
  info: {
    main: '#3182ce',      // ソフトブルー
    light: '#63b3ed',
    dark: '#2c5282',
    contrastText: '#ffffff',
  },
  
  // 成功カラー: 利益表示
  success: {
    main: '#38a169',      // プライマリと同じ緑色で統一感
    light: '#68d391',
    dark: '#2f855a',
    contrastText: '#ffffff',
  },
  
  // 背景色
  background: {
    default: '#f8fffe',   // ソフトホワイト（わずかにグリーンがかった白）
    paper: '#ffffff',     // 純白（カード背景）
  },
  
  // テキストカラー
  text: {
    primary: '#2d3748',   // ダークグレー（メインテキスト）
    secondary: '#4a5568', // ミディアムグレー（サブテキスト）
    disabled: '#a0aec0',  // ライトグレー（無効状態）
  },
  
  // 区切り線
  divider: '#e2e8f0',     // ライトグレー
  
  // アクションカラー
  action: {
    hover: 'rgba(56, 161, 105, 0.04)',      // プライマリカラーの薄い透明
    selected: 'rgba(56, 161, 105, 0.08)',   
    disabled: 'rgba(160, 174, 192, 0.3)',   
    disabledBackground: 'rgba(160, 174, 192, 0.12)',
    focus: 'rgba(56, 161, 105, 0.12)',
  },
  
  // 株式投資専用カラー
  common: {
    black: '#1a202c',
    white: '#ffffff',
  },
};

/**
 * 株式データ表示用のカスタムカラー
 * MUIテーマ拡張で使用
 */
export const stockColors = {
  // 価格変動表示用
  positive: '#38a169',    // 上昇（緑）
  negative: '#e53e3e',    // 下落（赤）
  neutral: '#4a5568',     // 変動なし（グレー）
  
  // 統計カード背景
  statCard: {
    background: '#edf7ed', // 薄いグリーン背景
    border: '#c6f6d5',     // ソフトグリーンボーダー
  },
  
  // アラート・通知用
  alert: {
    buy: '#38a169',        // 買いシグナル
    sell: '#e53e3e',       // 売りシグナル  
    watch: '#d69e2e',      // 注視
  },
  
  // チャート用カラーパレット
  chart: {
    line: '#38a169',       // メインライン
    area: 'rgba(56, 161, 105, 0.1)', // エリアの塗りつぶし
    grid: '#e2e8f0',       // グリッド線
    volume: '#68d391',     // 出来高バー
  },
};

// MUI v7対応 - TypeScript型拡張用の宣言
declare module '@mui/material/styles' {
  interface Palette {
    stock: typeof stockColors;
  }
  
  interface PaletteOptions {
    stock?: typeof stockColors;
  }
  
  // v7では必須の型拡張
  interface Theme {
    stock: typeof stockColors;
  }
  
  interface ThemeOptions {
    stock?: typeof stockColors;
  }
}