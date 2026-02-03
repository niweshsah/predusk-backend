"""
Me-API Playground - FastAPI Backend
Main application file with all API endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from typing import List, Optional
from datetime import datetime
import os
from contextlib import asynccontextmanager
# from fastapi import FastAPI
from database import get_db, init_db, check_db_connection
from models import Profile, Education, WorkExperience, Project, Skill, SocialLink
from schemas import (
    ProfileResponse, ProfileUpdate,
    EducationResponse, WorkExperienceResponse,
    ProjectResponse, SkillResponse, SkillWithCount,
    SocialLinkResponse, SearchResult, HealthResponse
)
from auth import verify_credentials

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("🚀 Starting Me-API Playground...")
    init_db()
    if check_db_connection(): # No arguments needed now!
        print("✅ Database connected successfully")
    else:
        print("⚠️  Database connection failed - check configuration")
    
    yield # The app stays here while running
    
    # --- Shutdown (Optional) ---
    print("Shutting down...")

app = FastAPI(
    title="Me-API Playground",
    lifespan=lifespan, # Register the lifespan handler here
    description="A live, queryable resume/portfolio API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Allow requests from Streamlit frontend
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["*"],  # Add "*" for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Startup Event =====
# @app.on_event("startup")
# async def startup_event():
#     """Initialize database on startup"""
#     print("🚀 Starting Me-API Playground...")
#     init_db()
#     if check_db_connection():
#         print("✅ Database connected successfully")
#     else:
#         print("⚠️  Database connection failed - check configuration")


# ===== Health Check Endpoint =====
@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Check if the API is running and database is connected
    
    Returns health status, timestamp, and database connectivity
    """
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        version="1.0.0"
    )


# ===== Profile Endpoints =====
@app.get("/profile", response_model=ProfileResponse, tags=["Profile"])
def get_profile(db: Session = Depends(get_db)):
    """
    Get complete profile with all related data
    
    Returns:
        - Profile information
        - Education history
        - Work experience
        - Projects with associated skills
        - Skills
        - Social links
    """
    profile = db.query(Profile).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@app.put("/profile", response_model=ProfileResponse, tags=["Profile"])
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """
    Update profile information (requires authentication)
    
    Protected endpoint - requires Basic Auth
    Updates profile and optionally replaces related data
    """
    profile = db.query(Profile).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update basic profile fields
    profile.name = profile_data.name
    profile.email = profile_data.email
    profile.phone = profile_data.phone
    profile.location = profile_data.location
    profile.bio = profile_data.bio
    profile.updated_at = datetime.utcnow()
    
    # Update education if provided
    if profile_data.education is not None:
        # Delete existing education
        db.query(Education).filter(Education.profile_id == profile.id).delete()
        # Add new education
        for edu in profile_data.education:
            new_edu = Education(profile_id=profile.id, **edu.model_dump())
            db.add(new_edu)
    
    # Update work experience if provided
    if profile_data.work_experience is not None:
        db.query(WorkExperience).filter(WorkExperience.profile_id == profile.id).delete()
        for work in profile_data.work_experience:
            new_work = WorkExperience(profile_id=profile.id, **work.model_dump())
            db.add(new_work)
    
    # Update skills if provided
    if profile_data.skills is not None:
        db.query(Skill).filter(Skill.profile_id == profile.id).delete()
        for skill in profile_data.skills:
            new_skill = Skill(profile_id=profile.id, **skill.model_dump())
            db.add(new_skill)
    
    # Update projects if provided
    if profile_data.projects is not None:
        db.query(Project).filter(Project.profile_id == profile.id).delete()
        for project in profile_data.projects:
            project_dict = project.model_dump()
            skill_ids = project_dict.pop('skill_ids', [])
            new_project = Project(profile_id=profile.id, **project_dict)
            
            # Associate skills with project
            if skill_ids:
                skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
                new_project.skills.extend(skills)
            
            db.add(new_project)
    
    # Update social links if provided
    if profile_data.social_links is not None:
        db.query(SocialLink).filter(SocialLink.profile_id == profile.id).delete()
        for link in profile_data.social_links:
            new_link = SocialLink(profile_id=profile.id, **link.model_dump())
            db.add(new_link)
    
    db.commit()
    db.refresh(profile)
    
    return profile


