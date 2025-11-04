// モックデータ
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