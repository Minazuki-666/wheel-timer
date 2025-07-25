# 使用するパッケージを指定
$packages = @(
    "ipython",
    "jupyter",
    "matplotlib",
    "matplotlib-inline",
    "numpy",
    "pandas",
    "polars",
    "scikit-learn",
    "seaborn",
    "xlsx2csv"
)

# 仮想環境が存在するかチェック
if (-Not (Test-Path -Path ".venv" -PathType Container)) {
    Write-Host ".venvフォルダが存在しません。仮想環境を作成します..."
    # 仮想環境作成
    uv venv
} else {
    Write-Host ".venvフォルダが既に存在します。仮想環境の作成をスキップします。"
}

# 仮想環境をアクティブ化
.venv\Scripts\activate

# パッケージのインストール
uv pip install $packages

# 参考：https://zenn.dev/kazu0429/articles/ed5011178d4b85#pip-compile-%2B-pip-sync