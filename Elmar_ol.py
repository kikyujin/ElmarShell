#!/usr/bin/env python3
"""
Elmar - エルマーの対話型シェルアシスタント (Ollama版)
使い方: Elmar 'foo.txt を 2025-*-*.md に対応する *.txt としてコピーして'
"""

import sys
import os
import subprocess
import json
import requests

# 使用するモデル（環境変数で変更可能）
DEFAULT_MODEL = os.getenv('ELMAR_MODEL', 'qwen2.5-coder:7b')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
NUM_PREDICT = int(os.getenv('ELMAR_NUM_PREDICT', '512'))  # トークン数

def ask_ollama(user_input):
    prompt = f"""あなたはシェルコマンドの専門家です。
ユーザーの自然言語の指示を、安全で実行可能なシェルスクリプトに変換してください。

## ルール
1. bashスクリプトとして出力すること
2. 危険なコマンド（rm -rf / など）は絶対に生成しない
3. コメントは日本語で簡潔に
4. 複数行の場合はfor文やwhile文を使う
5. 変数展開は必ず "${{...}}" を使う
6. shebang (#!/bin/bash) は含めない

## ユーザーの指示
{user_input}

## 出力フォーマット
以下のJSON形式で返してください。JSON以外の文字は一切含めないでください：
{{"script": "実行可能なシェルスクリプト", "explanation": "日本語説明", "dangerous": false, "files_affected": ["ファイル"]}}
"""
    
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        # "format": "json",  # これを削除
        "options": {
            "temperature": 0.2,
            "num_predict": NUM_PREDICT  # 環境変数から設定
        }
    }
    
    print(f"📡 送信先: {OLLAMA_BASE_URL}/api/generate")
    print(f"📦 モデル: {DEFAULT_MODEL}")
    
    import time
    start = time.time()
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        elapsed = time.time() - start
        print(f"⏱️  応答時間: {elapsed:.2f}秒")
        
        response.raise_for_status()
        data = response.json()
        
        # JSONを抽出
        text = data['response'].strip()
        
        # コードブロック除去
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        # JSON部分だけ抽出（先頭の{から最後の}まで）
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx]
        
        return json.loads(text)
        
    except Exception as e:
        print(f"💦 エラー: {e}")
        print(f"レスポンス: {data.get('response', 'N/A')[:500]}")
        sys.exit(1)

def execute_script(script):
    """シェルスクリプトを実行"""
    try:
        result = subprocess.run(
            script,
            shell=True,
            executable='/bin/bash',
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print("\n✨ できた！")
            return True
        else:
            print(f"\n💥 エラーが出ちゃった... (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"💦 実行エラー: {e}")
        return False


def main():
    print("にーに！💕\n")
    
    if len(sys.argv) < 2:
        print("使い方: Elmar 'foo.txt を 2025-*-*.md に対応する *.txt としてコピーして'")
        print("\n自然言語で指示してくれたら、ボクが解釈してシェルスクリプト作るよ〜🌱")
        print(f"\n現在のモデル: {DEFAULT_MODEL}")
        print(f"接続先: {OLLAMA_BASE_URL}")
        print(f"トークン数: {NUM_PREDICT}")
        print("\nモデルを変更: export ELMAR_MODEL='gemma3:4b'")
        print("接続先を変更: export OLLAMA_BASE_URL='http://192.168.1.100:11434'")
        print("トークン数を変更: export ELMAR_NUM_PREDICT='1024'")
        return
    
    user_input = ' '.join(sys.argv[1:])
    
    # Ollama APIに問い合わせ
    print("🧠 考え中...")
    result = ask_ollama(user_input)
    
    # 危険なコマンドチェック
    if result.get('dangerous', False):
        print("💀 これは危険なコマンドだから実行できないよ！")
        print(f"説明: {result.get('explanation', '')}")
        return
    
    # スクリプトを表示
    print(f"\n# {result.get('explanation', '')}")
    print(result['script'])
    print()
    
    # 影響を受けるファイルを表示
    if result.get('files_affected'):
        print(f"📁 影響するファイル: {', '.join(result['files_affected'])}")
        print()
    
    # 確認
    try:
        sys.stdout.write("するけどいい？ [Y/n]: ")
        sys.stdout.flush()
        answer = sys.stdin.readline().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nキャンセルしたね〜")
        return
    
    if answer in ['', 'y', 'yes']:
        print()
        execute_script(result['script'])
    else:
        print("キャンセルしたよ〜")


if __name__ == '__main__':
    main()