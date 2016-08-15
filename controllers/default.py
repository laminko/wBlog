# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

from index_ext import update_tags_archives


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    archive_year = request.vars.year or None
    archive_month = request.vars.month or None
    archive_day = request.vars.day or None
    current_tag = request.vars.tag or None
    current_page = request.vars.page or None

    response.title += ' | ' + T('Posts')
    if not current_page:
        redirect(URL(vars={'page': 1}))
    else:
        page = int(current_page)

    max_record = session.max_record_per_page
    start = (page-1) * max_record
    end = page * max_record
    full_name = T("Visitor")

    if auth.user:
        full_name = "%(first_name)s %(last_name)s" % auth.user.as_dict()

    template_text = T("Hello, %s!")
    welcome_text = template_text % full_name

    where = (db.post.is_draft == False)
    if archive_year and archive_month and archive_day:
        where &= (db.post.created_on.year() == archive_year) & \
                 (db.post.created_on.month() == archive_month) & \
                 (db.post.created_on.day() == archive_day)
    elif archive_year and archive_month:
        where &= (db.post.created_on.year() == archive_year) & \
                 (db.post.created_on.month() == archive_month)
    elif archive_year:
        where &= (db.post.created_on.year() == archive_year)
    elif current_tag:
        where &= (db.post.tags.contains(current_tag))
    else:
        response.flash = welcome_text

    posts = db(where).select(
        db.post.ALL,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.postcomment.id.count().with_alias('comments'),
        groupby=db.post.id,
        left=(
            db.auth_user.on(db.post.created_by == db.auth_user.id),
            db.postcomment.on(
                (db.post.id == db.postcomment.post) &
                (db.postcomment.reply_to == None)
            )
        ),
        orderby=~db.post.created_on,
        limitby=(start, end)
    )

    return dict(posts=posts)


@auth.requires(
    auth.has_membership('Root') or
    auth.has_membership('Admin') or
    auth.has_membership('Editor')
)
def posts():
    grid = SQLFORM.grid(
        db.post,
        paginate=10
    )
    return dict(form=grid)


@auth.requires(
    auth.has_membership('Root') or
    auth.has_membership('Admin') or
    auth.has_membership('Editor')
)
def uploads():
    grid = SQLFORM.grid(
        db.upload,
        paginate=10
    )
    return dict(form=grid)


def about():
    return dict()


def contact():
    form = SQLFORM(db.contact)
    if auth.settings.captcha:
        recaptch_widget = DIV(
            LABEL(
                T('Verify'),
                _class="control-label col-sm-3"
            ),
            DIV(
                auth.settings.captcha,
                _class="col-sm-9"
            ),
            _class="form-group")
        form.element('div#submit_record__row').insert(
            -1,
            recaptch_widget
        )
    if form.process().accepted:
        pass
    return dict(form=form)


def post():
    post_id = request.args(0) or None
    record = db(db.post.id == post_id).select(
        db.post.ALL,
        db.auth_user.first_name,
        db.auth_user.last_name,
        left=db.auth_user.on(db.post.created_by == db.auth_user.id)
    ).last()
    return dict(record=record)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def getobject():
    """
    For the files which are accessible to everyone.
    """
    image_id = request.args(0) or None
    if image_id:
        image = db((db.upload.id == image_id) &
                   (db.upload.is_public == True)).select().last()
        if image:
            redirect(URL('download', args=[image.the_file]))
    error_message = T("File not found!")
    raise HTTP(404, error_message)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


# @request.restful()
# def api():
#     response.view = 'generic.' + (request.extension or 'json')
#     def GET(*args, **vars):
#         patterns = 'auto'
#         parser = db.parse_as_rest(patterns, args, vars)
#         if parser.status == 200:
#             return dict(content=parser.response)
#         else:
#             raise HTTP(parser.status,parser.error)
#
#     def POST(table_name, **vars):
#         return db[table_name].validate_and_insert(**vars)
#
#     def PUT(table_name, record_id, **vars):
#         return db(db[table_name]._id == record_id).update(**vars)
#
#     def DELETE(table_name, record_id):
#         return db(db[table_name]._id == record_id).delete()
#
#     return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)
