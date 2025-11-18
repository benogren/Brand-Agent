#!/usr/bin/env python3
"""
Setup script for Vertex AI Memory Bank collection.

This script helps create and configure the Memory Bank collection
for AI Brand Studio's long-term memory capabilities.

Memory Bank collections are created through gcloud CLI or Cloud Console.
This script provides instructions and validation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_setup_instructions():
    """Print instructions for creating Memory Bank collection."""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'YOUR_PROJECT_ID')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    collection_id = os.getenv('MEMORY_BANK_COLLECTION_ID', 'brand_studio_memories')

    print("=" * 80)
    print("Vertex AI Memory Bank Setup Instructions")
    print("=" * 80)
    print()
    print("Memory Bank is currently in preview and requires setup through gcloud CLI.")
    print()
    print("📋 **Prerequisites:**")
    print("  - Google Cloud project with Vertex AI API enabled")
    print("  - gcloud CLI installed and authenticated")
    print("  - Vertex AI Memory Bank preview access enabled")
    print()
    print("=" * 80)
    print("Setup Steps:")
    print("=" * 80)
    print()
    print("1. **Enable Vertex AI API** (if not already enabled):")
    print(f"   gcloud services enable aiplatform.googleapis.com --project={project_id}")
    print()
    print("2. **Set default project and location:**")
    print(f"   gcloud config set project {project_id}")
    print(f"   gcloud config set ai/region {location}")
    print()
    print("3. **Create Memory Bank Collection:**")
    print()
    print("   Note: As of November 2024, Memory Bank is in preview.")
    print("   The exact command may vary. Check latest documentation:")
    print("   https://cloud.google.com/vertex-ai/docs/generative-ai/context-cache/memory-bank")
    print()
    print("   Expected command format (when available):")
    print(f"   gcloud ai memory-banks create {collection_id} \\")
    print(f"     --project={project_id} \\")
    print(f"     --region={location} \\")
    print("     --description='Long-term memory for AI Brand Studio'")
    print()
    print("4. **Update .env file** with collection ID:")
    print(f"   MEMORY_BANK_COLLECTION_ID={collection_id}")
    print()
    print("=" * 80)
    print("Alternative: File-based Fallback")
    print("=" * 80)
    print()
    print("If Memory Bank is not yet available, the system will automatically")
    print("use file-based storage in the .memory_bank/ directory.")
    print()
    print("This provides the same functionality for development and testing.")
    print()
    print("=" * 80)
    print("Validation")
    print("=" * 80)
    print()
    print("To verify your Memory Bank setup, run:")
    print("  python scripts/test_memory_bank.py")
    print()
    print("=" * 80)


def check_memory_bank_availability():
    """Check if Memory Bank is available and configured."""
    print("\n🔍 Checking Memory Bank availability...")
    print()

    # Check if project is configured
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set in .env")
        return False

    print(f"✅ Project ID: {project_id}")

    # Try to import Memory Bank client
    try:
        from src.session.memory_bank import MemoryBankClient

        client = MemoryBankClient()
        print(f"✅ Memory Bank client initialized")
        print(f"   Collection ID: {client.collection_id}")

        if client.memory_bank is None:
            print("⚠️  Memory Bank API not available - using file-based fallback")
            print("   Files will be stored in .memory_bank/ directory")
        else:
            print("✅ Memory Bank API available")

        return True

    except Exception as e:
        print(f"❌ Failed to initialize Memory Bank client: {e}")
        return False


def create_memory_bank_directory():
    """Create directory for file-based fallback storage."""
    from pathlib import Path

    memory_dir = Path(".memory_bank")
    memory_dir.mkdir(exist_ok=True)

    gitignore_file = memory_dir / ".gitignore"
    gitignore_file.write_text("# Ignore all memory files\n*\n!.gitignore\n")

    print()
    print("✅ Created .memory_bank/ directory for fallback storage")
    print("   (Added .gitignore to exclude from version control)")


if __name__ == "__main__":
    print()
    print_setup_instructions()

    # Check if Memory Bank is available
    available = check_memory_bank_availability()

    # Create fallback directory
    create_memory_bank_directory()

    print()
    print("=" * 80)
    print("Setup Complete!")
    print("=" * 80)
    print()

    if available:
        print("✅ Memory Bank client is ready to use")
        print()
        print("Next steps:")
        print("  1. Test the memory bank: python scripts/test_memory_bank.py")
        print("  2. Integrate with orchestrator for learning capabilities")
    else:
        print("⚠️  Memory Bank API not available")
        print()
        print("The system will use file-based fallback storage.")
        print("This is fully functional for development and testing.")

    print()
    sys.exit(0 if available else 1)
