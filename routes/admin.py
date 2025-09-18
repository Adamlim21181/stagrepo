from flask import redirect, url_for, session, flash
from extensions import db
import models
from . import main


@main.route('/admin/competition/<int:competition_id>/start')
def start_competition(competition_id):
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    # End any currently live competition
    current_live = models.Competitions.query.filter_by(status='live').first()
    if current_live:
        current_live.status = 'ended'
        current_live.ended_at = db.func.now()

    # Start the selected competition
    competition = models.Competitions.query.get_or_404(competition_id)
    competition.status = 'live'
    competition.started_at = db.func.now()

    db.session.commit()
    flash(f'Competition "{competition.name}" is now live!', 'success')
    return redirect(url_for('main.competitions'))


@main.route('/admin/competition/<int:competition_id>/end')
def end_competition(competition_id):
    """End a live competition."""
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    competition = models.Competitions.query.get_or_404(competition_id)
    competition.status = 'ended'
    competition.ended_at = db.func.now()

    db.session.commit()
    flash(f'Competition "{competition.name}" has ended.', 'success')
    return redirect(url_for('main.competitions'))


@main.route('/admin/competition/<int:competition_id>/delete', methods=['POST'])
def delete_competition(competition_id):
    """Delete a competition and all related data (cascade delete)."""
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    comp = models.Competitions.query.get_or_404(competition_id)

    # Don't allow deleting a live comp
    if getattr(comp, 'status', None) == 'live':
        flash("You can't delete a LIVE competition.", 'warning')
        return redirect(url_for('main.competitions'))

    """
    I have to delete the JudgesScores first, then from the Scores table,
    then from the entries table to avoid foreign key constraint issues.
    """

    judge_scores_to_delete = db.session.query(models.JudgeScores) \
        .join(models.Scores) \
        .join(models.Entries) \
        .filter(models.Entries.competition_id == comp.id) \
        .all()

    for judge_score in judge_scores_to_delete:
        db.session.delete(judge_score)

    scores_to_delete = db.session.query(models.Scores) \
        .join(models.Entries) \
        .filter(models.Entries.competition_id == comp.id) \
        .all()

    for score in scores_to_delete:
        db.session.delete(score)

    entries_to_delete = models.Entries.query.filter_by(
        competition_id=comp.id
    ).all()
    for entry in entries_to_delete:
        db.session.delete(entry)

    db.session.delete(comp)
    db.session.commit()

    flash('Competition and related data deleted successfully!', 'success')
    return redirect(url_for('main.competitions'))


@main.route('/admin/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    """Delete an entry and all related scores."""
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    entry = models.Entries.query.get_or_404(entry_id)

    """
    I have to delete the JudgesScores first, then from the Scores table
    because of foreign key constraints.
    """

    judge_scores_to_delete = db.session.query(models.JudgeScores) \
        .join(models.Scores) \
        .filter(models.Scores.entry_id == entry.id) \
        .all()

    for judge_score in judge_scores_to_delete:
        db.session.delete(judge_score)

    scores_to_delete = models.Scores.query.filter_by(
        entry_id=entry.id
    ).all()
    for score in scores_to_delete:
        db.session.delete(score)

    db.session.delete(entry)
    db.session.commit()

    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('main.entries'))


@main.route('/admin/gymnast/<int:gymnast_id>/delete', methods=['POST'])
def delete_gymnast(gymnast_id):
    """Delete a gymnast and all related data (cascade delete)."""
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    gymnast = models.Gymnasts.query.get_or_404(gymnast_id)

    """
    I have to delete the JudgesScores first, then from the Scores table,
    then from the entries table, then finally the gymnast because of
    foreign key constraints.
    """

    judge_scores_to_delete = db.session.query(models.JudgeScores) \
        .join(models.Scores) \
        .join(models.Entries) \
        .filter(models.Entries.gymnast_id == gymnast.id) \
        .all()

    for judge_score in judge_scores_to_delete:
        db.session.delete(judge_score)

    scores_to_delete = db.session.query(models.Scores) \
        .join(models.Entries) \
        .filter(models.Entries.gymnast_id == gymnast.id) \
        .all()

    for score in scores_to_delete:
        db.session.delete(score)

    entries_to_delete = models.Entries.query.filter_by(
        gymnast_id=gymnast.id
    ).all()
    for entry in entries_to_delete:
        db.session.delete(entry)

    db.session.delete(gymnast)
    db.session.commit()

    flash('Gymnast and related data deleted successfully!', 'success')
    return redirect(url_for('main.gymnasts'))


@main.route('/admin/score/<int:score_id>/delete', methods=['POST'])
def delete_score(score_id):
    """Delete a specific score and its judge scores."""
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    score = models.Scores.query.get_or_404(score_id)

    db.session.query(models.JudgeScores).filter_by(score_id=score.id).delete()

    db.session.delete(score)
    db.session.commit()

    flash('Score deleted successfully!', 'success')
    return redirect(url_for('main.scoring'))
