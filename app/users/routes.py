from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _
from app import db
from app.users.forms import EditProfileForm, MessageForm
from app.models import User, Post, Message, Notification
from guess_language import guess_language
from app.users import bp


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('users.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('users.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Vos modifications ont été enregistrées.'))
        return redirect(url_for('users.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Modifier le profil'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Utilisateur %(username)s introuvable.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('Vous ne pouvez pas vous suivre !'))
        return redirect(url_for('users.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('Vous suivez maintenant %(username)s !', username=username))
    return redirect(url_for('users.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Utilisateur %(username)s introuvable.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('Vous ne pouvez pas vous suivre !'))
        return redirect(url_for('users.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('Vous ne suivez plus %(username)s.', username=username))
    return redirect(url_for('users.user', username=username))


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        language = guess_language(form.message.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data, language=language)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Votre message a été envoyé.'))
        return redirect(url_for('users.user', username=recipient))
    return render_template('send_message.html', title=_('Envoyer un message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('users.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('users.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])