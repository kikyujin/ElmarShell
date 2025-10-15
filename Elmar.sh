#!/bin/bash
# Elmar - ラッパースクリプト
# 使い方: Elmar 'foo.txt を 2025-*-*.md に対応する *.txt としてコピーして'

# コマンド引数がなければ使い方を表示して終了
if [ $# -eq 0 ]; then
    echo "使い方: $0 '操作内容を日本語で記述してください'"
    echo "例: $0 'foo.txt を 2025-*-*.md に対応する *.txt としてコピーして'"
    echo "Geminiを強制する場合: $0 --gemini 'foo.txt をコピーして'"
    exit 1
fi

# スクリプトのディレクトリを取得
SCRIPT_DIR="$HOME/work/ElmarShell"

# venvを有効化
source "$SCRIPT_DIR/venv/bin/activate"

# 環境変数でgRPCの警告を抑制
export GRPC_VERBOSITY=ERROR
export GLOG_minloglevel=2

# OLLAMA_BASE_URLが未定義なら定義
if [ -z "${OLLAMA_BASE_URL}" ]; then
    export OLLAMA_BASE_URL='http://galg60x.local:11434'
fi

# --gemini オプション判定
if [ "$1" = "--gemini" ]; then
#    echo "Using Gemini model (forced by --gemini option)"
    SCRIPT="Elmar.py"
    shift
else
    curl -s --max-time 2 "$OLLAMA_BASE_URL" > /dev/null
    if [ $? -eq 0 ]; then
        # OLLAMA版
#        echo "Using OLLAMA model"
        SCRIPT="Elmar_ol.py"
    else
        # Gemmin版
#        echo "Using Gemini model"
        SCRIPT="Elmar.py"
    fi
fi

# SCRIPTがElmar.pyでGEMINI_API_KEYが未定義ならエラー
if [ "$SCRIPT" = "Elmar.py" ] && [ -z "${GEMINI_API_KEY}" ]; then
    echo "エラー: GEMINI_API_KEYが定義されていません。環境変数を設定してください。" >&2
    exit 1
fi

# stderrだけフィルタリング、stdinは/dev/ttyから直接読む
python3 "$SCRIPT_DIR/$SCRIPT" "$@" < /dev/tty 2> >(grep -v "ALTS creds ignored" | grep -v "absl::InitializeLog" >&2)
