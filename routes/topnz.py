from flask import render_template
from . import main


@main.route('/topnz')
def topnz():
    return render_template('topnz.html')
