from flask import render_template, redirect, url_for, request
from web import web_bp
from models import db, Incident, User, Comment

@web_bp.route('/')
def index():
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    users = User.query.all()
    return render_template('index.html', incidents=incidents, users=users)

@web_bp.route('/incidents/<int:incident_id>')
def incident_detail(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    users = User.query.all()
    comments = Comment.query.filter_by(incident_id=incident_id).order_by(Comment.created_at.asc()).all()
    return render_template('detail.html', incident=incident, users=users, comments=comments)
