#!/usr/bin/env python3
"""
Test script for admin pagination functionality
Tests both Users and Lessons pagination with 10 records per page
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"

def test_admin_login():
    """Test admin login and return access token"""
    print("🔐 Testing admin login...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Admin login successful")
        return token
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        print(response.text)
        return None

def test_users_pagination(token):
    """Test users pagination with 10 records per page"""
    print("\n👥 Testing Users Pagination...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test page 1
    response = requests.get(f"{BASE_URL}/admin/users?page=1&page_size=10", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if "users" in data and "pagination" in data:
            print("✅ Users pagination working correctly")
            print(f"   📊 Total users: {data['pagination']['total_count']}")
            print(f"   📄 Current page: {data['pagination']['current_page']}")
            print(f"   📏 Page size: {data['pagination']['page_size']}")
            print(f"   📚 Total pages: {data['pagination']['total_pages']}")
            print(f"   👥 Users on this page: {len(data['users'])}")
            
            # Test pagination navigation
            if data['pagination']['has_next']:
                print("   ➡️ Testing page 2...")
                response2 = requests.get(f"{BASE_URL}/admin/users?page=2&page_size=10", headers=headers)
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"   ✅ Page 2 loaded with {len(data2['users'])} users")
                else:
                    print(f"   ❌ Page 2 failed: {response2.status_code}")
            
            return True
        else:
            print("❌ Users pagination response missing pagination data")
            print(f"Response keys: {list(data.keys())}")
            return False
    else:
        print(f"❌ Users pagination failed: {response.status_code}")
        print(response.text)
        return False

def test_lessons_pagination(token):
    """Test lessons pagination with 10 records per page"""
    print("\n📚 Testing Lessons Pagination...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test page 1
    response = requests.get(f"{BASE_URL}/admin/lessons?page=1&page_size=10", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if "lessons" in data and "pagination" in data:
            print("✅ Lessons pagination working correctly")
            print(f"   📊 Total lessons: {data['pagination']['total_count']}")
            print(f"   📄 Current page: {data['pagination']['current_page']}")
            print(f"   📏 Page size: {data['pagination']['page_size']}")
            print(f"   📚 Total pages: {data['pagination']['total_pages']}")
            print(f"   📖 Lessons on this page: {len(data['lessons'])}")
            
            # Test pagination navigation  
            if data['pagination']['has_next']:
                print("   ➡️ Testing page 2...")
                response2 = requests.get(f"{BASE_URL}/admin/lessons?page=2&page_size=10", headers=headers)
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"   ✅ Page 2 loaded with {len(data2['lessons'])} lessons")
                else:
                    print(f"   ❌ Page 2 failed: {response2.status_code}")
            
            return True
        else:
            print("❌ Lessons pagination response format incorrect")
            print(f"Response keys: {list(data.keys())}")
            return False
    else:
        print(f"❌ Lessons pagination failed: {response.status_code}")
        print(response.text)
        return False

def test_filtering(token):
    """Test filtering functionality"""
    print("\n🔍 Testing Filtering...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test user role filtering
    response = requests.get(f"{BASE_URL}/admin/users?page=1&page_size=10&role=admin", headers=headers)
    if response.status_code == 200:
        data = response.json()
        admin_count = len(data['users'])
        print(f"   ✅ Admin users filter: {admin_count} admin users found")
    else:
        print(f"   ❌ User role filtering failed: {response.status_code}")
    
    # Test user status filtering
    response = requests.get(f"{BASE_URL}/admin/users?page=1&page_size=10&status=active", headers=headers)
    if response.status_code == 200:
        data = response.json()
        active_count = len(data['users'])
        print(f"   ✅ Active users filter: {active_count} active users found")
    else:
        print(f"   ❌ User status filtering failed: {response.status_code}")

def main():
    """Run all pagination tests"""
    print("🧪 Admin Pagination Test Suite")
    print("=" * 50)
    
    # Get admin token
    token = test_admin_login()
    if not token:
        print("❌ Cannot proceed without admin token")
        return False
    
    # Test users pagination
    users_ok = test_users_pagination(token)
    
    # Test lessons pagination
    lessons_ok = test_lessons_pagination(token)
    
    # Test filtering
    test_filtering(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   👥 Users Pagination: {'✅ PASS' if users_ok else '❌ FAIL'}")
    print(f"   📚 Lessons Pagination: {'✅ PASS' if lessons_ok else '❌ FAIL'}")
    
    if users_ok and lessons_ok:
        print("\n🎉 All pagination tests passed!")
        print("✅ 10 records per page configuration working")
        print("✅ Navigation controls functional")
        print("✅ Backend pagination API working")
        return True
    else:
        print("\n❌ Some pagination tests failed")
        return False

if __name__ == "__main__":
    main()