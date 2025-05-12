from create_app import db
import models

from faker import Faker
import random

fake = Faker("en_NZ")

def add_roles():
    role_names = ["admin", "judges", "public"]
    for name in role_names:
        if not models.Roles.query.filter_by(name=name).first():
            role = models.Roles(
                name = name
            )
            db.session.add(role)
    db.session.commit()
    print("Roles added successfully.")
    
def add_users():
    roles = {
        "admin": "admin",
        "judges": "judges",
        "public": None
    }
    for username, role_name in roles.items():
        if not models.Users.query.filter_by(username=username).first():
            user = models.Users(
                username=username
            )
            
            if role_name:
                role = models.Roles.query.filter_by(name=role_name).first()
                if role:
                    user.roles.append(role)
                    
            db.session.add(user)
    db.session.commit()
    print("Users added successfully.")
    
def add_seasons():
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
    name = fake.company()
    for _ in range(15):
        if not models.Clubs.query.filter_by(name=name).first():
            club = models.Clubs(
                name=name
            )
            db.session.add(club)
    db.session.commit()
    print("Clubs added successfully.")

def add_apparatus():
    apparatus = ["Floor", "Pommel Horse", "Still Rings", "Vault", "Parallel Bars", "Horizontal Bar"]
    for name in apparatus:
        apparatus = models.Apparatus(
            name = name
        )
        db.session.add(apparatus)
    db.session.commit()
    print("Apparatus added successfully.")

def add_competitions():
    seasons = [season.id for season in models.Seasons.query.all()]

    for _ in range(20):
        competition = models.Competitions(
            season_id = random.choice(seasons),
            name = fake.color_name(),
            address = fake.address()
        )
        db.session.add(competition)
    db.session.commit()
    print("Competitions added successfully.")

def add_gymnasts():
    clubs = [club.id for club in models.Clubs.query.all()]
    levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Junior International", "Senior International"]

    for _ in range(55):
        gymnast = models.Gymnasts(
            club_id = random.choice(clubs),
            name = fake.name(),
            level = random.choice(levels)
        )
        db.session.add(gymnast)
    db.session.commit()
    print("Gymnasts added successfully.")

def add_entries():
    competitions = [competition.id for competition in models.Competitions.query.all()]
    gymnasts = [gymnast.id for gymnast in models.Gymnasts.query.all()]

    entries = 0

    # prevent duplicate gymnasts in the same competition
    while entries <= 1000:
        competition_id = random.choice(competitions)
        gymnast_id = random.choice(gymnasts)

        existing_entry = models.Entries.query.filter_by(competition_id=competition_id, gymnast_id=gymnast_id).first()
        # first() gets the first row that matches the filter, or None is returned if no match is found
        if not existing_entry:
            entry = models.Entries(
                competition_id = competition_id,
                gymnast_id = gymnast_id
            )
            db.session.add(entry)
            entries += 1

    db.session.commit()
    print("Entries added successfully.")

def add_scores():
    entries = [entry.id for entry in models.Entries.query.all()]
    apparatus = models.Apparatus.query.all()

    for entry_id in entries:
        for app in apparatus:
            e_score = round(fake.random.uniform(0.00,10.00), 2)
            d_score = round(fake.random.uniform(0.00,10.00), 2)
            penalty = round(fake.random.uniform(0.00,2.00), 2)
            total = round(e_score + d_score - penalty, 2)

            score = models.Scores(
                entries_id = entry_id,
                apparatus_id = app.id,
                e_score = e_score,
                d_score = d_score,
                penalty = penalty,
                total = total
            )
            db.session.add(score)
    db.session.commit()
    print("Scores added successfully.")

def create_random_data():
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
    print("Random data created successfully.")
