"""
seed_mock_data.py — Sprint 2 Mock Data Seeder.
AI/ML Engineer: Mayank Kumar.

Seeds rich faculty profiles, education, experience, and achievement records
so the system is immediately ready for data analysis, portfolio viewing,
and subsequent ML completeness scoring (Sprint 3 / Sprint 4).
"""

import datetime
import uuid
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.department import Department
from app.models.faculty_profile import FacultyProfile
from app.models.education import Education
from app.models.experience import Experience
from app.models.achievement import Achievement


def seed_mock_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("🌱 Seeding Sprint 2 mock data...")

        # 1. Ensure Department exists
        dept = db.query(Department).filter(Department.code == "CSE-DS").first()
        if not dept:
            dept = Department(
                id=str(uuid.uuid4()),
                name="Computer Science & Engineering (Data Science)",
                code="CSE-DS",
            )
            db.add(dept)
            db.commit()
            db.refresh(dept)
            print(f"  ✓ Department created: {dept.name}")

        # 2. Ensure Faculty User exists
        faculty_email = "dr.mayank@skit.ac.in"
        user = db.query(User).filter(User.email == faculty_email).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email=faculty_email,
                hashed_password=get_password_hash("FacultyPass123!"),
                is_active=True,
                role="faculty",
                department_id=dept.id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  ✓ Faculty user created: {user.email}")

        # 3. Ensure Faculty Profile exists
        profile = (
            db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
        )
        if not profile:
            profile = FacultyProfile(
                id=str(uuid.uuid4()),
                user_id=user.id,
                first_name="Dr. Mayank",
                last_name="Kumar",
                designation="Associate Professor",
                department=dept.name,
                bio=(
                    "Associate Professor of Computer Science specializing in AI/ML, NLP, "
                    "and Data Analytics. Leading machine learning research on educational "
                    "analytics and dynamic faculty portfolio architectures."
                ),
                skills="Python, PyTorch, TensorFlow, Scikit-learn, Pandas, NLP, FastAPI, PostgreSQL",
                profile_image_url="/placeholder-user.jpg",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            print(
                f"  ✓ Faculty profile created for {profile.first_name} {profile.last_name}"
            )

        # 4. Seed Education
        existing_edu = (
            db.query(Education).filter(Education.faculty_id == profile.id).count()
        )
        if existing_edu == 0:
            edu_records = [
                Education(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    degree="Ph.D. in Computer Science & Engineering",
                    institution="Indian Institute of Technology (IIT) Delhi",
                    field_of_study="Artificial Intelligence & Machine Learning",
                    start_date=datetime.date(2017, 8, 1),
                    end_date=datetime.date(2021, 5, 20),
                    grade="9.8 CGPA",
                ),
                Education(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    degree="M.Tech in Data Science",
                    institution="National Institute of Technology (NIT) Kurukshetra",
                    field_of_study="Data Science & Engineering",
                    start_date=datetime.date(2015, 8, 1),
                    end_date=datetime.date(2017, 6, 15),
                    grade="9.5 CGPA",
                ),
                Education(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    degree="B.Tech in Computer Science & Engineering",
                    institution="Rajasthan Technical University",
                    field_of_study="Computer Science",
                    start_date=datetime.date(2011, 8, 1),
                    end_date=datetime.date(2015, 6, 1),
                    grade="8.9 CGPA",
                ),
            ]
            db.add_all(edu_records)
            db.commit()
            print(f"  ✓ Seeded {len(edu_records)} education records")

        # 5. Seed Experience
        existing_exp = (
            db.query(Experience).filter(Experience.faculty_id == profile.id).count()
        )
        if existing_exp == 0:
            exp_records = [
                Experience(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    job_title="Associate Professor",
                    organization="Swami Keshvanand Institute of Technology (SKIT)",
                    start_date=datetime.date(2021, 7, 1),
                    end_date=None,
                    is_current=True,
                    description="Teaching Machine Learning, Deep Learning, and guiding M.Tech/B.Tech research scholars.",
                    employment_type="Full-time",
                ),
                Experience(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    job_title="Postdoctoral Research Fellow",
                    organization="AI Research Laboratory, IIT Delhi",
                    start_date=datetime.date(2020, 6, 1),
                    end_date=datetime.date(2021, 6, 30),
                    is_current=False,
                    description="Conducted research on Transformer attention mechanisms and natural language understanding.",
                    employment_type="Full-time",
                ),
            ]
            db.add_all(exp_records)
            db.commit()
            print(f"  ✓ Seeded {len(exp_records)} experience records")

        # 6. Seed Achievements
        existing_ach = (
            db.query(Achievement).filter(Achievement.faculty_id == profile.id).count()
        )
        if existing_ach == 0:
            ach_records = [
                Achievement(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    title="Best Research Paper Award",
                    category="Award",
                    achievement_date=datetime.date(2023, 11, 15),
                    description="Awarded for paper on 'Efficient Attention Optimization for Domain-Specific LLMs' at IEEE ICMLA.",
                ),
                Achievement(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    title="Senior Member of ACM",
                    category="Membership",
                    achievement_date=datetime.date(2022, 9, 1),
                    description="Conferred Senior Membership for contributions to computer science education and research.",
                ),
                Achievement(
                    id=str(uuid.uuid4()),
                    faculty_id=profile.id,
                    title="State Faculty Excellence Award",
                    category="Recognition",
                    achievement_date=datetime.date(2024, 3, 22),
                    description="Recognized by the Department of Higher Education for pedagogical innovation in Data Science.",
                ),
            ]
            db.add_all(ach_records)
            db.commit()
            print(f"  ✓ Seeded {len(ach_records)} achievement records")

        print("✨ Sprint 2 mock data seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_mock_data()
