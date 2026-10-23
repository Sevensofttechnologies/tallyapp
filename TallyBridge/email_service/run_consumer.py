"""
Email Consumer Runner
Start the email microservice consumer
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_service.consumer import run_consumer

if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL MICROSERVICE - RabbitMQ Consumer")
    print("=" * 60)
    print("Starting consumer...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    run_consumer()
