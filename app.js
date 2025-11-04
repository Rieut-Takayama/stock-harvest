// サンプル株式データ（実際のプロジェクトでは外部APIを使用）
const sampleStocks = [
    // 3ヶ月予測
    {
        period: 3,
        stocks: [
            { symbol: '7203', name: 'トヨタ自動車', score: 92, growth: '+15%' },
            { symbol: '6758', name: 'ソニーグループ', score: 88, growth: '+12%' },
            { symbol: '9984', name: 'ソフトバンクグループ', score: 85, growth: '+18%' },
            { symbol: '6861', name: 'キーエンス', score: 83, growth: '+10%' },
            { symbol: '4063', name: '信越化学工業', score: 81, growth: '+8%' }
        ]
    },
    // 6ヶ月予測
    {
        period: 6,
        stocks: [
            { symbol: '9432', name: '日本電信電話', score: 90, growth: '+22%' },
            { symbol: '6954', name: 'ファナック', score: 87, growth: '+20%' },
            { symbol: '8035', name: '東京エレクトロン', score: 86, growth: '+25%' },
            { symbol: '9433', name: 'KDDI', score: 84, growth: '+15%' },
            { symbol: '7741', name: 'HOYA', score: 82, growth: '+18%' }
        ]
    },
    // 9ヶ月予測
    {
        period: 9,
        stocks: [
            { symbol: '6098', name: 'リクルートHD', score: 91, growth: '+30%' },
            { symbol: '4661', name: 'オリエンタルランド', score: 89, growth: '+28%' },
            { symbol: '9983', name: 'ファーストリテイリング', score: 87, growth: '+25%' },
            { symbol: '8001', name: '伊藤忠商事', score: 85, growth: '+22%' },
            { symbol: '6367', name: 'ダイキン工業', score: 83, growth: '+20%' }
        ]
    },
    // 12ヶ月予測
    {
        period: 12,
        stocks: [
            { symbol: '7974', name: '任天堂', score: 94, growth: '+40%' },
            { symbol: '6501', name: '日立製作所', score: 92, growth: '+35%' },
            { symbol: '8306', name: '三菱UFJフィナンシャル', score: 90, growth: '+32%' },
            { symbol: '4519', name: '中外製薬', score: 88, growth: '+38%' },
            { symbol: '6902', name: 'デンソー', score: 86, growth: '+30%' }
        ]
    }
];

// 株価分析を実行
function analyzeStocks() {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // ローディング表示
    loading.classList.add('active');
    results.innerHTML = '';
    
    // 分析をシミュレート（2秒後に結果表示）
    setTimeout(() => {
        loading.classList.remove('active');
        displayResults();
    }, 2000);
}

// 結果を表示
function displayResults() {
    const results = document.getElementById('results');
    
    sampleStocks.forEach(periodData => {
        const periodCard = createPeriodCard(periodData);
        results.appendChild(periodCard);
    });
}

// 期間ごとのカードを作成
function createPeriodCard(data) {
    const card = document.createElement('div');
    card.className = 'period-card';
    
    // ヘッダー
    const header = document.createElement('div');
    header.className = 'period-header';
    header.innerHTML = `<h2>${data.period}ヶ月後予測</h2>`;
    card.appendChild(header);
    
    // 株式リスト
    data.stocks.forEach(stock => {
        const stockItem = createStockItem(stock);
        card.appendChild(stockItem);
    });
    
    return card;
}

// 個別の株式アイテムを作成
function createStockItem(stock) {
    const item = document.createElement('div');
    item.className = 'stock-item';
    
    // 高スコアの株式を強調
    const isHighConfidence = stock.score >= 90;
    
    item.innerHTML = `
        <div class="stock-symbol">${stock.symbol}</div>
        <div class="stock-name">${stock.name}</div>
        <div class="prediction-score">
            <span class="score">AIスコア: ${stock.score}/100</span>
            <span class="growth-indicator ${isHighConfidence ? 'high-confidence' : ''}">
                予想上昇率 ${stock.growth}
            </span>
        </div>
    `;
    
    return item;
}

// ページ読み込み時のアニメーション
document.addEventListener('DOMContentLoaded', () => {
    // ヘッダーのフェードイン効果
    const header = document.querySelector('header');
    header.style.opacity = '0';
    header.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        header.style.transition = 'all 0.6s ease';
        header.style.opacity = '1';
        header.style.transform = 'translateY(0)';
    }, 100);
});