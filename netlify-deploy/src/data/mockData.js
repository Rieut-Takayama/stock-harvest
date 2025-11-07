// ロジックA - ストップ高張り付き銘柄
const logicAStocks = [
  {
    code: "4180",
    name: "Appier Group",
    type: "新規上場銘柄",
    triggerDate: "2025-11-01",
    triggerEvent: "四半期決算発表",
    currentPrice: 1856,
    limitPrice: 2156,
    recommendedEntry: 2264, // +5% from limit
    stopLoss: null, // 3日連続下落後に設定
    target: 2830, // +25%
    status: "監視中",
    daysHeld: 2,
    currentReturn: -2.1
  },
  {
    code: "7342",
    name: "ウェルスナビ",
    type: "新規上場銘柄",
    triggerDate: "2025-10-28",
    triggerEvent: "業績修正発表",
    currentPrice: 945,
    limitPrice: 980,
    recommendedEntry: 1029,
    stopLoss: null,
    target: 1286,
    status: "エントリー済",
    daysHeld: 5,
    currentReturn: -8.2
  },
  {
    code: "5032",
    name: "ANYCOLOR",
    type: "新規上場銘柄",
    triggerDate: "2025-10-31",
    triggerEvent: "四半期決算発表",
    currentPrice: 3240,
    limitPrice: 3450,
    recommendedEntry: 3623,
    stopLoss: null,
    target: 4529,
    status: "エントリー待機",
    daysHeld: 0,
    currentReturn: 0
  }
];

// ロジックB - 赤字→黒字転換銘柄
const logicBStocks = [
  {
    code: "3681",
    name: "ブイキューブ",
    previousStatus: "前年度赤字",
    currentQuarter: "Q2黒字転換",
    ma5: 892,
    currentPrice: 905,
    recommendedEntry: 892,
    stopLoss: 803, // -10%
    target: 1115, // +25%
    status: "エントリー済",
    entryDate: "2025-10-15",
    currentReturn: 1.5
  },
  {
    code: "3932",
    name: "アカツキ",
    previousStatus: "前年度赤字",
    currentQuarter: "Q3黒字転換",
    ma5: 2156,
    currentPrice: 2189,
    recommendedEntry: 2156,
    stopLoss: 1940,
    target: 2695,
    status: "監視中",
    entryDate: null,
    currentReturn: 0
  },
  {
    code: "7037",
    name: "テノ.ホールディングス",
    previousStatus: "前年度赤字",
    currentQuarter: "Q1黒字転換",
    ma5: 456,
    currentPrice: 478,
    recommendedEntry: 456,
    stopLoss: 410,
    target: 570,
    status: "利益確定済",
    entryDate: "2025-09-20",
    currentReturn: 26.3
  },
  {
    code: "9467",
    name: "アルファポリス",
    previousStatus: "前年度赤字",
    currentQuarter: "Q2黒字転換",
    ma5: 1234,
    currentPrice: 1289,
    recommendedEntry: 1234,
    stopLoss: 1111,
    target: 1543,
    status: "エントリー済",
    entryDate: "2025-10-25",
    currentReturn: 4.5
  }
];

// 手動決済シグナル
const manualSignals = [
  {
    code: "7342",
    name: "ウェルスナビ",
    logic: "A",
    signalType: "損切りシグナル",
    reason: "3営業日連続下落",
    urgency: "high",
    entryPrice: 1029,
    currentPrice: 945,
    loss: -8.2,
    action: "翌営業日寄り値で決済推奨"
  },
  {
    code: "3681",
    name: "ブイキューブ",
    logic: "B",
    signalType: "中途撤退期限",
    reason: "決算日から1ヶ月半経過まで残り3日",
    urgency: "medium",
    entryPrice: 892,
    currentPrice: 905,
    profit: 1.5,
    action: "利益10%未達のため撤退検討"
  }
];

