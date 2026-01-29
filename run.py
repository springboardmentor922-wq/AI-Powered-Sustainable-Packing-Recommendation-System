#!/usr/bin/env python3
"""
EcoPackAI - Run Script
Simple script to start the Flask application
"""

from app import app

if __name__ == '__main__':
    print("🚀 Starting EcoPackAI Recommendation System...")
    print("📱 Frontend: http://localhost:5000")
    print("🔌 API: http://localhost:5000/api/")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )
