#!/usr/bin/env python3
"""
Simple script to view all data in the local database
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    db_path = 'loanpro.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all applications
        cursor.execute("""
            SELECT 
                application_id,
                first_name,
                last_name,
                email,
                phone,
                loan_amount,
                annual_income,
                status,
                created_at
            FROM loan_applications 
            ORDER BY created_at DESC
        """)
        
        applications = cursor.fetchall()
        
        print("=" * 100)
        print("📊 LOAN APPLICATIONS DATABASE")
        print("=" * 100)
        print(f"Total Applications: {len(applications)}")
        print("-" * 100)
        
        if applications:
            print(f"{'App ID':<15} {'Name':<25} {'Email':<30} {'Loan Amount':<15} {'Status':<12} {'Date':<20}")
            print("-" * 100)
            
            for app in applications:
                app_id, first_name, last_name, email, phone, loan_amount, annual_income, status, created_at = app
                name = f"{first_name} {last_name}"
                print(f"{app_id:<15} {name:<25} {email:<30} ₹{loan_amount:>12,.0f} {status:<12} {created_at:<20}")
        else:
            print("No applications found in database.")
        
        # Get eligibility data
        cursor.execute("""
            SELECT 
                la.application_id,
                ec.percentage,
                ec.status,
                ec.total_score
            FROM loan_applications la
            JOIN eligibility_checks ec ON la.id = ec.application_id
            ORDER BY ec.percentage DESC
        """)
        
        eligibility_data = cursor.fetchall()
        
        if eligibility_data:
            print("\n" + "=" * 80)
            print("🎯 ELIGIBILITY SCORES")
            print("=" * 80)
            print(f"{'App ID':<15} {'Eligibility %':<15} {'Score':<10} {'Status':<20}")
            print("-" * 80)
            
            for data in eligibility_data:
                app_id, percentage, status, total_score = data
                print(f"{app_id:<15} {percentage:>12.1f}% {total_score:>8}/100 {status:<20}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == '__main__':
    view_database()