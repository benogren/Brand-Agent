# AI Brand Studio - Setup Guide

This guide walks you through setting up the AI Brand Studio project, including Google Cloud infrastructure and local development environment.

## Prerequisites

- Python 3.9 or higher
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (gcloud CLI)
- Git
- A Google Cloud account with billing enabled

## Step 1: Google Cloud Project Setup

### Option A: Automated Setup (Recommended)

Run the automated setup script:

```bash
./scripts/setup_gcp.sh
```

This script will:
1. Create or configure your Google Cloud project
2. Enable all required APIs (Vertex AI, Cloud SQL, Vector Search, Secret Manager, Logging)
3. Set up Application Default Credentials
4. Configure default region (us-central1)

### Option B: Manual Setup

1. **Create a Google Cloud Project:**
   ```bash
   export PROJECT_ID="your-project-id"
   gcloud projects create $PROJECT_ID
   gcloud config set project $PROJECT_ID
   ```

2. **Enable Billing:**
   - Visit https://console.cloud.google.com/billing
   - Link billing account to your project

3. **Enable Required APIs:**
   ```bash
   gcloud services enable \
     aiplatform.googleapis.com \
     storage.googleapis.com \
     sql-component.googleapis.com \
     sqladmin.googleapis.com \
     logging.googleapis.com \
     monitoring.googleapis.com \
     cloudtrace.googleapis.com \
     secretmanager.googleapis.com
   ```

4. **Set Default Region:**
   ```bash
   gcloud config set compute/region us-central1
   ```

5. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

## Step 2: Local Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Brand-Agent
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install with dev dependencies
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required variables:
   - `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
   - `GOOGLE_CLOUD_LOCATION`: Region (default: us-central1)
   - `DATABASE_URL`: PostgreSQL connection string (set after Step 3)

## Step 3: Database Setup

### Cloud SQL PostgreSQL Instance

Run the automated setup script:

```bash
./scripts/setup_cloud_sql.sh
```

This script will:
1. Create a Cloud SQL PostgreSQL instance (f1-micro tier for free tier)
2. Create the `brandstudio` database
3. Create a database user with password
4. Provide connection details for .env configuration

### Manual Database Setup

If you prefer manual setup:

1. **Create Cloud SQL instance:**
   ```bash
   gcloud sql instances create brandstudio-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1 \
     --no-assign-ip
   ```

2. **Create database:**
   ```bash
   gcloud sql databases create brandstudio \
     --instance=brandstudio-db
   ```

3. **Create user:**
   ```bash
   gcloud sql users create brandstudio-user \
     --instance=brandstudio-db \
     --password=YOUR_SECURE_PASSWORD
   ```

### Local Development with Cloud SQL Proxy

To connect to Cloud SQL from your local machine:

1. **Download Cloud SQL Proxy:**
   ```bash
   curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
   chmod +x cloud-sql-proxy
   ```

2. **Run the proxy:**
   ```bash
   ./cloud-sql-proxy PROJECT_ID:REGION:INSTANCE_NAME
   ```

3. **Update .env with local connection:**
   ```
   DATABASE_URL=postgresql://brandstudio-user:PASSWORD@localhost:5432/brandstudio
   ```

## Step 4: Secret Manager Configuration

Configure API keys securely in Google Cloud Secret Manager:

```bash
./scripts/setup_secrets.sh
```

This script will prompt you for:
- **Namecheap API Key** (optional) - for domain availability checking
- **USPTO API Key** (optional) - for trademark search
- **Twitter/X API credentials** (optional) - for social media handle checking
- **Instagram API Key** (optional) - for handle checking
- **LinkedIn API Key** (optional) - for handle checking
- **Database Password** (recommended) - for Cloud SQL access

All secrets are stored securely in Google Cloud Secret Manager and never committed to git.

### Accessing Secrets in Code

Secrets will be accessed via `src/infrastructure/secrets.py` (created in later tasks):

```python
from src.infrastructure.secrets import get_secret

# Example usage
namecheap_key = get_secret('namecheap-api-key')
```

## Step 5: Vector Search Setup

See Phase 2 tasks for Vector Search index creation.

## Step 5: Verify Installation

Run tests to verify setup:

```bash
pytest tests/
```

## Troubleshooting

### "gcloud: command not found"
Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### "API not enabled" errors
Run: `gcloud services list --enabled` to check enabled APIs
Enable missing APIs: `gcloud services enable <api-name>`

### Authentication issues
Re-authenticate:
```bash
gcloud auth login
gcloud auth application-default login
```

## Next Steps

After completing setup:
1. Proceed to implement agents (Task 2.0)
2. Create custom tools (Tasks 3.0, 9.0, 10.0)
3. Set up RAG with Vector Search (Tasks 6.0-8.0)

## Cost Management

To stay within free tier:
- Use f1-micro for Cloud SQL
- Set min_instances=0 for Agent Engine
- Monitor usage in [Cloud Console](https://console.cloud.google.com)
- Set up billing alerts at $10, $20, $50

## Support

For issues or questions:
- Check [CLAUDE.md](../CLAUDE.md) for development notes
- Review [PRD](../tasks/prd-ai-brand-studio.md) for requirements
- Consult [Google Cloud documentation](https://cloud.google.com/docs)
