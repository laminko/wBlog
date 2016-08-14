def totalcomments():
    postid = request.vars.postid or None
    comments = db(
        (db.postcomment.post == postid) &
        (db.postcomment.reply_to == None)
    ).count()
    return dict(comments=comments)


def post():
    postid = request.vars.postid or None
    reply_to = request.vars.reply_to or None
    form = None
    comments = db(
        (db.postcomment.post == postid) &
        (db.postcomment.reply_to == None)
    ).count()
    if auth.is_logged_in():
        form = SQLFORM(db.postcomment, hidden=dict(reply_to=None))
        if form.process().accepted:
            db.postcomment.insert(
                post = postid,
                body = form.vars.body,
                reply_to = reply_to
            )
            response.flash = "Comment saved."
    return dict(form=form,
                comments=comments,
                postid=postid)


def reply():
    postid = request.vars.postid or None
    reply_to = request.vars.reply_to or None
    hide_reply = request.vars.hide_reply or "F"
    comments = db(
        (db.postcomment.post == postid) &
        (db.postcomment.reply_to == reply_to)
    ).select()
    return dict(comments=comments, postid=postid, hide_reply=hide_reply)


@auth.requires(
    auth.has_membership('Root') or
    auth.has_membership('Admin') or
    auth.has_membership('Editor')
)
def removeComment():
    status_code = 0
    comment_id = request.vars.comment_id or None
    try:
        db(db.postcomment.id == comment_id).update(
            is_deleted=True
        )
        status_code = 1
    except:
        status_code = 0
    return dict(status=status_code)
