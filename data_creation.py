"""Database seeding and test data creation functions."""

from create_app import db
import models

from faker import Faker
import random

fake = Faker("en_NZ")


def add_roles():
    """Add default user roles (admin, judges)"""
    role_names = ["admin", "judges"]
    for name in role_names:
        if not models.Roles.query.filter_by(name=name).first():
            role = models.Roles(
                name=name
            )
            db.session.add(role)
    db.session.commit()
    print("Roles added successfully.")


def add_users():
    """Add default users with preset credentials"""
    # initial users needed for system access
    roles = {
        "admin": "admin",
        "judges": "judges"
    }

    codes = {
        "admin": "admin123",
        "judges": "judge123"
    }

    for username, role_name in roles.items():
        if not models.Users.query.filter_by(username=username).first():
            role = models.Roles.query.filter_by(name=role_name).first()
            if not role:
                print(f"Warning: Role '{role_name}' not found!")
                continue

            user = models.Users(
                username=username,
                code=codes[username],
                role_id=role.id
            )

            db.session.add(user)
    db.session.commit()
    print("Users added successfully.")


def add_seasons():
    """Add random competition seasons"""
    for _ in range(5):
        year = random.randint(2010, 2025)
        if not models.Seasons.query.filter_by(year=year).first():
            season = models.Seasons(
                year=year
            )
            db.session.add(season)
    db.session.commit()
    print("Seasons added successfully.")


def add_clubs():
    """Add sample gymnastics clubs"""
    for _ in range(15):
        name = fake.company()
        if not models.Clubs.query.filter_by(name=name).first():
            club = models.Clubs(
                name=name
            )
            db.session.add(club)
    db.session.commit()
    print("Clubs added successfully.")


def add_apparatus():
    """Add gymnastics apparatus (floor, vault, bars, etc.)"""
    apparatus = ["Floor", "Pommel Horse", "Still Rings", "Vault",
                 "Parallel Bars", "Horizontal Bar"]
    for name in apparatus:
        apparatus = models.Apparatus(
            name=name
        )
        db.session.add(apparatus)
    db.session.commit()
    print("Apparatus added successfully.")


def add_competitions():
    """Add sample competitions with dates and locations"""
    from datetime import datetime, timedelta

    base_date = datetime(2025, 7, 23).date()

    for _ in range(20):
        street_address = fake.street_address()
        city = fake.city()
        address = f"{street_address}, {city}"

        # Generate dates within 6 months before and after current date
        days_offset = random.randint(-180, 180)
        competition_date = base_date + timedelta(days=days_offset)

        # Find the correct season based on the competition year
        competition_year = competition_date.year
        season = models.Seasons.query.filter_by(year=competition_year).first()

        # If no season exists for that year, create one
        if not season:
            season = models.Seasons(year=competition_year)
            db.session.add(season)
            db.session.flush()

        competition = models.Competitions(
            season_id=season.id,
            name=fake.color_name(),
            address=address,
            competition_date=competition_date
        )
        db.session.add(competition)
    db.session.commit()
    print("Competitions added successfully.")


def add_gymnasts():
    """Add sample gymnasts with random clubs and levels"""
    clubs = [club.id for club in models.Clubs.query.all()]
    levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5",
              "Level 6", "Level 7", "Level 8", "Level 9",
              "Junior International", "Senior International"]

    for _ in range(55):
        gymnast = models.Gymnasts(
            club_id=random.choice(clubs),
            name=fake.name(),
            level=random.choice(levels)
        )
        db.session.add(gymnast)
    db.session.commit()
    print("Gymnasts added successfully.")


def add_entries():
    """Add competition entries (gymnast-competition links)"""
    competitions = [competition.id
                    for competition in models.Competitions.query.all()]

    gymnasts = [gymnast.id for gymnast in models.Gymnasts.query.all()]

    entries = 0

    # While loop prevents duplicate entries
    while entries < 1100:
        competition_id = random.choice(competitions)
        gymnast_id = random.choice(gymnasts)

        existing_entry = models.Entries.query.filter_by(
            competition_id=competition_id, gymnast_id=gymnast_id
        ).first()

        if not existing_entry:
            entry = models.Entries(
                competition_id=competition_id,
                gymnast_id=gymnast_id
            )
            db.session.add(entry)
            entries += 1

    db.session.commit()
    print("Entries added successfully.")


