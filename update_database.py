#!/usr/bin/env python3
"""
Script to update your profile via API
Run: python update_database.py
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
import os

load_dotenv()


# Get credentials from environment variables
API_URL = os.getenv("API_URL", "https://me-api-backend.onrender.com")
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD", "hello123")


# Configuration
# API_URL = "https://me-api-backend.onrender.com"  # Change to your URL
# USERNAME = "admin"
# PASSWORD = "YourSecurePassword123"  # Your actual password

# Your complete updated profile
new_profile_data = {
    "name": "Jane Smith",
    "email": "jane.smith@gmail.com",
    "phone": "+1 (415) 555-0123",
    "location": "San Francisco, CA",
    "bio": "Senior Full-Stack Engineer with 6 years of experience building scalable web applications. Passionate about clean code, system design, and mentoring junior developers.",
    
    "education": [
        {
            "institution": "Stanford University",
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "start_date": "2015-09",
            "end_date": "2019-05",
            "gpa": 3.85,
            "description": "Specialized in distributed systems and machine learning. Dean's List all 4 years."
        },
        {
            "institution": "MIT",
            "degree": "Master of Science",
            "field": "Artificial Intelligence",
            "start_date": "2019-09",
            "end_date": "2021-05",
            "gpa": 3.9,
            "description": "Thesis on neural architecture search for efficient deep learning models."
        }
    ],
    
    "work_experience": [
        {
            "company": "Meta",
            "position": "Senior Software Engineer",
            "description": "Lead engineer for messaging infrastructure. Rebuilt core systems to handle 10B+ messages/day. Reduced latency by 60% and costs by 40%. Mentor to 3 junior engineers.",
            "start_date": "2021-03",
            "end_date": "Present",
            "is_current": True,
            "location": "Menlo Park, CA"
        },
        {
            "company": "Stripe",
            "position": "Software Engineer",
            "description": "Built payment processing APIs handling $10M+ daily transactions. Implemented fraud detection system reducing chargebacks by 25%.",
            "start_date": "2019-06",
            "end_date": "2021-02",
            "is_current": False,
            "location": "San Francisco, CA"
        },
        {
            "company": "Google",
            "position": "Software Engineering Intern",
            "description": "Developed Chrome extension features used by 1M+ users. Improved performance by 30%.",
            "start_date": "2018-06",
            "end_date": "2018-08",
            "is_current": False,
            "location": "Mountain View, CA"
        }
    ],
    
    "skills": [
        # Backend
        {"name": "Python", "level": "expert", "category": "backend", "years_experience": 6.0},
        {"name": "JavaScript", "level": "expert", "category": "backend", "years_experience": 5.0},
        {"name": "TypeScript", "level": "advanced", "category": "backend", "years_experience": 4.0},
        {"name": "Node.js", "level": "expert", "category": "backend", "years_experience": 5.0},
        {"name": "FastAPI", "level": "advanced", "category": "backend", "years_experience": 3.0},
        {"name": "Django", "level": "intermediate", "category": "backend", "years_experience": 2.0},
        {"name": "Go", "level": "intermediate", "category": "backend", "years_experience": 2.0},
        
        # Frontend
        {"name": "React", "level": "expert", "category": "frontend", "years_experience": 5.0},
        {"name": "Next.js", "level": "advanced", "category": "frontend", "years_experience": 3.0},
        {"name": "Vue.js", "level": "intermediate", "category": "frontend", "years_experience": 2.0},
        {"name": "Tailwind CSS", "level": "advanced", "category": "frontend", "years_experience": 3.0},
        
        # Database
        {"name": "PostgreSQL", "level": "expert", "category": "database", "years_experience": 5.0},
        {"name": "MongoDB", "level": "advanced", "category": "database", "years_experience": 4.0},
        {"name": "Redis", "level": "advanced", "category": "database", "years_experience": 3.0},
        {"name": "Elasticsearch", "level": "intermediate", "category": "database", "years_experience": 2.0},
        
        # DevOps
        {"name": "Docker", "level": "expert", "category": "devops", "years_experience": 4.0},
        {"name": "Kubernetes", "level": "advanced", "category": "devops", "years_experience": 3.0},
        {"name": "AWS", "level": "advanced", "category": "devops", "years_experience": 4.0},
        {"name": "CI/CD", "level": "advanced", "category": "devops", "years_experience": 4.0},
        {"name": "Terraform", "level": "intermediate", "category": "devops", "years_experience": 2.0},
    ],
    
    "projects": [
        {
            "name": "Real-Time Analytics Platform",
            "description": "Built enterprise analytics platform processing 100K events/second using WebSockets, React, and PostgreSQL. Deployed on AWS with auto-scaling. Used by 500+ companies to track user behavior and generate insights.",
            "github_url": "https://github.com/janesmith/analytics-platform",
            "demo_url": "https://analytics-demo.janesmith.com",
            "start_date": "2023-01",
            "end_date": "2023-08",
            "status": "completed",
            "skill_ids": []
        },
        {
            "name": "AI Content Generator",
            "description": "AI-powered writing assistant using GPT-4 API, React, and FastAPI. Generates blog posts, emails, social media content. 10K+ active users. Integrated with Stripe for subscription billing.",
            "github_url": "https://github.com/janesmith/ai-writer",
            "demo_url": "https://aiwriter.janesmith.com",
            "start_date": "2023-09",
            "end_date": "Present",
            "status": "in-progress",
            "skill_ids": []
        },
        {
            "name": "E-Commerce Microservices",
            "description": "Scalable e-commerce platform using microservices architecture. Handles 10K+ orders/day. Built with Node.js, PostgreSQL, RabbitMQ, and Docker. Deployed on Kubernetes with 99.9% uptime.",
            "github_url": "https://github.com/janesmith/ecommerce-api",
            "start_date": "2022-03",
            "end_date": "2022-11",
            "status": "completed",
            "skill_ids": []
        },
        {
            "name": "DevOps Automation Toolkit",
            "description": "CLI tool for automating cloud infrastructure deployment. Supports AWS, GCP, Azure. Written in Go. Used internally by 50+ developers.",
            "github_url": "https://github.com/janesmith/devops-toolkit",
            "start_date": "2022-01",
            "end_date": "2022-05",
            "status": "completed",
            "skill_ids": []
        }
    ],
    
    "social_links": [
        {"platform": "GitHub", "url": "https://github.com/janesmith", "icon": "github"},
        {"platform": "LinkedIn", "url": "https://linkedin.com/in/janesmith", "icon": "linkedin"},
        {"platform": "Twitter", "url": "https://twitter.com/janesmith", "icon": "twitter"},
        {"platform": "Portfolio", "url": "https://janesmith.com", "icon": "globe"},
        {"platform": "Medium", "url": "https://medium.com/@janesmith", "icon": "medium"},
    ]
}

def update_profile():
    """Update profile via API"""
    print("🔄 Updating profile...")
    print(f"API URL: {API_URL}")
    
    try:
        response = requests.put(
            f"{API_URL}/profile",
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            json=new_profile_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Profile updated successfully!")
            print("\n📊 Updated profile:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Profile Update Script")
    print("=" * 60)
    update_profile()