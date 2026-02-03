"""
Me-API Playground - FastAPI Backend
Main application file with all API endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from typing import List, Optional
from datetime import datetime
import os

from database import get_db, init_db, check_db_connection
from models import Profile, Education, WorkExperience, Project, Skill, SocialLink
from schemas import (
    ProfileResponse, ProfileCreate, ProfileUpdate,
    EducationResponse, EducationCreate, EducationUpdate,
    WorkExperienceResponse, WorkExperienceCreate, WorkExperienceUpdate,
    ProjectResponse, ProjectCreate, ProjectUpdate,
    SkillResponse, SkillCreate, SkillUpdate, SkillWithCount,
    SocialLinkResponse, SocialLinkCreate, SocialLinkUpdate,
    SearchResult, HealthResponse
)
from auth import verify_credentials

# Initialize FastAPI app
app = FastAPI(
    title="Me-API Playground",
    description="A live, queryable resume/portfolio API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Startup Event =====
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Me-API Playground...")
    init_db()
    if check_db_connection():
        print("✅ Database connected successfully")
    else:
        print("⚠️  Database connection failed - check configuration")


# ===== Health Check Endpoint =====
@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Check if the API is running and database is connected
    """
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        version="1.0.0"
    )


# ===== Profile CRUD Endpoints =====

@app.get("/profile", response_model=ProfileResponse, tags=["Profile"])
def read_profile(db: Session = Depends(get_db)):
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
        raise HTTPException(
            status_code=404, 
            detail="Profile not found. Create a profile first using POST /profile"
        )
    
    return profile


@app.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED, tags=["Profile"])
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """
    Create a new profile (requires authentication)
    
    Only one profile can exist. If a profile already exists, use PUT /profile to update it.
    
    Protected endpoint - requires Basic Auth
    """
    # Check if profile already exists
    existing_profile = db.query(Profile).first()
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists. Use PUT /profile to update it."
        )
    
    # Create new profile
    profile = Profile(
        name=profile_data.name,
        email=profile_data.email,
        phone=profile_data.phone,
        location=profile_data.location,
        bio=profile_data.bio
    )
    db.add(profile)
    db.flush()  # Get profile.id
    
    # Add education
    for edu_data in profile_data.education:
        education = Education(profile_id=profile.id, **edu_data.model_dump())
        db.add(education)
    
    # Add work experience
    for work_data in profile_data.work_experience:
        work = WorkExperience(profile_id=profile.id, **work_data.model_dump())
        db.add(work)
    
    # Add skills
    for skill_data in profile_data.skills:
        skill = Skill(profile_id=profile.id, **skill_data.model_dump())
        db.add(skill)
    
    db.flush()  # Get skill IDs
    
    # Add projects with skill associations
    for project_data in profile_data.projects:
        project_dict = project_data.model_dump()
        skill_ids = project_dict.pop('skill_ids', [])
        
        project = Project(profile_id=profile.id, **project_dict)
        
        # Associate skills
        if skill_ids:
            skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
            project.skills.extend(skills)
        
        db.add(project)
    
    # Add social links
    for link_data in profile_data.social_links:
        link = SocialLink(profile_id=profile.id, **link_data.model_dump())
        db.add(link)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@app.put("/profile", response_model=ProfileResponse, tags=["Profile"])
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """
    Update existing profile (requires authentication)
    
    This replaces ALL data. To update specific fields, send only those fields.
    Protected endpoint - requires Basic Auth
    """
    profile = db.query(Profile).first()
    
    if not profile:
        raise HTTPException(
            status_code=404, 
            detail="Profile not found. Create one first using POST /profile"
        )
    
    # Update basic profile fields
    profile.name = profile_data.name
    profile.email = profile_data.email
    profile.phone = profile_data.phone
    profile.location = profile_data.location
    profile.bio = profile_data.bio
    profile.updated_at = datetime.utcnow()
    
    # Update education if provided
    if profile_data.education is not None:
        db.query(Education).filter(Education.profile_id == profile.id).delete()
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
    
    db.flush()  # Get new skill IDs
    
    # Update projects if provided
    if profile_data.projects is not None:
        db.query(Project).filter(Project.profile_id == profile.id).delete()
        for project in profile_data.projects:
            project_dict = project.model_dump()
            skill_ids = project_dict.pop('skill_ids', [])
            new_project = Project(profile_id=profile.id, **project_dict)
            
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