def add_scores():
    """Add performance scores for all entries and apparatus"""
    entries = [entry.id for entry in models.Entries.query.all()]
    apparatus = models.Apparatus.query.all()

    for entry_id in entries:
        for app in apparatus:
            e_score = round(fake.random.uniform(0.00, 10.00), 2)
            d_score = round(fake.random.uniform(0.00, 10.00), 2)
            penalty = round(fake.random.uniform(0.00, 2.00), 2)
            total = round(e_score + d_score - penalty, 2)

            score = models.Scores(
                entry_id=entry_id,
                apparatus_id=app.id,
                e_score=e_score,
                d_score=d_score,
                penalty=penalty,
                total=total
            )
            db.session.add(score)
    db.session.commit()
    print("Scores added successfully.")


def create_judge_scores_table():
    """Create judge_scores table for multiple judge scoring"""
    db.create_all()
    print("✅ judge_scores table created successfully!")


def add_sample_judge_scores():
    """Add sample judge scores for testing multi-judge system"""
    # Get some existing scores to add judge scores for
    scores = models.Scores.query.limit(10).all()

    for score in scores:
        # Add 2-3 judge scores per apparatus
        num_judges = random.randint(2, 3)

        judge_e_scores = []
        for judge_num in range(1, num_judges + 1):
            variation = random.uniform(-0.5, 0.5)
            judge_e_score = max(0, min(10, score.e_score + variation))

            judge_score = models.JudgeScores(
                score_id=score.id,
                judge_number=judge_num,
                e_score=round(judge_e_score, 3)
            )
            db.session.add(judge_score)
            judge_e_scores.append(judge_e_score)

        # Update score with average of all judge scores
        if judge_e_scores:
            avg_e_score = sum(judge_e_scores) / len(judge_e_scores)
            score.e_score = round(avg_e_score, 3)
            score.total = score.e_score + score.d_score - score.penalty

    db.session.commit()
    print(f"Sample judge scores added for {len(scores)} routines.")


def clear_all_data():
    """Clear all data and reset auto-increment counters"""
    print("Clearing all existing data...")

    # Delete in reverse order of dependencies
    db.session.execute('DELETE FROM judge_scores')
    db.session.execute('DELETE FROM scores')
    db.session.execute('DELETE FROM entries')
    db.session.execute('DELETE FROM gymnasts')
    db.session.execute('DELETE FROM competitions')
    db.session.execute('DELETE FROM apparatus')
    db.session.execute('DELETE FROM clubs')
    db.session.execute('DELETE FROM seasons')
    db.session.execute('DELETE FROM users')
    db.session.execute('DELETE FROM roles')

    # Reset auto-increment counters for SQLite
    table_names = '"roles", "users", "seasons", "clubs", "apparatus"'
    table_names += ', "competitions", "gymnasts", "entries", "scores"'
    table_names += ', "judge_scores"'

    db.session.execute(
        f'UPDATE sqlite_sequence SET seq = 0 WHERE name IN ({table_names})'
    )

    db.session.commit()
    print("All data cleared and auto-increment counters reset.")


def create_random_data():
    """Create all test data in correct order"""
    db.create_all()
    add_roles()
    add_users()
    add_seasons()
    add_clubs()
    add_apparatus()
    add_competitions()
    add_gymnasts()
    add_entries()
    add_scores()
    add_sample_judge_scores()  # Add judge scores after regular scores
    print("All data created successfully including judge scores!")


def recreate_all_data():
    """Clear all data and recreate fresh test data"""
    clear_all_data()
    create_random_data()
    print("Database completely recreated with fresh data!")
