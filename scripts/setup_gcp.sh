#!/bin/bash
# Google Cloud Project Setup Script for AI Brand Studio
# This script sets up the required Google Cloud infrastructure

set -e  # Exit on error

echo "=== AI Brand Studio - Google Cloud Setup ==="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for project ID if not set
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    read -p "Enter your Google Cloud Project ID (or press Enter to create new): " PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        read -p "Enter a new project ID to create: " PROJECT_ID
        echo "Creating new project: $PROJECT_ID"
        gcloud projects create $PROJECT_ID
    fi
    export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
else
    PROJECT_ID=$GOOGLE_CLOUD_PROJECT
fi

echo "Using project: $PROJECT_ID"
echo ""

# Set the project
echo "Setting active project..."
gcloud config set project $PROJECT_ID

# Enable billing (manual step - user needs to do this in console)
echo ""
echo "⚠️  IMPORTANT: Ensure billing is enabled for project $PROJECT_ID"
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
read -p "Press Enter once billing is enabled to continue..."

# Enable required APIs
echo ""
echo "Enabling required Google Cloud APIs..."
echo "This may take a few minutes..."

gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudtrace.googleapis.com \
  secretmanager.googleapis.com

echo ""
echo "✅ Required APIs enabled:"
echo "  - Vertex AI (aiplatform.googleapis.com)"
echo "  - Cloud Storage (storage.googleapis.com)"
echo "  - Cloud SQL (sql-component.googleapis.com, sqladmin.googleapis.com)"
echo "  - Cloud Logging (logging.googleapis.com)"
echo "  - Cloud Monitoring (monitoring.googleapis.com)"
echo "  - Cloud Trace (cloudtrace.googleapis.com)"
echo "  - Secret Manager (secretmanager.googleapis.com)"

# Set default region
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
echo ""
echo "Setting default region to: $REGION"
gcloud config set compute/region $REGION

# Authenticate for application default credentials
echo ""
echo "Setting up Application Default Credentials..."
gcloud auth application-default login

echo ""
echo "✅ Google Cloud setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
echo "2. Run scripts/setup_cloud_sql.sh to create database"
echo "3. Run scripts/setup_vector_search.py to create Vector Search index"
