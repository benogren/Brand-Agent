#!/bin/bash
# Cloud SQL PostgreSQL Setup Script for AI Brand Studio
# Creates a PostgreSQL instance in the free tier (f1-micro)

set -e  # Exit on error

echo "=== AI Brand Studio - Cloud SQL Setup ==="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
if [ -z "$PROJECT_ID" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT not set and no default project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Using project: $PROJECT_ID"

# Configuration
INSTANCE_NAME=${CLOUD_SQL_INSTANCE_NAME:-brandstudio-db}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
DATABASE_VERSION="POSTGRES_15"
TIER="db-f1-micro"  # Free tier eligible
DB_NAME="brandstudio"
DB_USER="brandstudio-user"

echo ""
echo "Configuration:"
echo "  Instance Name: $INSTANCE_NAME"
echo "  Region: $REGION"
echo "  Database Version: $DATABASE_VERSION"
echo "  Tier: $TIER (free tier)"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

read -p "Continue with this configuration? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Setup cancelled."
    exit 0
fi

# Check if instance already exists
if gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID &> /dev/null; then
    echo ""
    echo "⚠️  Instance '$INSTANCE_NAME' already exists!"
    read -p "Do you want to use the existing instance? (y/n): " USE_EXISTING
    if [ "$USE_EXISTING" != "y" ]; then
        echo "Setup cancelled. Please use a different instance name."
        exit 0
    fi
    echo "Using existing instance..."
else
    # Create Cloud SQL instance
    echo ""
    echo "Creating Cloud SQL instance... (this takes 5-10 minutes)"
    gcloud sql instances create $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --database-version=$DATABASE_VERSION \
        --tier=$TIER \
        --region=$REGION \
        --no-assign-ip \
        --network=default \
        --database-flags=max_connections=100

    echo "✅ Cloud SQL instance created: $INSTANCE_NAME"
fi

# Create database
echo ""
echo "Creating database: $DB_NAME"
if gcloud sql databases describe $DB_NAME --instance=$INSTANCE_NAME --project=$PROJECT_ID &> /dev/null; then
    echo "Database '$DB_NAME' already exists, skipping..."
else
    gcloud sql databases create $DB_NAME \
        --instance=$INSTANCE_NAME \
        --project=$PROJECT_ID
    echo "✅ Database created: $DB_NAME"
fi

# Create user with password
echo ""
echo "Creating database user: $DB_USER"
read -s -p "Enter password for $DB_USER: " DB_PASSWORD
echo ""

if gcloud sql users describe $DB_USER --instance=$INSTANCE_NAME --project=$PROJECT_ID &> /dev/null; then
    echo "User '$DB_USER' already exists, updating password..."
    gcloud sql users set-password $DB_USER \
        --instance=$INSTANCE_NAME \
        --project=$PROJECT_ID \
        --password=$DB_PASSWORD
else
    gcloud sql users create $DB_USER \
        --instance=$INSTANCE_NAME \
        --project=$PROJECT_ID \
        --password=$DB_PASSWORD
    echo "✅ User created: $DB_USER"
fi

# Get connection details
echo ""
echo "=== Connection Details ==="
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
echo ""

# Generate DATABASE_URL
echo "Add this to your .env file:"
echo ""
echo "# For Cloud SQL with Unix socket (recommended for Cloud Run/App Engine)"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$CONNECTION_NAME"
echo ""
echo "# For local development with Cloud SQL Proxy"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""

# Instructions for Cloud SQL Proxy
echo "=== Local Development Setup ==="
echo ""
echo "To connect from your local machine, install and run Cloud SQL Proxy:"
echo ""
echo "1. Download Cloud SQL Proxy:"
echo "   curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64"
echo "   chmod +x cloud-sql-proxy"
echo ""
echo "2. Run Cloud SQL Proxy:"
echo "   ./cloud-sql-proxy $CONNECTION_NAME"
echo ""
echo "3. In another terminal, connect to database:"
echo "   psql \"postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME\""
echo ""

echo "✅ Cloud SQL setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with DATABASE_URL"
echo "2. Run migrations: python scripts/run_migrations.py"
echo "3. Verify connection: python -c 'from src.session.database import test_connection; test_connection()'"
