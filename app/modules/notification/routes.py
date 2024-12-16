from flask import flash, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.modules.notification import notification_bp
from app.modules.notification.models import Notification



@notification_bp.route("/notification/list", methods=["GET"])
@login_required
def list_notifications():
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).all()

    return render_template(
        "notification/list_notifications.html", notifications=unread_notifications
    )

@notification_bp.route("/notifications/mark_as_read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash("You are not authorized to mark this notification as read.", "danger")
        return redirect(url_for("notification.list_notifications"))

    notification.is_read = True
    db.session.commit()

    flash("Notification marked as read.", "success")
    return redirect(url_for("notification.list_notifications"))
