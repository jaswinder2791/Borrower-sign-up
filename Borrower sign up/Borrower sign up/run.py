#!/usr/bin/env python3
"""
LoanPro Application Runner
"""

import os
import sys
from app import app, init_db

def main():
    """Main function to run the application"""
    
    # Initialize database if it doesn't exist
    if not os.path.exists('loanpro.db'):
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")
    
    # Set environment variables if not set
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Run the application
    print("Starting LoanPro Application...")
    print("Access the application at: http://localhost:5000")
    print("Admin panel at: http://localhost:5000/admin")
    print("Default admin credentials: admin / admin123")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\nShutting down LoanPro Application...")
        sys.exit(0)

if __name__ == '__main__':
    main()