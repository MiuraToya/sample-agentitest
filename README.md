# sample-agentitest

React + FastAPI の Todo アプリケーション。AWS にデプロイし、Playwright E2E テストと AgentiTest（AI エージェントテスト）を比較するためのサンプルプロジェクト。

## 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | React 19, TypeScript, Vite, React Router |
| バックエンド | FastAPI, Python 3.12, Mangum (Lambda アダプタ) |
| 認証 | Amazon Cognito (メール + パスワード) |
| データベース | Amazon DynamoDB |
| ホスティング | S3 + CloudFront (フロント), Lambda + API Gateway (API) |
| IaC | Terraform |
| CI | GitHub Actions (OIDC 認証) |
| E2E テスト | Playwright for Python, Allure レポート |
| AI テスト | browser_use + Gemini (AgentiTest 比較用) |

## プロジェクト構成

```
├── frontend/                  # React アプリ
│   └── src/
│       ├── auth/              #   Cognito 認証コンテキスト
│       └── pages/             #   Home, About, Login, Todo
├── backend/                   # FastAPI アプリ (Lambda 上で動作)
│   └── main.py
├── terraform/                 # メインインフラ (S3 backend)
│   ├── setup/                 #   ブートストラップ (OIDC, state bucket)
│   └── *.tf
├── tests/
│   ├── e2e/                   # Playwright E2E テスト
│   └── agentitest/            # AI エージェントテスト (比較用)
└── .github/workflows/         # CI ワークフロー
```

## セットアップ

### 前提条件

- Node.js 20+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Terraform 1.0+
- AWS CLI (プロファイル設定済み)

### ローカル開発

```bash
# フロントエンド
cd frontend
npm install
npm run dev

# バックエンド
cd backend
uv sync
uv run uvicorn main:app --reload
```

### AWS デプロイ

#### 1. ブートストラップ (初回のみ)

```bash
cd terraform/setup
terraform init
terraform apply
```

OIDC プロバイダー、state 用 S3 バケット、DynamoDB ロックテーブルが作成されます。

#### 2. メインインフラ

```bash
cd terraform

# backend.tfvars を作成 (backend.tfvars.example を参照)
cp backend.tfvars.example backend.tfvars
# バケット名やプロファイルを記入

terraform init -backend-config=backend.tfvars
terraform apply
```

#### 3. フロントエンドビルド & デプロイ

```bash
cd frontend
VITE_COGNITO_USER_POOL_ID=<pool_id> \
VITE_COGNITO_CLIENT_ID=<client_id> \
npm run build

aws s3 sync dist/ s3://<bucket_name> --delete
aws cloudfront create-invalidation --distribution-id <dist_id> --paths "/*"
```

#### 4. バックエンドデプロイ

```bash
cd backend
pip install --platform manylinux2014_x86_64 --implementation cp \
  --python-version 3.12 --only-binary=:all: --target ./package -r <(uv pip compile pyproject.toml)
cd package && zip -r ../lambda.zip . && cd ..
zip lambda.zip main.py

cd ../terraform
terraform apply
```

## テスト

### E2E テスト (Playwright)

```bash
# 依存インストール
uv sync
uv run playwright install chromium

# テスト実行
AWS_PROFILE=<your-profile> uv run pytest tests/e2e/ -v --alluredir=allure-results
```

テストメソッドは日本語で記述されています:

```
test_トップページにタイトルと説明文が表示される
test_AboutカードからAboutページへ遷移できる
test_未認証でTodoページにアクセスするとログインに飛ぶ
test_正しい認証情報でサインインするとTodoページが表示される
test_サインアウト後にTodoページへアクセスするとログインに戻る
test_Todoを追加するとリストに表示される
test_Todoを追加して削除すると空メッセージが表示される
test_複数Todoから1件削除すると残りが正しく表示される
test_ナビでHomeとAboutを行き来できる
test_未認証時ナビにサインインリンクが表示される
test_認証後ナビにサインアウトボタンが表示される
```

### 環境変数

テスト設定は環境変数で上書き可能です:

| 変数 | デフォルト | 説明 |
|---|---|---|
| `E2E_BASE_URL` | CloudFront URL | テスト対象の URL |
| `E2E_TEST_EMAIL` | `test@example.com` | テストユーザーのメール |
| `E2E_TEST_PASSWORD` | `Test1234` | テストユーザーのパスワード |
| `E2E_DYNAMODB_TABLE` | `sample-agentitest-todos` | DynamoDB テーブル名 |
| `E2E_AWS_REGION` | `ap-northeast-1` | AWS リージョン |

## CI

GitHub Actions で main ブランチへの push / PR 時に E2E テストが自動実行されます。AWS 認証には OIDC を使用し、静的クレデンシャルは不要です。

### 必要な GitHub 設定

**Variables** (Settings > Variables > Actions):
- `AWS_ROLE_ARN` — OIDC 用 IAM ロール ARN
- `E2E_BASE_URL` — CloudFront URL
- `E2E_TEST_EMAIL` — テストユーザーメール
- `E2E_DYNAMODB_TABLE` — DynamoDB テーブル名

**Secrets** (Settings > Secrets > Actions):
- `E2E_TEST_PASSWORD` — テストユーザーパスワード