@app.delete("/profile", status_code=status.HTTP_204_NO_CONTENT, tags=["Profile"])
def delete_profile(
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """
    Delete the profile and all related data (requires authentication)
    
    WARNING: This cannot be undone!
    Protected endpoint - requires Basic Auth
    """
    profile = db.query(Profile).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(profile)
    db.commit()
    
    return None


# ===== Education Endpoints =====

@app.get("/education", response_model=List[EducationResponse], tags=["Education"])
def read_education(db: Session = Depends(get_db)):
    """Get all education records"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.education


@app.post("/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED, tags=["Education"])
def create_education(
    education_data: EducationCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Add new education record (requires authentication)"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    education = Education(profile_id=profile.id, **education_data.model_dump())
    db.add(education)
    db.commit()
    db.refresh(education)
    
    return education


@app.put("/education/{education_id}", response_model=EducationResponse, tags=["Education"])
def update_education(
    education_id: int,
    education_data: EducationUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Update education record (requires authentication)"""
    education = db.query(Education).filter(Education.id == education_id).first()
    if not education:
        raise HTTPException(status_code=404, detail="Education record not found")
    
    for key, value in education_data.model_dump(exclude_unset=True).items():
        setattr(education, key, value)
    
    db.commit()
    db.refresh(education)
    
    return education


@app.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Education"])
def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Delete education record (requires authentication)"""
    education = db.query(Education).filter(Education.id == education_id).first()
    if not education:
        raise HTTPException(status_code=404, detail="Education record not found")
    
    db.delete(education)
    db.commit()
    
    return None


# ===== Work Experience Endpoints =====

@app.get("/work-experience", response_model=List[WorkExperienceResponse], tags=["Work Experience"])
def read_work_experience(db: Session = Depends(get_db)):
    """Get all work experience records"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.work_experience


@app.post("/work-experience", response_model=WorkExperienceResponse, status_code=status.HTTP_201_CREATED, tags=["Work Experience"])
def create_work_experience(
    work_data: WorkExperienceCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Add new work experience (requires authentication)"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    work = WorkExperience(profile_id=profile.id, **work_data.model_dump())
    db.add(work)
    db.commit()
    db.refresh(work)
    
    return work


@app.put("/work-experience/{work_id}", response_model=WorkExperienceResponse, tags=["Work Experience"])
def update_work_experience(
    work_id: int,
    work_data: WorkExperienceUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Update work experience (requires authentication)"""
    work = db.query(WorkExperience).filter(WorkExperience.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    for key, value in work_data.model_dump(exclude_unset=True).items():
        setattr(work, key, value)
    
    db.commit()
    db.refresh(work)
    
    return work


@app.delete("/work-experience/{work_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Work Experience"])
def delete_work_experience(
    work_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Delete work experience (requires authentication)"""
    work = db.query(WorkExperience).filter(WorkExperience.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    db.delete(work)
    db.commit()
    
    return None


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
    
    if skill:
        query = query.join(Project.skills).filter(
            func.lower(Skill.name) == skill.lower()
        )
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.all()
    return projects


@app.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
def read_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Add new project (requires authentication)"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    project_dict = project_data.model_dump()
    skill_ids = project_dict.pop('skill_ids', [])
    
    project = Project(profile_id=profile.id, **project_dict)
    
    if skill_ids:
        skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
        project.skills.extend(skills)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@app.put("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Update project (requires authentication)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_dict = project_data.model_dump(exclude_unset=True)
    skill_ids = project_dict.pop('skill_ids', None)
    
    for key, value in project_dict.items():
        setattr(project, key, value)
    
    if skill_ids is not None:
        project.skills.clear()
        if skill_ids:
            skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
            project.skills.extend(skills)
    
    db.commit()
    db.refresh(project)
    
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Delete project (requires authentication)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return None


# ===== Skills Endpoints =====

@app.get("/skills", response_model=List[SkillResponse], tags=["Skills"])
def read_skills(db: Session = Depends(get_db)):
    """Get all skills"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.skills


@app.get("/skills/top", response_model=List[SkillWithCount], tags=["Skills"])
def get_top_skills(
    limit: int = Query(10, ge=1, le=50, description="Number of top skills to return"),
    db: Session = Depends(get_db)
):
    """Get the most-used skills based on project count"""
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


@app.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED, tags=["Skills"])
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Add new skill (requires authentication)"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    skill = Skill(profile_id=profile.id, **skill_data.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    
    return skill


@app.put("/skills/{skill_id}", response_model=SkillResponse, tags=["Skills"])
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Update skill (requires authentication)"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    for key, value in skill_data.model_dump(exclude_unset=True).items():
        setattr(skill, key, value)
    
    db.commit()
    db.refresh(skill)
    
    return skill


@app.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Skills"])
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Delete skill (requires authentication)"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(skill)
    db.commit()
    
    return None


# ===== Social Links Endpoints =====

@app.get("/social-links", response_model=List[SocialLinkResponse], tags=["Social Links"])
def read_social_links(db: Session = Depends(get_db)):
    """Get all social links"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.social_links


@app.post("/social-links", response_model=SocialLinkResponse, status_code=status.HTTP_201_CREATED, tags=["Social Links"])
def create_social_link(
    link_data: SocialLinkCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Add new social link (requires authentication)"""
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    link = SocialLink(profile_id=profile.id, **link_data.model_dump())
    db.add(link)
    db.commit()
    db.refresh(link)
    
    return link


@app.put("/social-links/{link_id}", response_model=SocialLinkResponse, tags=["Social Links"])
def update_social_link(
    link_id: int,
    link_data: SocialLinkUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Update social link (requires authentication)"""
    link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Social link not found")
    
    for key, value in link_data.model_dump(exclude_unset=True).items():
        setattr(link, key, value)
    
    db.commit()
    db.refresh(link)
    
    return link


@app.delete("/social-links/{link_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Social Links"])
def delete_social_link(
    link_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials)
):
    """Delete social link (requires authentication)"""
    link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Social link not found")
    
    db.delete(link)
    db.commit()
    
    return None


# ===== Search Endpoint =====
@app.get("/search", response_model=List[SearchResult], tags=["Search"])
def search_content(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """Global search across projects and work experience"""
    search_term = f"%{q.lower()}%"
    results = []
    
    projects = db.query(Project).filter(
        or_(
            func.lower(Project.name).like(search_term),
            func.lower(Project.description).like(search_term)
        )
    ).all()
    
    for project in projects:
        score = 1.0
        if project.name and q.lower() in project.name.lower():
            score += 0.5
        
        results.append(SearchResult(
            type="project",
            id=project.id,
            title=project.name,
            description=project.description,
            relevance_score=score
        ))
    
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
    
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return results


# ===== Root Endpoint =====
@app.get("/", tags=["System"])
def root():
    """API root endpoint with basic information and links"""
    return {
        "name": "Me-API Playground",
        "version": "1.0.0",
        "description": "A live, queryable resume/portfolio API with full CRUD operations",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "profile": {
                "read": "GET /profile",
                "create": "POST /profile (auth required)",
                "update": "PUT /profile (auth required)",
                "delete": "DELETE /profile (auth required)"
            },
            "education": {
                "list": "GET /education",
                "create": "POST /education (auth required)",
                "update": "PUT /education/{id} (auth required)",
                "delete": "DELETE /education/{id} (auth required)"
            },
            "work_experience": {
                "list": "GET /work-experience",
                "create": "POST /work-experience (auth required)",
                "update": "PUT /work-experience/{id} (auth required)",
                "delete": "DELETE /work-experience/{id} (auth required)"
            },
            "projects": {
                "list": "GET /projects",
                "read": "GET /projects/{id}",
                "create": "POST /projects (auth required)",
                "update": "PUT /projects/{id} (auth required)",
                "delete": "DELETE /projects/{id} (auth required)"
            },
            "skills": {
                "list": "GET /skills",
                "top": "GET /skills/top",
                "create": "POST /skills (auth required)",
                "update": "PUT /skills/{id} (auth required)",
                "delete": "DELETE /skills/{id} (auth required)"
            },
            "social_links": {
                "list": "GET /social-links",
                "create": "POST /social-links (auth required)",
                "update": "PUT /social-links/{id} (auth required)",
                "delete": "DELETE /social-links/{id} (auth required)"
            },
            "search": "GET /search?q=query"
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