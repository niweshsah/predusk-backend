"""
Database Models for Me-API Playground
Defines all SQLAlchemy models with relationships
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Junction table for many-to-many relationship between projects and skills
project_skills = Table(
    'project_skills',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)


class Profile(Base):
    """Main profile model - single record expected"""
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))
    location = Column(String(255))
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    work_experience = relationship("WorkExperience", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    social_links = relationship("SocialLink", back_populates="profile", cascade="all, delete-orphan")


class Education(Base):
    """Education history"""
    __tablename__ = 'education'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field = Column(String(255))
    start_date = Column(String(50))  # e.g., "2015-09" or "September 2015"
    end_date = Column(String(50))    # e.g., "2019-05" or "May 2019" or "Present"
    gpa = Column(Float)
    description = Column(Text)
    
    # Relationships
    profile = relationship("Profile", back_populates="education")


class WorkExperience(Base):
    """Work experience history"""
    __tablename__ = 'work_experience'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(String(50))
    end_date = Column(String(50))
    is_current = Column(Boolean, default=False)
    location = Column(String(255))
    
    # Relationships
    profile = relationship("Profile", back_populates="work_experience")


class Project(Base):
    """Portfolio projects"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(500))
    github_url = Column(String(500))
    demo_url = Column(String(500))
    start_date = Column(String(50))
    end_date = Column(String(50))
    status = Column(String(50))  # e.g., "completed", "in-progress", "archived"
    
    # Relationships
    profile = relationship("Profile", back_populates="projects")
    skills = relationship("Skill", secondary=project_skills, back_populates="projects")


class Skill(Base):
    """Skills and technologies"""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(String(50))  # e.g., "beginner", "intermediate", "advanced", "expert"
    category = Column(String(100))  # e.g., "frontend", "backend", "database", "devops"
    years_experience = Column(Float)
    
    # Relationships
    profile = relationship("Profile", back_populates="skills")
    projects = relationship("Project", secondary=project_skills, back_populates="skills")


class SocialLink(Base):
    """Social media and professional links"""
    __tablename__ = 'social_links'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    platform = Column(String(100), nullable=False)  # e.g., "github", "linkedin", "twitter"
    url = Column(String(500), nullable=False)
    icon = Column(String(100))  # Optional icon class/name
    
    # Relationships
    profile = relationship("Profile", back_populates="social_links")
