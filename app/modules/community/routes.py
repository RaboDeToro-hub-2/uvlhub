from flask import render_template, redirect, url_for, flash
from app import db
from app.modules.community.forms import CommunityForm
from app.modules.community.models import Community
from app.modules.community import community_bp
from flask_login import login_required, current_user
from flask import Blueprint
from . import routes

@community_bp.route('/list', methods=["GET", "POST"])
@login_required
def list_communities():
    # Obtener todas las comunidades de la base de datos
    communities = Community.query.all()
    
    # Renderizar la plantilla con las comunidades
    return render_template('community/list_communities.html', communities=communities)


@community_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CommunityForm()
    if form.validate_on_submit():
        new_community = Community(
            name=form.name.data,
            description=form.description.data,
        )
        
        db.session.add(new_community)
        db.session.commit()
        
        flash('Community created successfully!', 'success')
        return redirect(url_for('public.index'))
    
    return render_template("community/create.html", form=form)