# ===== Projects Endpoints =====
@app.get("/projects", response_model=List[ProjectResponse], tags=["Projects"])
def get_projects(
    skill: Optional[str] = Query(None, description="Filter projects by skill name"),
    status: Optional[str] = Query(None, description="Filter by status (completed, in-progress, archived)"),
    db: Session = Depends(get_db)
):
    """
    Get all projects with optional filtering
    
    Query Parameters:
        - skill: Filter projects that use a specific skill
        - status: Filter by project status
    """
    query = db.query(Project)
    
    # Filter by skill if provided
    if skill:
        query = query.join(Project.skills).filter(
            func.lower(Skill.name) == skill.lower()
        )
    
    # Filter by status if provided
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.all()
    return projects


# ===== Skills Endpoints =====
@app.get("/skills/top", response_model=List[SkillWithCount], tags=["Skills"])
def get_top_skills(
    limit: int = Query(10, ge=1, le=50, description="Number of top skills to return"),
    db: Session = Depends(get_db)
):
    """
    Get the most-used skills based on project count
    
    Returns skills ordered by the number of projects they're used in
    """
    # Query skills with project count
    skills_with_counts = (
        db.query(
            Skill,
            func.count(Project.id).label('project_count')
        )
        .outerjoin(Skill.projects)
        .group_by(Skill.id)
        .order_by(desc('project_count'))
        .limit(limit)
        .all()
    )
    
    # Format response
    result = []
    for skill, count in skills_with_counts:
        skill_dict = {
            "id": skill.id,
            "name": skill.name,
            "level": skill.level,
            "category": skill.category,
            "years_experience": skill.years_experience,
            "project_count": count
        }
        result.append(SkillWithCount(**skill_dict))
    
    return result


# ===== Search Endpoint =====
@app.get("/search", response_model=List[SearchResult], tags=["Search"])
def search_content(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Global search across projects and work experience
    
    Searches in:
        - Project names and descriptions
        - Work experience positions and descriptions
    
    Returns results ordered by relevance
    """
    search_term = f"%{q.lower()}%"
    results = []
    
    # Search projects
    projects = db.query(Project).filter(
        or_(
            func.lower(Project.name).like(search_term),
            func.lower(Project.description).like(search_term)
        )
    ).all()
    
    for project in projects:
        # Calculate simple relevance score (can be improved with full-text search)
        score = 1.0
        if project.name and q.lower() in project.name.lower():
            score += 0.5  # Name matches are more relevant
        
        results.append(SearchResult(
            type="project",
            id=project.id,
            title=project.name,
            description=project.description,
            relevance_score=score
        ))
    
    # Search work experience
    work_experiences = db.query(WorkExperience).filter(
        or_(
            func.lower(WorkExperience.position).like(search_term),
            func.lower(WorkExperience.description).like(search_term),
            func.lower(WorkExperience.company).like(search_term)
        )
    ).all()
    
    for work in work_experiences:
        score = 1.0
        if work.position and q.lower() in work.position.lower():
            score += 0.5
        
        results.append(SearchResult(
            type="work_experience",
            id=work.id,
            title=f"{work.position} at {work.company}",
            description=work.description,
            relevance_score=score
        ))
    
    # Sort by relevance score
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return results


# ===== Error Handlers =====
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 error handler"""
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler"""
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
        "status_code": 500
    }


# ===== Root Endpoint =====
@app.get("/", tags=["System"])
def root():
    """
    API root endpoint with basic information and links
    """
    return {
        "name": "Me-API Playground",
        "version": "1.0.0",
        "description": "A live, queryable resume/portfolio API",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "profile": "/profile",
            "projects": "/projects",
            "top_skills": "/skills/top",
            "search": "/search"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
