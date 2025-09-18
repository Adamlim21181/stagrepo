from flask import render_template, request
from extensions import db
import models
from . import main


@main.route('/live')
def live():
    selected_level = request.args.get('level')
    selected_apparatus_id = request.args.get('apparatus')

    # Check if there's a live competition
    live_competition = models.Competitions.query.filter_by(
        status='live'
        ).first()

    if not live_competition:
        return render_template('live.html', no_live_competition=True)

    # Fetch all distinct levels from the live competition
    levels = db.session.query(
        models.Gymnasts.level
    ).join(models.Entries).filter(
        models.Entries.competition_id == live_competition.id
    ).distinct().order_by(models.Gymnasts.level).all()
    levels = [lvl[0] for lvl in levels]

    desired_order = [
        'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5',
        'Level 6', 'Level 7', 'Level 8', 'Level 9',
        'Junior International', 'Senior International'
    ]

    # Sort levels to match the desired order
    levels = sorted(levels, key=lambda x: desired_order.index(x)
                    if x in desired_order else 100)

    apparatus_list = models.Apparatus.query.all()

    leaderboard_data = []

    if selected_level:
        if selected_apparatus_id and selected_apparatus_id != 'all_around':

            leaderboard_data = (
                db.session.query(models.Scores, models.Gymnasts, models.Clubs)
                .join(models.Entries,
                      models.Scores.entry_id == models.Entries.id)
                .join(models.Gymnasts,
                      models.Entries.gymnast_id == models.Gymnasts.id
                      )
                .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
                .filter(models.Entries.competition_id == live_competition.id)
                .filter(models.Gymnasts.level == selected_level)
                .filter(models.Scores.apparatus_id == selected_apparatus_id)
                .order_by(models.Scores.total.desc())
                .all()
            )
        else:
            # Show all-around scores (total of all apparatus)
            # or when no apparatus selected
            # Get all gymnasts for the selected level with their
            # total scores across all apparatus
            leaderboard_data = (
                db.session.query(
                    models.Gymnasts.id,
                    models.Gymnasts.name,
                    models.Gymnasts.level,
                    models.Clubs.name.label('club_name'),
                    db.func.sum(models.Scores.e_score).label('total_e_score'),
                    db.func.sum(models.Scores.d_score).label('total_d_score'),
                    db.func.sum(models.Scores.penalty).label('total_penalty'),
                    db.func.sum(models.Scores.total).label('total_score')
                )
                .join(models.Entries,
                      models.Entries.gymnast_id == models.Gymnasts.id)
                .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
                .join(models.Scores,
                      models.Scores.entry_id == models.Entries.id)
                .filter(models.Entries.competition_id == live_competition.id)
                .filter(models.Gymnasts.level == selected_level)
                .group_by(
                    models.Gymnasts.id,
                    models.Gymnasts.name,
                    models.Gymnasts.level,
                    models.Clubs.name
                )
                .order_by(db.func.sum(models.Scores.total).desc())
                .all()
            )

    return render_template(
            'live.html',
            levels=levels,
            selected_level=selected_level,
            apparatus_list=apparatus_list,
            selected_apparatus_id=selected_apparatus_id,
            leaderboard_data=leaderboard_data,
            live_competition=live_competition
        )
