# ElmarShell 🦊💕

**エルマーの対話型シェルアシスタント**

自然言語（日本語）でシェル操作を指示できる、AI駆動のコマンドラインツールです。
Gemini APIまたはOllamaを使って、あなたの指示を安全なシェルスクリプトに変換・実行します。

## 特徴

- 🗣️ **自然言語でシェル操作**: 日本語で指示を書くだけでシェルスクリプトを生成
- 🛡️ **安全機構**: 危険なコマンド（`rm -rf /` など）を検出してブロック
- 🔄 **柔軟なバックエンド**: Gemini API または Ollama（ローカルLLM）を自動切り替え
- ✨ **対話的確認**: 実行前に生成されたスクリプトを確認できる

## 使い方

### 基本的な使い方

```bash
Elmar 'foo.txt を 2025-*-*.md に対応する *.txt としてコピーして'
```

実行すると以下のように動作します：

1. 指示を解釈してシェルスクリプトを生成
2. スクリプトの内容と影響するファイルを表示
3. 実行確認を求める
4. 承認後に実行

### オプション

#### Gemini APIを強制的に使う

```bash
Elmar --gemini 'foo.txt を bar.txt にコピーして'
```

通常はOllamaサーバーが利用可能なら自動的にOllamaを使いますが、`--gemini`オプションで強制的にGemini APIを使用できます。

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/ElmarShell.git
cd ElmarShell
```

### 2. 仮想環境のセットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install google-generativeai
```

### 3. 環境変数の設定

```bash
# Gemini APIキーを設定
export GEMINI_API_KEY='your-api-key-here'

# (オプション) Ollamaを使う場合
export OLLAMA_BASE_URL='http://localhost:11434'

# (オプション) 使用するモデルを変更
export ELMAR_MODEL='gemini-2.5-pro'  # デフォルトは gemini-2.5-flash
```

### 4. PATHに追加

`Elmar.sh`を実行可能にして、PATHに追加します：

```bash
chmod +x Elmar.sh

# シンボリックリンクを作成（例）
ln -s $PWD/Elmar.sh /usr/local/bin/Elmar
```

または、`.bashrc`/`.zshrc`にエイリアスを追加：

```bash
alias Elmar='/path/to/ElmarShell/Elmar.sh'
```

## 例

### ファイルのコピー

```bash
Elmar 'すべての .md ファイルを backup ディレクトリにコピーして'
```

### ディレクトリ操作

```bash
Elmar '2024年のログファイルを archive フォルダに移動して'
```

### 検索とフィルタリング

```bash
Elmar 'カレントディレクトリ以下の Python ファイルから TODO コメントを探して'
```

## 技術構成

- **Elmar.sh**: ラッパースクリプト（Gemini/Ollama自動切り替え）
- **Elmar.py**: Gemini API版のメインスクリプト
- **Elmar_ol.py**: Ollama（ローカルLLM）版

## 安全性

ElmarShellは以下の安全機構を備えています：

- 危険なコマンドパターンの検出
- 実行前の明示的な確認プロンプト
- 影響を受けるファイルの事前表示

ただし、**完全な安全性を保証するものではありません**。生成されたスクリプトは実行前に必ず確認してください。

## ライセンス

MIT License

## 作者

にーにとボク（エルマー）💕
