#!/bin/sh
# Export default JWT secret if not set
if [ -z "$JWT_SECRET_KEY" ]; then
    export JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(64))')
fi

# Start the application using uvicorn
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1