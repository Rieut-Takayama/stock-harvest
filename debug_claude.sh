#!/bin/bash

echo "🔍 Claude Code 診断ツール"
echo "================================"

echo ""
echo "📋 1. システム環境確認"
echo "--------------------------------"
echo "OS: $(uname -s)"
echo "Shell: $SHELL"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "npm: $(npm --version 2>/dev/null || echo 'Not installed')"

echo ""
echo "📋 2. Claude Code 状態確認"
echo "--------------------------------"
echo "Claude Code version: $(claude-code --version 2>/dev/null || echo 'Not found or error')"
echo "Claude Code path: $(which claude-code 2>/dev/null || echo 'Not found in PATH')"

echo ""
echo "📋 3. 実行中プロセス確認"
echo "--------------------------------"
CLAUDE_PROCESSES=$(ps aux | grep -i claude | grep -v grep)
if [ -z "$CLAUDE_PROCESSES" ]; then
    echo "No Claude processes running"
else
    echo "$CLAUDE_PROCESSES"
fi

echo ""
echo "📋 4. ポート使用状況確認"
echo "--------------------------------"
echo "Port 3247 (frontend): $(lsof -ti:3247 2>/dev/null && echo 'In use' || echo 'Available')"
echo "Port 8432 (backend): $(lsof -ti:8432 2>/dev/null && echo 'In use' || echo 'Available')"

echo ""
echo "📋 5. ターミナル権限確認"
echo "--------------------------------"
echo "Current terminal: $TERM"
echo "Terminal app: $(ps -o comm= -p $PPID)"

echo ""
echo "🔧 6. 修復コマンド実行"
echo "--------------------------------"

echo "Killing any stuck Claude processes..."
pkill -f claude 2>/dev/null && echo "✅ Processes killed" || echo "ℹ️ No processes to kill"

echo "Clearing npm cache..."
npm cache clean --force 2>/dev/null && echo "✅ npm cache cleared" || echo "⚠️ npm cache clean failed"

echo "Checking for Claude Code updates..."
npm list -g @anthropics/claude-code 2>/dev/null && echo "✅ Claude Code is installed" || echo "⚠️ Claude Code not found globally"

echo ""
echo "🚀 7. 新しいClaude Codeセッション起動テスト"
echo "--------------------------------"
echo "Trying to start claude-code..."

# 新しいターミナルで起動を試みる
osascript <<EOF
tell application "Terminal"
    do script "echo 'Testing claude-code in new terminal...' && claude-code --help && echo 'Claude Code is working!' || echo 'Claude Code failed to start'"
end tell
EOF

echo ""
echo "✅ 診断完了!"
echo "================================"
echo ""
echo "📝 次の手順:"
echo "1. 上記の新しいターミナルウィンドウでClaude Codeが動作するか確認"
echo "2. 動作しない場合: 'npm install -g @anthropics/claude-code' で再インストール"
echo "3. それでもダメな場合: 手動でPhase 3から進めます"
echo ""