// 元のモックデータ（互換性のため残す）
const mockStocks = [
  {
    code: "7203",
    name: "トヨタ自動車",
    price: 2845,
    change: 125,
    changeRate: 4.6,
    volume: 15234500,
    signal: "強い買い",
    score: 92,
    entry: 2850,
    stopLoss: 2750,
    target: 3050,
    sector: "自動車"
  },
  {
    code: "9984",
    name: "ソフトバンクグループ",
    price: 5821,
    change: -89,
    changeRate: -1.5,
    volume: 8921300,
    signal: "中立",
    score: 55,
    entry: 5800,
    stopLoss: 5600,
    target: 6000,
    sector: "通信"
  },
  {
    code: "6758",
    name: "ソニーグループ",
    price: 13450,
    change: 280,
    changeRate: 2.1,
    volume: 3456700,
    signal: "買い",
    score: 78,
    entry: 13500,
    stopLoss: 13000,
    target: 14000,
    sector: "電気機器"
  },
  {
    code: "8306",
    name: "三菱UFJフィナンシャル",
    price: 1289,
    change: 45,
    changeRate: 3.6,
    volume: 45123000,
    signal: "強い買い",
    score: 88,
    entry: 1290,
    stopLoss: 1240,
    target: 1350,
    sector: "銀行"
  },
  {
    code: "4755",
    name: "楽天グループ",
    price: 678,
    change: 32,
    changeRate: 5.0,
    volume: 12890000,
    signal: "買い",
    score: 75,
    entry: 680,
    stopLoss: 650,
    target: 720,
    sector: "サービス"
  },
  {
    code: "9433",
    name: "KDDI",
    price: 4123,
    change: -23,
    changeRate: -0.6,
    volume: 2345600,
    signal: "中立",
    score: 60,
    entry: 4100,
    stopLoss: 4000,
    target: 4200,
    sector: "通信"
  },
  {
    code: "6861",
    name: "キーエンス",
    price: 56780,
    change: 890,
    changeRate: 1.6,
    volume: 234500,
    signal: "買い",
    score: 82,
    entry: 57000,
    stopLoss: 55000,
    target: 59000,
    sector: "電気機器"
  },
  {
    code: "7974",
    name: "任天堂",
    price: 7234,
    change: 156,
    changeRate: 2.2,
    volume: 1890000,
    signal: "買い",
    score: 79,
    entry: 7250,
    stopLoss: 7000,
    target: 7500,
    sector: "その他製品"
  },
  {
    code: "3382",
    name: "セブン&アイHD",
    price: 2156,
    change: -34,
    changeRate: -1.6,
    volume: 3456000,
    signal: "売り",
    score: 35,
    entry: 2150,
    stopLoss: 2200,
    target: 2050,
    sector: "小売"
  },
  {
    code: "7267",
    name: "本田技研工業",
    price: 1567,
    change: 78,
    changeRate: 5.2,
    volume: 8901000,
    signal: "強い買い",
    score: 91,
    entry: 1570,
    stopLoss: 1500,
    target: 1650,
    sector: "自動車"
  }
];

// スキャン統計データ
const scanStats = {
  totalScanned: 3842,
  strongBuy: 156,
  buy: 342,
  neutral: 2890,
  sell: 298,
  strongSell: 156,
  lastUpdate: new Date().toLocaleTimeString('ja-JP')
};

// セクター別パフォーマンス
const sectorPerformance = [
  { sector: "自動車", performance: 4.2, count: 89 },
  { sector: "電気機器", performance: 2.8, count: 156 },
  { sector: "銀行", performance: 3.1, count: 45 },
  { sector: "通信", performance: -0.5, count: 23 },
  { sector: "サービス", performance: 1.9, count: 234 },
  { sector: "小売", performance: -1.2, count: 178 }
];

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    logicAStocks,
    logicBStocks,
    manualSignals,
    mockStocks,
    scanStats,
    sectorPerformance
  };
}