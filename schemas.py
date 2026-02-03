"""
Pydantic Schemas for Request/Response Validation
Type-safe data models for API endpoints
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


# ===== Education Schemas =====
class EducationBase(BaseModel):
    institution: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., min_length=1, max_length=255)
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    description: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# ===== Work Experience Schemas =====
class WorkExperienceBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    position: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    location: Optional[str] = None


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceResponse(WorkExperienceBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# ===== Skill Schemas =====
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced|expert)$")
    category: Optional[str] = None
    years_experience: Optional[float] = Field(None, ge=0)


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class SkillWithCount(SkillResponse):
    """Skill with project count for top skills endpoint"""
    project_count: int = 0


# ===== Project Schemas =====
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(completed|in-progress|archived)$")


class ProjectCreate(ProjectBase):
    skill_ids: List[int] = []  # List of skill IDs to associate


class ProjectResponse(ProjectBase):
    id: int
    skills: List[SkillResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ===== Social Link Schemas =====
class SocialLinkBase(BaseModel):
    platform: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    icon: Optional[str] = None


class SocialLinkCreate(SocialLinkBase):
    pass


class SocialLinkResponse(SocialLinkBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# ===== Profile Schemas =====
class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class ProfileCreate(ProfileBase):
    education: List[EducationCreate] = []
    work_experience: List[WorkExperienceCreate] = []
    projects: List[ProjectCreate] = []
    skills: List[SkillCreate] = []
    social_links: List[SocialLinkCreate] = []


class ProfileUpdate(ProfileBase):
    education: Optional[List[EducationCreate]] = None
    work_experience: Optional[List[WorkExperienceCreate]] = None
    projects: Optional[List[ProjectCreate]] = None
    skills: Optional[List[SkillCreate]] = None
    social_links: Optional[List[SocialLinkCreate]] = None


class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    education: List[EducationResponse] = []
    work_experience: List[WorkExperienceResponse] = []
    projects: List[ProjectResponse] = []
    skills: List[SkillResponse] = []
    social_links: List[SocialLinkResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ===== Search Result Schema =====
class SearchResult(BaseModel):
    type: str  # "project" or "work_experience"
    id: int
    title: str
    description: Optional[str]
    relevance_score: float = 1.0
    
    model_config = ConfigDict(from_attributes=True)


# ===== Health Check Schema =====
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    version: str = "1.0.0"
