from flask import render_template, redirect, url_for, session, flash, request
from extensions import db
import models
from . import main


@main.route('/gymnast/<int:gymnast_id>')
def gymnast_profile(gymnast_id):
    # Get the specific gymnast or return 404 if not found
    gymnast = models.Gymnasts.query.get_or_404(gymnast_id)

    # TODO: Add queries for:
    # - Best scores per apparatus
    # - Competition history
    # - Recent results

    apparatus_list = models.Apparatus.query.all()
    apparatus_data = {}
    all_around_data = []

    if gymnast.id:

        best_per_app = (
            db.session.query(
                models.Gymnasts.id,
                models.Scores.apparatus_id,
                db.func.max(models.Scores.total).label('best_score')
            )
            .join(
                models.Entries,
                models.Entries.gymnast_id == models.Gymnasts.id
                )
            .join(
                models.Scores,
                models.Scores.entry_id == models.Entries.id
                )
            .filter(models.Gymnasts.id == gymnast.id)
            .subquery()
        )

        all_around_data = (
            db.session.query(
                models.Gymnasts.id,
                models.Gymnasts.name,
                models.Clubs.name.label('club_name'),
                db.func.sum(best_per_app.c.best_score).label('total_score')
            )
            .join(best_per_app, best_per_app.c.id == models.Gymnasts.id)
            .join(models.Clubs, models.Clubs.id == models.Gymnasts.club_id)
            .group_by(
                models.Gymnasts.id,
                models.Gymnasts.name,
                models.Clubs.name
            )
            .order_by(db.func.sum(best_per_app.c.best_score).desc())
            .limit(24)
            .all()
        )

        for apparatus in apparatus_list:
            apparatus_data[apparatus.name] = (
                db.session.query(
                    models.Gymnasts.id,
                    models.Gymnasts.name,
                    models.Clubs.name.label('club_name'),
                    db.func.max(models.Scores.e_score).label('e_score'),
                    db.func.max(models.Scores.d_score).label('d_score'),
                    db.func.max(models.Scores.penalty).label('penalty'),
                    db.func.max(models.Scores.total).label('total')
                )
                .join(models.Entries,
                      models.Entries.gymnast_id == models.Gymnasts.id
                      )
                .join(models.Scores,
                      models.Scores.entry_id == models.Entries.id
                      )
                .join(models.Clubs, models.Clubs.id == models.Gymnasts.club_id)
                .filter(models.Gymnasts.id == gymnast.id)
                .group_by(models.Gymnasts.id,
                          models.Gymnasts.name,
                          models.Clubs.name
                          )
                .order_by(db.func.max(models.Scores.total).desc())
                .limit(8)
                .all()
            )

    return render_template('profiles.html',
                           gymnast=gymnast,
                           apparatus_data=apparatus_data,
                           all_around_data=all_around_data,
                           )
