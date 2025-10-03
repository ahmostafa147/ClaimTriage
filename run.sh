#!/bin/bash

# Claims Triage Agent - Run Script

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default mode
export APP_MODE=${APP_MODE:-MOCK}

echo "Claims Triage Agent"
echo "==================="
echo "Mode: $APP_MODE"
echo ""

# Check for production mode requirements
if [ "$APP_MODE" = "PROD" ]; then
    if [ -z "$LANDINGAI_API_KEY" ]; then
        echo "WARNING: APP_MODE is PROD but LANDINGAI_API_KEY is not set"
        echo "Falling back to MOCK mode"
        export APP_MODE=MOCK
    else
        echo "Using LandingAI ADE for extraction"
    fi
fi

if [ "$APP_MODE" = "MOCK" ]; then
    echo "Using MOCK mode with synthetic documents"
fi

echo ""
echo "Starting Streamlit..."
echo ""

# Run streamlit
streamlit run app.py --server.port 8501 --server.address localhost
