
from flask import render_template, request
from extensions import db
import models
import forms
from . import main


@main.route('/results')
def results():
    """Results page with search, sorting, and pagination functionality."""
    form = forms.ResultsSearchForm(request.args, meta={'csrf': False})
    search_query = form.search.data or ''

    # Choices for the pagination
    pagination_options = [
        (5, '5'), (10, '10'), (20, '20'), (50, '50'),
        (100, '100'), (1000, '1000'), (-1, 'All'),
    ]
    sort_options = [
        ('total', 'Total Score'),
        ('e_score', 'Execution Score'),
        ('d_score', 'Difficulty Score'),
        ('penalty', 'Penalty'),
        ('gymnast_name', 'Gymnast Name'),
        ('club_name', 'Club Name'),
        ('competition_name', 'Competition'),
        ('apparatus_name', 'Apparatus'),
        ('level', 'Level'),
        ('id', 'Gymnast ID'),
        ('entry_id', 'Entry ID'),
    ]
    form.per_page.choices = pagination_options
    form.sort_by.choices = sort_options

    # Read current controls (with defaults)
    per_page = form.per_page.data if form.per_page.data is not None else 5
    sort_by = form.sort_by.data or 'total'
    sort_order = form.sort_order.data or request.args.get('sort_order', 'desc')

    query = (
        models.Scores.query
        .join(models.Entries, models.Scores.entry_id == models.Entries.id)
        .join(models.Gymnasts, models.Entries.gymnast_id == models.Gymnasts.id)
        .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
        .join(
            models.Competitions,
            models.Entries.competition_id == models.Competitions.id
        )
        .join(
            models.Apparatus,
            models.Scores.apparatus_id == models.Apparatus.id
        )
        .options(
            db.joinedload(models.Scores.entry)
              .joinedload(models.Entries.gymnasts)
              .joinedload(models.Gymnasts.clubs),
            db.joinedload(models.Scores.entry)
              .joinedload(models.Entries.competitions),
            db.joinedload(models.Scores.apparatus),
        )
    )

    # Search filter
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            db.or_(
                models.Gymnasts.name.ilike(like),
                models.Clubs.name.ilike(like),
                models.Competitions.name.ilike(like),
                models.Apparatus.name.ilike(like),
                models.Gymnasts.level.ilike(like),
                db.cast(models.Entries.id, db.String).ilike(like),
                db.cast(models.Gymnasts.id, db.String).ilike(like),
            )
        )

    # Sorting
    # for others use columns/related columns
    total_expr = (
        models.Scores.e_score + models.Scores.d_score - models.Scores.penalty
    )

    level_order_case = db.case(
        (models.Gymnasts.level == 'Level 1', 1),
        (models.Gymnasts.level == 'Level 2', 2),
        (models.Gymnasts.level == 'Level 3', 3),
        (models.Gymnasts.level == 'Level 4', 4),
        (models.Gymnasts.level == 'Level 5', 5),
        (models.Gymnasts.level == 'Level 6', 6),
        (models.Gymnasts.level == 'Level 7', 7),
        (models.Gymnasts.level == 'Level 8', 8),
        (models.Gymnasts.level == 'Level 9', 9),
        (models.Gymnasts.level == 'Junior Inter', 10),
        (models.Gymnasts.level == 'Senior Inter', 11),
        else_=999
    )

    sort_map = {
        'total': total_expr,
        'e_score': models.Scores.e_score,
        'd_score': models.Scores.d_score,
        'penalty': models.Scores.penalty,
        'gymnast_name': models.Gymnasts.name,
        'club_name': models.Clubs.name,
        'competition_name': models.Competitions.name,
        'apparatus_name': models.Apparatus.name,
        'level': level_order_case,
        'id': models.Gymnasts.id,
        'entry_id': models.Entries.id,
    }
    sort_col = sort_map.get(sort_by, total_expr)
    query = query.order_by(
        db.desc(sort_col) if sort_order == 'desc' else db.asc(sort_col)
    )

    # Pagination
    if per_page == -1:  # show all
        results = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        try:
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        except AttributeError:
            pagination = db.paginate(
                query,
                page=page,
                per_page=per_page,
                error_out=False
            )
        results = pagination.items

    return render_template(
        'results.html',
        search_query=search_query,
        current_sort_by=sort_by,
        current_sort_order=sort_order,
        per_page=per_page,
        form=form,
        results=pagination if pagination else type('obj', (object,), {
            'items': results,
            'page': 1,
            'pages': 1,
            'per_page': len(results),
            'total': len(results),
            'has_prev': False,
            'has_next': False,
            'prev_num': None,
            'next_num': None
        })(),
        pagination_options=pagination_options,
        sort_options=sort_options,
    )
