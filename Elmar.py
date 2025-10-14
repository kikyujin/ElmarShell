#!/usr/bin/env python3
"""
Elmar - エルマーの対話型シェルアシスタント (Gemini API版)
使い方: Elmar 'foo.txt を 2025-*-*.md に対応する *.txt としてコピーして'
"""

import sys
import os
import subprocess
import json

# 標準エラー出力のフィルタリング（import前に設定）
class FilteredStderr:
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.filter_keywords = ['ALTS creds ignored', 'absl::InitializeLog']
    
    def write(self, text):
        # フィルタリングするキーワード
        if not any(keyword in text for keyword in self.filter_keywords):
            return self.original_stderr.write(text)
        return len(text)
    
    def flush(self):
        return self.original_stderr.flush()
    
    def __getattr__(self, name):
        # その他の属性は元のstderrに委譲
        return getattr(self.original_stderr, name)

# stderrを置き換え（import前に実行）
sys.stderr = FilteredStderr(sys.stderr)

# 環境変数設定
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

import google.generativeai as genai

# 使用するモデル（環境変数で変更可能）
DEFAULT_MODEL = os.getenv('ELMAR_MODEL', 'gemini-2.5-flash')


def init_gemini():
    """Gemini APIの初期化"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("💦 GEMINI_API_KEY が設定されてないよ...")
        print("export GEMINI_API_KEY='your-api-key' してね〜")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    print(f"Using: {DEFAULT_MODEL}")
    return genai.GenerativeModel(DEFAULT_MODEL)


def ask_gemini(model, user_input):
    """
    Gemini APIに自然言語のシェル命令を投げて、
    実行可能なシェルスクリプトとして返してもらう
    """
    
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
JSONで以下の形式で返してください：
{{
  "script": "実行可能なシェルスクリプト（複数行可）",
  "explanation": "何をするスクリプトか、30文字程度の日本語説明",
  "dangerous": false,
  "files_affected": ["影響を受けるファイルパターンの配列"]
}}

危険なコマンドの場合は dangerous を true にしてください。
"""
    
    response = model.generate_content(prompt)
    
    # JSONを抽出（```json ... ``` で囲まれてる場合に対応）
    text = response.text.strip()
    if text.startswith('```json'):
        text = text.split('```json')[1].split('```')[0].strip()
    elif text.startswith('```'):
        text = text.split('```')[1].split('```')[0].strip()
    
    return json.loads(text)


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
            # 実行結果のエラーは表示する
            print(result.stderr, file=sys.stderr.original_stderr)
        
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
        print("モデルを変更: export ELMAR_MODEL='gemini-2.5-pro'")
        return
    
    # Gemini初期化
    try:
        model = init_gemini()
    except Exception as e:
        print(f"💦 Gemini APIの初期化に失敗: {e}")
        return
    
    user_input = ' '.join(sys.argv[1:])
    
    # Gemini APIに問い合わせ
    print("🧠 考え中...")
    try:
        result = ask_gemini(model, user_input)
    except Exception as e:
        print(f"💦 Gemini APIエラー: {e}")
        return
    
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
    
    # 確認（stdin直接読み込み）
    try:
        # sys.stdinを直接使う
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
