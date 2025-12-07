"""Admin routes for competition management"""
from flask import redirect, url_for, flash
from extensions import db
import models
from . import main
from .login import admin_required


@main.route('/admin/competition/<int:competition_id>/start')
@admin_required
def start_competition(competition_id):
    """Start a competition and set it as live."""
    current_live = models.Competitions.query.filter_by(status='live').first()
    if current_live:
        current_live.status = 'ended'
        current_live.ended_at = db.func.now()

    competition = models.Competitions.query.get_or_404(competition_id)
    competition.status = 'live'
    competition.started_at = db.func.now()

    db.session.commit()
    flash(f'Competition "{competition.name}" is now live!', 'success')
    return redirect(url_for('main.competitions'))


@main.route('/admin/competition/<int:competition_id>/end')
@admin_required
def end_competition(competition_id):
    """End a live competition."""
    competition = models.Competitions.query.get_or_404(competition_id)
    competition.status = 'ended'
    competition.ended_at = db.func.now()

    db.session.commit()
    flash(f'Competition "{competition.name}" has ended.', 'success')
    return redirect(url_for('main.competitions'))


@main.route('/admin/competition/<int:competition_id>/delete', methods=['POST'])
@admin_required
def delete_competition(competition_id):
    """Delete a competition and all related data."""
    competition = models.Competitions.query.get_or_404(competition_id)
    competition_name = competition.name
    
    # Delete related entries first (due to foreign key constraints)
    entries = models.Entries.query.filter_by(
        competition_id=competition_id
    ).all()
    for entry in entries:
        db.session.delete(entry)
    
    # Delete related scores
    scores = models.Scores.query.filter_by(
        competition_id=competition_id
    ).all()
    for score in scores:
        db.session.delete(score)
    
    # Now delete the competition
    db.session.delete(competition)
    db.session.commit()
    
    flash(f'Competition "{competition_name}" and all related data have been '
          f'deleted.', 'success')
    return redirect(url_for('main.competitions'))


