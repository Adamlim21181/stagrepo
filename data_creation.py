from app import create_app, models, db

from faker import Faker
import random

fake = Faker("en_NZ")

def add_users():
    roles = ["admin", "judge", None]
    codes = ["1234", "abcd", None]

    # zip() is used to match each role with its corresponding code
    for role, code in zip(roles, codes):
        user = models.Users(
            role = role,
            code = code
        )
        db.session.add(user)
    db.session.commit()

def add_seasons():
    for _ in range(5):
        season = models.Seasons(
            year = random.randint(2010, 2025)
        )
        db.session.add(season)
    db.session.commit()

def add_clubs():
    for _ in range(15):
        club = models.Clubs(
            name = fake.company()
        )
        db.session.add(club)
    db.session.commit()

def add_apparatus():
    apparatus = ["Floor", "Pommel Horse", "Still Rings", "Vault", "Parallel Bars", "Horizontal Bar"]
    for app in apparatus:
        apparatus = models.Apparatus(
            name = app
        )
        db.session.add(apparatus)
    db.session.commit()

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

def add_entries():
    competitions = [competition.id for competition in models.Competitions.query.all()]
    gymnasts = [gymnast.id for gymnast in models.Gymnasts.query.all()]
    
    entries = 0
    
    # prevent duplicate gymnasts in the same competition
    while entries <= 1000:
        competition_id = random.choice(competitions)
        gymnast_id = random.choice(gymnasts)
    
        # first() gets the first row that matches the filter, or None is returned if no match is found
        if not models.Entries.query.filter_by(competition_id=competition_id, gymnast_id=gymnast_id).first():
            entry = models.Entries()(
                competition_id = competition_id,
                gymnast_id = gymnast_id
            )
            db.session.add(entry)
            entries += 1
    
    db.session.commit()

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
                entry_id = entry_id,
                apparatus_id = app.id,
                e_score = e_score,
                d_score = d_score,
                penalty = penalty,
                total = total
            )   
            db.session.add(score)
    db.session.commit()
        
def create_random_data():
    add_users()
    add_seasons()
    add_clubs()
    add_apparatus()
    add_competitions()
    add_gymnasts()
    add_entries()
    add_scores()
