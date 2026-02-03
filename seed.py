"""
Database Seed Script
Populates the database with initial profile data
"""
from sqlalchemy.orm import Session
from models import Profile, Education, WorkExperience, Project, Skill, SocialLink
from database import SessionLocal, init_db


def seed_database():
    """
    Seed the database with sample profile data
    Replace placeholders with your actual information
    """
    db: Session = SessionLocal()
    
    try:
        # Check if profile already exists
        existing_profile = db.query(Profile).first()
        if existing_profile:
            print("⚠️  Profile already exists. Skipping seed.")
            return
        
        # Create main profile
        profile = Profile(
            name="[YOUR NAME]",
            email="your.email@example.com",
            phone="+1 (555) 123-4567",
            location="San Francisco, CA",
            bio="Full-Stack Engineer and System Architect with expertise in building scalable web applications. Passionate about clean code, system design, and solving complex problems."
        )
        db.add(profile)
        db.flush()  # Get profile.id
        
        # Add education
        education_data = [
            Education(
                profile_id=profile.id,
                institution="University of Technology",
                degree="Bachelor of Science",
                field="Computer Science",
                start_date="2016-09",
                end_date="2020-05",
                gpa=3.8,
                description="Focus on algorithms, data structures, and software engineering"
            ),
            Education(
                profile_id=profile.id,
                institution="Tech Bootcamp",
                degree="Full-Stack Web Development Certificate",
                field="Web Development",
                start_date="2020-06",
                end_date="2020-09",
                description="Intensive program covering React, Node.js, and modern web technologies"
            )
        ]
        db.add_all(education_data)
        
        # Add work experience
        work_data = [
            WorkExperience(
                profile_id=profile.id,
                company="Tech Innovations Inc.",
                position="Senior Full-Stack Engineer",
                description="Led development of cloud-native microservices architecture. Improved system performance by 40% and reduced infrastructure costs by 30%.",
                start_date="2022-01",
                end_date="Present",
                is_current=True,
                location="San Francisco, CA"
            ),
            WorkExperience(
                profile_id=profile.id,
                company="StartupXYZ",
                position="Full-Stack Developer",
                description="Built RESTful APIs and responsive frontend applications. Collaborated with cross-functional teams to deliver features on tight deadlines.",
                start_date="2020-10",
                end_date="2021-12",
                is_current=False,
                location="Remote"
            ),
            WorkExperience(
                profile_id=profile.id,
                company="Digital Solutions Co.",
                position="Junior Developer",
                description="Developed and maintained web applications using React and Django. Implemented automated testing and CI/CD pipelines.",
                start_date="2020-06",
                end_date="2020-09",
                is_current=False,
                location="New York, NY"
            )
        ]
        db.add_all(work_data)
        
        # Add skills
        skills_data = [
            # Frontend
            Skill(profile_id=profile.id, name="React", level="expert", category="frontend", years_experience=4.0),
            Skill(profile_id=profile.id, name="TypeScript", level="advanced", category="frontend", years_experience=3.5),
            Skill(profile_id=profile.id, name="Vue.js", level="intermediate", category="frontend", years_experience=2.0),
            Skill(profile_id=profile.id, name="HTML/CSS", level="expert", category="frontend", years_experience=5.0),
            Skill(profile_id=profile.id, name="Tailwind CSS", level="advanced", category="frontend", years_experience=2.5),
            
            # Backend
            Skill(profile_id=profile.id, name="Node.js", level="expert", category="backend", years_experience=4.0),
            Skill(profile_id=profile.id, name="Python", level="expert", category="backend", years_experience=4.5),
            Skill(profile_id=profile.id, name="FastAPI", level="advanced", category="backend", years_experience=2.0),
            Skill(profile_id=profile.id, name="Express.js", level="advanced", category="backend", years_experience=3.5),
            Skill(profile_id=profile.id, name="Django", level="intermediate", category="backend", years_experience=2.0),
            
            # Database
            Skill(profile_id=profile.id, name="PostgreSQL", level="advanced", category="database", years_experience=3.5),
            Skill(profile_id=profile.id, name="MongoDB", level="advanced", category="database", years_experience=3.0),
            Skill(profile_id=profile.id, name="Redis", level="intermediate", category="database", years_experience=2.0),
            
            # DevOps
            Skill(profile_id=profile.id, name="Docker", level="advanced", category="devops", years_experience=3.0),
            Skill(profile_id=profile.id, name="AWS", level="advanced", category="devops", years_experience=2.5),
            Skill(profile_id=profile.id, name="CI/CD", level="advanced", category="devops", years_experience=3.0),
            Skill(profile_id=profile.id, name="Kubernetes", level="intermediate", category="devops", years_experience=1.5),
        ]
        db.add_all(skills_data)
        db.flush()  # Get skill IDs
        
        # Create skill name to ID mapping for projects
        skill_map = {skill.name: skill.id for skill in skills_data}
        
        # Add projects
        projects_data = [
            Project(
                profile_id=profile.id,
                name="E-Commerce Platform",
                description="Full-featured e-commerce platform with real-time inventory management, payment processing, and admin dashboard. Built with microservices architecture.",
                github_url="https://github.com/yourusername/ecommerce-platform",
                demo_url="https://ecommerce-demo.example.com",
                start_date="2023-01",
                end_date="2023-06",
                status="completed"
            ),
            Project(
                profile_id=profile.id,
                name="Real-Time Analytics Dashboard",
                description="Interactive dashboard for visualizing business metrics with WebSocket connections for live updates. Handles 10,000+ concurrent users.",
                github_url="https://github.com/yourusername/analytics-dashboard",
                demo_url="https://analytics-demo.example.com",
                start_date="2023-07",
                end_date="2023-11",
                status="completed"
            ),
            Project(
                profile_id=profile.id,
                name="AI-Powered Chatbot",
                description="Customer service chatbot using natural language processing. Reduced support tickets by 35% and improved response times.",
                github_url="https://github.com/yourusername/ai-chatbot",
                start_date="2024-01",
                end_date="Present",
                status="in-progress"
            ),
            Project(
                profile_id=profile.id,
                name="Task Management API",
                description="RESTful API for team collaboration and task tracking. Features include real-time notifications, file attachments, and advanced filtering.",
                github_url="https://github.com/yourusername/task-api",
                demo_url="https://task-api-docs.example.com",
                start_date="2022-08",
                end_date="2022-12",
                status="completed"
            ),
        ]
        db.add_all(projects_data)
        db.flush()
        
        # Associate skills with projects
        # E-Commerce Platform - React, TypeScript, Node.js, PostgreSQL, Docker, AWS
        projects_data[0].skills.extend([
            s for s in skills_data if s.name in ["React", "TypeScript", "Node.js", "PostgreSQL", "Docker", "AWS"]
        ])
        
        # Analytics Dashboard - React, TypeScript, FastAPI, Redis, MongoDB
        projects_data[1].skills.extend([
            s for s in skills_data if s.name in ["React", "TypeScript", "FastAPI", "Redis", "MongoDB"]
        ])
        
        # AI Chatbot - Python, FastAPI, PostgreSQL
        projects_data[2].skills.extend([
            s for s in skills_data if s.name in ["Python", "FastAPI", "PostgreSQL"]
        ])
        
        # Task Management API - Node.js, Express.js, MongoDB, Docker
        projects_data[3].skills.extend([
            s for s in skills_data if s.name in ["Node.js", "Express.js", "MongoDB", "Docker"]
        ])
        
        # Add social links
        social_data = [
            SocialLink(
                profile_id=profile.id,
                platform="GitHub",
                url="https://github.com/yourusername",
                icon="github"
            ),
            SocialLink(
                profile_id=profile.id,
                platform="LinkedIn",
                url="https://linkedin.com/in/yourprofile",
                icon="linkedin"
            ),
            SocialLink(
                profile_id=profile.id,
                platform="Twitter",
                url="https://twitter.com/yourusername",
                icon="twitter"
            ),
            SocialLink(
                profile_id=profile.id,
                platform="Portfolio",
                url="https://yourportfolio.com",
                icon="globe"
            ),
        ]
        db.add_all(social_data)
        
        # Commit all changes
        db.commit()
        print("✅ Database seeded successfully!")
        print(f"   Profile: {profile.name}")
        print(f"   Education entries: {len(education_data)}")
        print(f"   Work experiences: {len(work_data)}")
        print(f"   Skills: {len(skills_data)}")
        print(f"   Projects: {len(projects_data)}")
        print(f"   Social links: {len(social_data)}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Initializing database and seeding data...")
    init_db()
    seed_database()
