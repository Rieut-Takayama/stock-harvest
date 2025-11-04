// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    updateLastUpdateTime();
    renderStockTable();
});

// 最終更新時刻を更新
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ja-JP');
    document.getElementById('lastUpdate').textContent = timeString;
}

// 株式テーブルをレンダリング
function renderStockTable() {
    const tbody = document.getElementById('stockTableBody');
    tbody.innerHTML = '';
    
    mockStocks.forEach(stock => {
        const row = createStockRow(stock);
        tbody.appendChild(row);
    });
}

// 株式の行を作成
function createStockRow(stock) {
    const tr = document.createElement('tr');
    
    // 価格変動のクラスを決定
    const priceClass = stock.changeRate > 0 ? 'price-up' : 'price-down';
    const changeSymbol = stock.changeRate > 0 ? '+' : '';
    
    // シグナルのクラスを決定
    let signalClass = 'neutral';
    if (stock.signal === '強い買い') signalClass = 'strong-buy';
    else if (stock.signal === '買い') signalClass = 'buy';
    else if (stock.signal === '売り') signalClass = 'sell';
    
    tr.innerHTML = `
        <td class="stock-code">${stock.code}</td>
        <td class="stock-name">${stock.name}</td>
        <td>¥${stock.price.toLocaleString()}</td>
        <td class="${priceClass}">
            ${changeSymbol}${stock.change} 
            (${changeSymbol}${stock.changeRate}%)
        </td>
        <td>${stock.volume.toLocaleString()}</td>
        <td>
            <div class="ai-score">
                <div class="score-bar">
                    <div class="score-fill" style="width: ${stock.score}%"></div>
                </div>
                <span>${stock.score}</span>
            </div>
        </td>
        <td>
            <span class="signal-badge ${signalClass}">${stock.signal}</span>
        </td>
        <td>
            <div class="price-info">
                <div class="entry">IN: ¥${stock.entry.toLocaleString()}</div>
                <div class="stop-loss">SL: ¥${stock.stopLoss.toLocaleString()}</div>
                <div class="target">TP: ¥${stock.target.toLocaleString()}</div>
            </div>
        </td>
        <td>
            <button class="action-btn" onclick="viewDetail('${stock.code}')">
                詳細
            </button>
        </td>
    `;
    
    return tr;
}

// スキャン開始
function startScan() {
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    
    // ローディング表示
    button.innerHTML = '<span class="loading"></span> スキャン中...';
    button.disabled = true;
    
    // 3秒後にスキャン完了をシミュレート
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.disabled = false;
        
        // データを更新
        updateLastUpdateTime();
        
        // アニメーション付きで統計を更新
        animateStats();
        
        // テーブルを再描画
        renderStockTable();
        
        // 完了通知
        showNotification('スキャン完了！新しい注目銘柄が見つかりました。');
    }, 3000);
}

// 統計のアニメーション
function animateStats() {
    const stats = document.querySelectorAll('.stat-value');
    stats.forEach(stat => {
        stat.style.transform = 'scale(1.2)';
        stat.style.transition = 'transform 0.3s ease';
        setTimeout(() => {
            stat.style.transform = 'scale(1)';
        }, 300);
    });
}

// フィルター機能
function filterStocks(filter) {
    // ボタンのアクティブ状態を更新
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // フィルタリング
    let filteredStocks = mockStocks;
    
    if (filter === 'buy') {
        filteredStocks = mockStocks.filter(s => 
            s.signal === '強い買い' || s.signal === '買い'
        );
    } else if (filter === 'sell') {
        filteredStocks = mockStocks.filter(s => 
            s.signal === '売り' || s.signal === '強い売り'
        );
    }
    
    // テーブルを再描画
    const tbody = document.getElementById('stockTableBody');
    tbody.innerHTML = '';
    
    filteredStocks.forEach(stock => {
        const row = createStockRow(stock);
        tbody.appendChild(row);
    });
}

// 詳細画面へ遷移
function viewDetail(code) {
    // モックアップなので、アラートで表示
    const stock = mockStocks.find(s => s.code === code);
    showNotification(`${stock.name}（${code}）の詳細画面へ遷移します`);
    
    // 実際の実装では以下のようにページ遷移
    // window.location.href = `mockups/stock-detail.html?code=${code}`;
}

// 通知表示
function showNotification(message) {
    // 通知要素を作成
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary-main);
        color: white;
        padding: var(--spacing-md) var(--spacing-lg);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒後に削除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// アニメーション定義を追加
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);