// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    updateLastUpdateTime();
    renderLogicResults();
    renderManualSignals();
});

// 最終更新時刻を更新
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ja-JP');
    document.getElementById('lastUpdate').textContent = timeString;
}

// ロジックA・Bの結果をレンダリング
function renderLogicResults() {
    // ロジックA
    const logicAContainer = document.getElementById('logicA-results');
    logicAContainer.innerHTML = '';
    
    logicAStocks.forEach(stock => {
        const card = createLogicACard(stock);
        logicAContainer.appendChild(card);
    });
    
    // ロジックB
    const logicBContainer = document.getElementById('logicB-results');
    logicBContainer.innerHTML = '';
    
    logicBStocks.forEach(stock => {
        const card = createLogicBCard(stock);
        logicBContainer.appendChild(card);
    });
}

// ロジックAカードを作成
function createLogicACard(stock) {
    const div = document.createElement('div');
    div.className = 'stock-card logic-a';
    
    const statusClass = stock.currentReturn < 0 ? 'negative' : 'positive';
    const returnSymbol = stock.currentReturn >= 0 ? '+' : '';
    
    div.innerHTML = `
        <div class="stock-card-header">
            <div class="stock-info">
                <span class="stock-code">${stock.code}</span>
                <span class="stock-name">${stock.name}</span>
            </div>
            <span class="badge badge-primary">${stock.status}</span>
        </div>
        <div class="stock-card-body">
            <div class="trigger-info">
                <small>トリガー: ${stock.triggerEvent} (${stock.triggerDate})</small>
            </div>
            <div class="price-grid">
                <div class="price-item">
                    <span class="label">ストップ高</span>
                    <span class="value">¥${stock.limitPrice.toLocaleString()}</span>
                </div>
                <div class="price-item">
                    <span class="label">推奨買値</span>
                    <span class="value accent">¥${stock.recommendedEntry.toLocaleString()}</span>
                    <small class="hint">前日終値+5%</small>
                </div>
                <div class="price-item">
                    <span class="label">現在値</span>
                    <span class="value">¥${stock.currentPrice.toLocaleString()}</span>
                </div>
                <div class="price-item">
                    <span class="label">目標価格</span>
                    <span class="value positive">¥${stock.target.toLocaleString()}</span>
                    <small class="hint">+25%</small>
                </div>
            </div>
            <div class="status-bar">
                <div class="status-item">
                    <span class="label">保有日数</span>
                    <span class="value">${stock.daysHeld}日</span>
                </div>
                <div class="status-item">
                    <span class="label">現在リターン</span>
                    <span class="value ${statusClass}">${returnSymbol}${stock.currentReturn}%</span>
                </div>
            </div>
            ${stock.currentReturn < -5 ? '<div class="warning-message"><span class="material-icons">warning</span> 3営業日連続下落を監視中</div>' : ''}
        </div>
        <div class="stock-card-footer">
            <button class="btn btn-sm btn-secondary" onclick="viewChart('${stock.code}')">
                <span class="material-icons">show_chart</span>
                チャート
            </button>
            <button class="btn btn-sm btn-primary" onclick="viewDetail('${stock.code}')">
                詳細を見る
            </button>
        </div>
    `;
    
    return div;
}

// ロジックBカードを作成
function createLogicBCard(stock) {
    const div = document.createElement('div');
    div.className = 'stock-card logic-b';
    
    const statusClass = stock.currentReturn > 0 ? 'positive' : stock.currentReturn < 0 ? 'negative' : 'neutral';
    const returnSymbol = stock.currentReturn > 0 ? '+' : '';
    
    div.innerHTML = `
        <div class="stock-card-header">
            <div class="stock-info">
                <span class="stock-code">${stock.code}</span>
                <span class="stock-name">${stock.name}</span>
            </div>
            <span class="badge badge-success">${stock.status}</span>
        </div>
        <div class="stock-card-body">
            <div class="trigger-info">
                <small>${stock.previousStatus} → ${stock.currentQuarter}</small>
            </div>
            <div class="price-grid">
                <div class="price-item">
                    <span class="label">5日移動平均</span>
                    <span class="value">¥${stock.ma5.toLocaleString()}</span>
                </div>
                <div class="price-item">
                    <span class="label">推奨買値</span>
                    <span class="value accent">¥${stock.recommendedEntry.toLocaleString()}</span>
                    <small class="hint">5日線付近</small>
                </div>
                <div class="price-item">
                    <span class="label">損切り</span>
                    <span class="value negative">¥${stock.stopLoss.toLocaleString()}</span>
                    <small class="hint">-10%</small>
                </div>
                <div class="price-item">
                    <span class="label">利確目標</span>
                    <span class="value positive">¥${stock.target.toLocaleString()}</span>
                    <small class="hint">+25%</small>
                </div>
            </div>
            <div class="status-bar">
                <div class="status-item">
                    <span class="label">現在値</span>
                    <span class="value">¥${stock.currentPrice.toLocaleString()}</span>
                </div>
                <div class="status-item">
                    <span class="label">現在リターン</span>
                    <span class="value ${statusClass}">${returnSymbol}${stock.currentReturn}%</span>
                </div>
            </div>
            ${stock.status === '利益確定済' ? '<div class="success-message"><span class="material-icons">check_circle</span> 目標達成！利益確定済み</div>' : ''}
        </div>
        <div class="stock-card-footer">
            <button class="btn btn-sm btn-secondary" onclick="viewChart('${stock.code}')">
                <span class="material-icons">show_chart</span>
                チャート
            </button>
            <button class="btn btn-sm btn-primary" onclick="viewDetail('${stock.code}')">
                詳細を見る
            </button>
        </div>
    `;
    
    return div;
}

