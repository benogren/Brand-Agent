#!/bin/bash
# Secret Manager Setup Script for AI Brand Studio
# Configures secrets for API keys (Namecheap, USPTO, social media)

set -e  # Exit on error

echo "=== AI Brand Studio - Secret Manager Setup ==="
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
echo ""

# Function to create or update a secret
create_or_update_secret() {
    local secret_name=$1
    local secret_description=$2
    local secret_value=$3

    # Check if secret already exists
    if gcloud secrets describe $secret_name --project=$PROJECT_ID &> /dev/null; then
        echo "Secret '$secret_name' already exists. Adding new version..."
        echo -n "$secret_value" | gcloud secrets versions add $secret_name \
            --project=$PROJECT_ID \
            --data-file=-
        echo "✅ Updated secret: $secret_name"
    else
        echo "Creating secret: $secret_name"
        echo -n "$secret_value" | gcloud secrets create $secret_name \
            --project=$PROJECT_ID \
            --replication-policy="automatic" \
            --data-file=-

        # Add description/labels
        gcloud secrets update $secret_name \
            --project=$PROJECT_ID \
            --update-labels=app=brand-studio

        echo "✅ Created secret: $secret_name"
    fi
}

echo "This script will help you configure API keys in Secret Manager."
echo "You can skip any optional API keys by pressing Enter."
echo ""

# Namecheap API Key (optional - fallback to python-whois)
echo "--- Namecheap API Key (Optional) ---"
echo "Used for domain availability checking. Falls back to python-whois if not provided."
read -p "Enter Namecheap API key (or press Enter to skip): " NAMECHEAP_KEY
if [ ! -z "$NAMECHEAP_KEY" ]; then
    create_or_update_secret "namecheap-api-key" "Namecheap API key for domain checking" "$NAMECHEAP_KEY"
else
    echo "Skipped Namecheap API key"
fi
echo ""

# USPTO API Key (optional - uses public API by default)
echo "--- USPTO API Key (Optional) ---"
echo "Used for trademark search. Public API used if not provided."
read -p "Enter USPTO API key (or press Enter to skip): " USPTO_KEY
if [ ! -z "$USPTO_KEY" ]; then
    create_or_update_secret "uspto-api-key" "USPTO API key for trademark search" "$USPTO_KEY"
else
    echo "Skipped USPTO API key"
fi
echo ""

# Twitter/X API credentials (optional)
echo "--- Twitter/X API Credentials (Optional) ---"
echo "Used for Twitter handle availability checking."
read -p "Enter Twitter API key (or press Enter to skip): " TWITTER_KEY
if [ ! -z "$TWITTER_KEY" ]; then
    create_or_update_secret "twitter-api-key" "Twitter API key for handle checking" "$TWITTER_KEY"

    read -p "Enter Twitter API secret: " TWITTER_SECRET
    create_or_update_secret "twitter-api-secret" "Twitter API secret for handle checking" "$TWITTER_SECRET"
else
    echo "Skipped Twitter API credentials"
fi
echo ""

# Instagram API credentials (optional)
echo "--- Instagram API Credentials (Optional) ---"
echo "Used for Instagram handle availability checking."
read -p "Enter Instagram API key (or press Enter to skip): " INSTAGRAM_KEY
if [ ! -z "$INSTAGRAM_KEY" ]; then
    create_or_update_secret "instagram-api-key" "Instagram API key for handle checking" "$INSTAGRAM_KEY"
else
    echo "Skipped Instagram API credentials"
fi
echo ""

# LinkedIn API credentials (optional)
echo "--- LinkedIn API Credentials (Optional) ---"
echo "Used for LinkedIn handle availability checking."
read -p "Enter LinkedIn API key (or press Enter to skip): " LINKEDIN_KEY
if [ ! -z "$LINKEDIN_KEY" ]; then
    create_or_update_secret "linkedin-api-key" "LinkedIn API key for handle checking" "$LINKEDIN_KEY"
else
    echo "Skipped LinkedIn API credentials"
fi
echo ""

# Database password (recommended)
echo "--- Database Password (Recommended) ---"
echo "Store your Cloud SQL database password securely."
read -p "Store database password in Secret Manager? (y/n): " STORE_DB_PASSWORD
if [ "$STORE_DB_PASSWORD" = "y" ]; then
    read -s -p "Enter database password: " DB_PASSWORD
    echo ""
    create_or_update_secret "database-password" "Cloud SQL database password" "$DB_PASSWORD"
fi
echo ""

# List all secrets
echo "=== Configured Secrets ==="
gcloud secrets list --project=$PROJECT_ID --filter="labels.app=brand-studio" --format="table(name,createTime)"
echo ""

# Show how to access secrets in Python
echo "=== Accessing Secrets in Python ==="
cat <<'EOF'

To access secrets in your code, use the Google Cloud Secret Manager client:

```python
from google.cloud import secretmanager

def access_secret(secret_id: str, project_id: str) -> str:
    """Access a secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Example usage:
namecheap_key = access_secret('namecheap-api-key', 'your-project-id')
```

Or use the helper in src/infrastructure/secrets.py (will be created in later tasks).
EOF

echo ""
echo "✅ Secret Manager setup complete!"
echo ""
echo "Next steps:"
echo "1. Secrets are now stored securely in Secret Manager"
echo "2. Update src/infrastructure/secrets.py to access these secrets"
echo "3. Never commit API keys to git - they're safe in Secret Manager"
