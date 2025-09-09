"""
Scoring routes.
Handles live competition scoring functionality for judges.
"""
from flask import render_template, redirect, url_for, session, flash, request
from extensions import db
import models
import forms
from . import main


@main.route('/scoring', methods=['GET', 'POST'])
def scoring():
    """Handle live competition scoring interface for judges."""
    if 'user_id' not in session:
        return render_template('nologin.html')

    # Get the live competition
    live_competition = models.Competitions.query.filter_by(
        status='live'
        ).first()

    if not live_competition:
        flash('No live competition is currently running. '
              'Please contact an admin.', 'warning')
        return render_template('scoring.html', no_live_competition=True)

    # Get all entries for the live competition (gymnasts who are competing)
    entries = db.session.query(models.Entries, models.Gymnasts, models.Clubs)\
        .join(models.Gymnasts,
              models.Entries.gymnast_id == models.Gymnasts.id)\
        .join(models.Clubs,
              models.Gymnasts.club_id == models.Clubs.id)\
        .filter(models.Entries.competition_id == live_competition.id)\
        .all()

    # Get all apparatus
    apparatus_list = models.Apparatus.query.all()

    # Calculate scoring progress for each gymnast
    scoring_progress = {}
    total_gymnasts = len(entries)
    fully_scored_gymnasts = 0

    for entry, gymnast, club in entries:
        scored_apparatus = set()
        for score in entry.scores:
            scored_apparatus.add(score.apparatus_id)

        total_apparatus = len(apparatus_list)
        scored_count = len(scored_apparatus)
        is_complete = scored_count == total_apparatus

        if is_complete:
            fully_scored_gymnasts += 1

        scoring_progress[entry.id] = {
            'scored_count': scored_count,
            'total_count': total_apparatus,
            'is_complete': is_complete,
            'percentage': (
                (scored_count / total_apparatus * 100)
                if total_apparatus > 0 else 0
            )
        }

    # Overall competition progress
    overall_progress = {
        'total_gymnasts': total_gymnasts,
        'fully_scored': fully_scored_gymnasts,
        'percentage': (
            (fully_scored_gymnasts / total_gymnasts * 100)
            if total_gymnasts > 0 else 0
        ),
        'is_complete': fully_scored_gymnasts == total_gymnasts
    }

    # Create form for scoring with proper WTF integration
    form = forms.AddScores()
    
    # Populate form choices dynamically
    form.entry_id.choices = [(0, 'Select a gymnast...')] + [
        (entry.id, f"{gymnast.name} - {club.name} ({gymnast.level})")
        for entry, gymnast, club in entries
    ]
    form.apparatus_id.choices = [(0, 'Select apparatus...')] + [
        (app.id, app.name) for app in apparatus_list
    ]

    # Handle form submission with existing multi-judge system
    if request.method == 'POST':
        entry_id = request.form.get('entry_id')
        apparatus_id = request.form.get('apparatus_id')
        d_score = request.form.get('d_score')
        penalty = request.form.get('penalty', 0)

        # Get execution scores (can be multiple)
        execution_scores = request.form.getlist('execution_scores')

        try:
            # Convert to floats and filter out empty values
            execution_scores = [
                float(score) for score in execution_scores
                if score and score.strip()
            ]

            if not execution_scores:
                flash('Please enter at least one execution score.', 'warning')
                return redirect(url_for('main.scoring'))

            d_score = float(d_score) if d_score else 0.0
            penalty = float(penalty) if penalty else 0.0

            # Find existing score or create new one
            existing_score = models.Scores.query.filter_by(
                entry_id=entry_id,
                apparatus_id=apparatus_id
            ).first()

            if existing_score:
                # Clear existing judge scores
                models.JudgeScores.query.filter_by(
                    score_id=existing_score.id
                ).delete()
            else:
                # Create new score record
                existing_score = models.Scores(
                    entry_id=entry_id,
                    apparatus_id=apparatus_id,
                    e_score=0.0,
                    d_score=d_score,
                    penalty=penalty,
                    total=0.0
                )
                db.session.add(existing_score)
                db.session.flush()  # Get the ID

            # Update D-score and penalty
            existing_score.d_score = d_score
            existing_score.penalty = penalty

            if len(execution_scores) == 1:
                # Single judge scoring
                existing_score.e_score = execution_scores[0]
                existing_score.total = (existing_score.e_score +
                                        existing_score.d_score -
                                        existing_score.penalty)
                flash(f'Score submitted! Total: {existing_score.total:.3f}',
                      'success')
            else:
                # Multiple judge scoring - save individual scores and average
                for judge_num, e_score in enumerate(execution_scores, 1):
                    judge_score = models.JudgeScores(
                        score_id=existing_score.id,
                        judge_number=judge_num,
                        e_score=round(e_score, 3)
                    )
                    db.session.add(judge_score)

                # Calculate and update averaged E-score
                existing_score.update_final_score()
                flash(
                    f'Multi-judge score submitted! Average E-score: '
                    f'{existing_score.e_score:.3f}, Total: '
                    f'{existing_score.total:.3f}',
                    'success'
                )

        except ValueError as e:
            flash(f'Invalid score values: {str(e)}', 'danger')
            return redirect(url_for('main.scoring'))

        db.session.commit()

        # Check if this completed scoring for a gymnast
        updated_entry = models.Entries.query.get(entry_id)
        if updated_entry:
            scored_apparatus_count = len(updated_entry.scores)
            if scored_apparatus_count == len(apparatus_list):
                gymnast_name = updated_entry.gymnasts.name
                flash(f'✅ {gymnast_name} scoring complete!', 'info')

        return redirect(url_for('main.scoring'))

    return render_template(
        'scoring.html',
        entries=entries,
        apparatus_list=apparatus_list,
        live_competition=live_competition,
        scoring_progress=scoring_progress,
        overall_progress=overall_progress,
        form=form
    )
