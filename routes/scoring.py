from flask import render_template, redirect, url_for, session, flash, request
from extensions import db
import models
import forms
from . import main


@main.route('/scoring', methods=['GET', 'POST'])
def scoring():

    if 'user_id' not in session:
        return render_template('nologin.html')
    
    # Check if user is judge or admin (role_id 1 or 2)
    if session.get('role_id') not in [1, 2]:
        flash('Access denied. Only judges and administrators can access '
              'score management.', 'error')
        return redirect(url_for('main.home'))

    live_competition = models.Competitions.query.filter_by(
        status='live'
        ).first()

    if not live_competition:
        flash('No live competition is currently running. '
              'Please contact an admin.', 'warning')
        return render_template('scoring.html', no_live_competition=True)

    entries = db.session.query(models.Entries, models.Gymnasts, models.Clubs)\
        .join(models.Gymnasts,
              models.Entries.gymnast_id == models.Gymnasts.id)\
        .join(models.Clubs,
              models.Gymnasts.club_id == models.Clubs.id)\
        .filter(models.Entries.competition_id == live_competition.id)\
        .all()

    apparatus_list = models.Apparatus.query.all()

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
            'is_complete': is_complete
        }

    overall_progress = {
        'total_gymnasts': total_gymnasts,
        'fully_scored': fully_scored_gymnasts,
        'percentage': (
            (fully_scored_gymnasts / total_gymnasts * 100)
            if total_gymnasts > 0 else 0
        ),
        'is_complete': fully_scored_gymnasts == total_gymnasts
    }

    form = forms.AddScores()

    form.entry_id.choices = [(0, 'Select a gymnast...')] + [
        (entry.id, f"{gymnast.name} - {club.name} ({gymnast.level})")
        for entry, gymnast, club in entries
    ]
    form.apparatus_id.choices = [(0, 'Select apparatus...')] + [
        (app.id, app.name) for app in apparatus_list
    ]

    if request.method == 'POST':
        if form.validate_on_submit():
            entry_id = form.entry_id.data
            apparatus_id = form.apparatus_id.data
            d_score = form.d_score.data
            penalty = form.penalty.data if form.penalty.data else 0.0

            # Handle execution scores (dynamic JavaScript input)
            execution_scores = request.form.getlist('execution_scores')

            try:
                # Convert to floats and filter out empty values
                execution_scores = [
                    float(score) for score in execution_scores
                    if score and score.strip()
                ]

                if not execution_scores:
                    flash(
                        'Please enter at least one execution score.',
                        'warning'
                    )
                    return redirect(url_for('main.scoring'))

                # Validate execution scores are in valid range
                for score in execution_scores:
                    if score < 0 or score > 10:
                        flash(
                            'Execution scores must be between 0 and 10.',
                            'danger'
                        )
                        return redirect(url_for('main.scoring'))

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
                    db.session.flush()

                existing_score.d_score = d_score
                existing_score.penalty = penalty

                if len(execution_scores) == 1:
                    # Single judge scoring
                    existing_score.e_score = execution_scores[0]
                    existing_score.total = (existing_score.e_score +
                                            existing_score.d_score -
                                            existing_score.penalty)
                    flash(
                        f'Score submitted! Total: {existing_score.total:.3f}',
                        'success'
                    )
                else:
                    # Multiple judge scoring - save individual scores
                    for judge_num, e_score in enumerate(execution_scores, 1):
                        judge_score = models.JudgeScores(
                            score_id=existing_score.id,
                            judge_number=judge_num,
                            e_score=round(e_score, 3)
                        )
                        db.session.add(judge_score)

                    existing_score.update_final_score()
                    flash(
                        f'Multi-judge score submitted! Average E-score: '
                        f'{existing_score.e_score:.3f}, Total: '
                        f'{existing_score.total:.3f}',
                        'success'
                    )

                db.session.commit()

                # Check if this completed scoring for a gymnast
                updated_entry = models.Entries.query.get(entry_id)
                if updated_entry:
                    scored_apparatus_count = len(updated_entry.scores)
                    if scored_apparatus_count == len(apparatus_list):
                        gymnast_name = updated_entry.gymnasts.name
                        flash(f'✅ {gymnast_name} scoring complete!', 'info')

                return redirect(url_for('main.scoring'))

            except ValueError as e:
                flash(f'Invalid score values: {str(e)}', 'danger')
                return redirect(url_for('main.scoring'))
        else:
            # Form validation failed - show specific error messages
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    flash(f"{field_name}: {error}", 'danger')

    return render_template(
        'scoring.html',
        entries=entries,
        apparatus_list=apparatus_list,
        live_competition=live_competition,
        scoring_progress=scoring_progress,
        overall_progress=overall_progress,
        form=form
    )


@main.route('/scoring/delete/<int:score_id>', methods=['POST'])
def delete_score(score_id):
    """Delete a score."""
    if 'user_id' not in session:
        return render_template('nologin.html')
    
    # Check if user is judge or admin (role_id 1 or 2)
    if session.get('role_id') not in [1, 2]:
        flash('Access denied. Only judges and administrators can delete '
              'scores.', 'error')
        return redirect(url_for('main.scoring'))

    score = models.Scores.query.get_or_404(score_id)
    
    # Store info for flash message
    gymnast_name = score.entries.gymnasts.name
    apparatus_name = score.apparatus.name
    
    # Delete the score
    db.session.delete(score)
    db.session.commit()
    
    flash(f'Score for {gymnast_name} on {apparatus_name} has been deleted.',
          'success')
    return redirect(url_for('main.scoring'))
