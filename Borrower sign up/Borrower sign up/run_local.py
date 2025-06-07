#!/usr/bin/env python3
"""
Local LoanPro Application Runner
No network dependencies - all data stored locally
"""

import os
import sys
import sqlite3
from app import app, init_db

def check_database():
    """Check if database exists and show stats"""
    db_path = 'loanpro.db'
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM loan_applications")
            app_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM loan_applications WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM loan_applications WHERE status = 'approved'")
            approved_count = cursor.fetchone()[0]
            
            print(f"📊 Database Status:")
            print(f"   Total Applications: {app_count}")
            print(f"   Pending: {pending_count}")
            print(f"   Approved: {approved_count}")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Database exists but error reading: {e}")
    else:
        print("📁 Database will be created on first run")

def main():
    """Main function to run the local application"""
    
    print("🏠 LoanPro - LOCAL APPLICATION")
    print("=" * 50)
    print("✅ No internet connection required")
    print("💾 All data stored locally in SQLite database")
    print("🔒 Completely offline operation")
    print()
    
    # Check database status
    check_database()
    print()
    
    # Initialize database if needed
    if not os.path.exists('loanpro.db'):
        print("🔧 Initializing database...")
        init_db()
        print("✅ Database initialized!")
        print()
    
    print("🌐 Application will be available at:")
    print("   🏠 Home Page: http://localhost:5000")
    print("   📝 Apply for Loan: http://localhost:5000/apply")
    print("   🔍 Check Status: http://localhost:5000/check-status")
    print("   👨‍💼 Admin Panel: http://localhost:5000/admin")
    print("   📊 View All Data: http://localhost:5000/view-all-applications")
    print()
    print("🔐 Admin Login:")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("⚡ Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the application on localhost only
        app.run(
            debug=True,
            host='127.0.0.1',  # Only localhost - no network
            port=5000,
            use_reloader=False  # Disable reloader to avoid double initialization
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down LoanPro Application...")
        print("💾 All data has been saved to local database")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()