// 手動決済シグナルをレンダリング
function renderManualSignals() {
    const container = document.querySelector('.signals-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    manualSignals.forEach(signal => {
        const item = createSignalItem(signal);
        container.appendChild(item);
    });
}

// シグナルアイテムを作成
function createSignalItem(signal) {
    const div = document.createElement('div');
    div.className = `signal-item ${signal.urgency === 'high' ? 'urgent' : ''}`;
    
    const returnValue = signal.loss || signal.profit || 0;
    const returnClass = returnValue < 0 ? 'loss' : 'profit';
    const returnSymbol = returnValue >= 0 ? '+' : '';
    
    div.innerHTML = `
        <div class="signal-icon">
            <span class="material-icons">${signal.urgency === 'high' ? 'warning' : 'schedule'}</span>
        </div>
        <div class="signal-content">
            <div class="signal-stock">
                <span class="stock-code">${signal.code}</span>
                <span class="stock-name">${signal.name}</span>
                <span class="badge badge-${signal.logic === 'A' ? 'danger' : 'success'}">ロジック${signal.logic}</span>
            </div>
            <div class="signal-message">
                <strong>${signal.signalType}</strong>
                <p>${signal.reason}。${signal.action}</p>
            </div>
            <div class="signal-prices">
                <span class="price-item">買付: ¥${signal.entryPrice.toLocaleString()}</span>
                <span class="price-item">現在: ¥${signal.currentPrice.toLocaleString()}</span>
                <span class="price-item ${returnClass}">${signal.loss ? '損失' : '利益'}: ${returnSymbol}${Math.abs(returnValue)}%</span>
            </div>
        </div>
        <button class="btn btn-sm btn-${signal.urgency === 'high' ? 'danger' : 'warning'}" 
                onclick="${signal.urgency === 'high' ? 'executeSignal' : 'reviewSignal'}('${signal.code}')">
            ${signal.urgency === 'high' ? '決済実行' : '詳細確認'}
        </button>
    `;
    
    return div;
}

// ロジックAスキャン
function scanLogicA() {
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    
    button.innerHTML = '<span class="loading"></span> スキャン中...';
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.disabled = false;
        updateLastUpdateTime();
        showNotification('ロジックAスキャン完了！3銘柄が条件に合致しました。');
        renderLogicResults();
    }, 2000);
}

// ロジックBスキャン
function scanLogicB() {
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    
    button.innerHTML = '<span class="loading"></span> スキャン中...';
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.disabled = false;
        updateLastUpdateTime();
        showNotification('ロジックBスキャン完了！4銘柄が条件に合致しました。');
        renderLogicResults();
    }, 2000);
}

// シグナル実行
function executeSignal(code) {
    if (confirm(`${code}の決済を実行しますか？`)) {
        showNotification(`${code}の決済注文を送信しました。`);
        // 実際の実装では決済APIを呼ぶ
    }
}

// シグナル確認
function reviewSignal(code) {
    const signal = manualSignals.find(s => s.code === code);
    showNotification(`${signal.name}（${code}）の詳細を確認します。`);
}

// チャート表示
function viewChart(code) {
    showNotification(`${code}のチャートを表示します。`);
}

// 詳細画面へ遷移
function viewDetail(code) {
    window.location.href = `mockups/stock-detail.html?code=${code}`;
}

// 通知表示
function showNotification(message) {
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
    
    .loading {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.6s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);