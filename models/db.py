# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------

if not request.is_local:
    request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from CommonMark import commonmark
from index_ext import update_tags_archives


# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
# from gluon.tools import Recaptcha

# auth.settings.captcha = Recaptcha(
#     request,
#     'client-side secret',
#     'server-side secret',
#     use_ssl=True
# )
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 5
auth.settings.login_captcha = False

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

SYM_PAGE_BREAKER = " {LMK:PAGE-BREAK} "
SINGLE_SPACE = " "

# Tables
db.define_table('post',
                Field('title', 'string'),
                Field('body', 'text'),
                Field('body_pagebreak',
                      compute=lambda r: (
                        r['body'] or "").split(SYM_PAGE_BREAKER)[0]),
                Field('body_nobreak',
                      compute=lambda r: (
                        r['body'] or "").replace(SYM_PAGE_BREAKER,
                                                 SINGLE_SPACE)),
                Field('has_pagebreak',
                      compute=lambda r: SYM_PAGE_BREAKER in (r['body'] or "")),
                Field('is_draft', 'boolean', default=False),
                Field('total_likes', 'integer', default=0,
                      readable=False, writable=False),
                Field('created_on', 'datetime', default=request.now,
                      readable=False, writable=False),
                Field('created_by', 'reference auth_user',
                      default=auth.user_id,
                      readable=False, writable=False),
                Field('modified_on', 'datetime', update=request.now,
                      readable=False, writable=False),
                Field('modified_by', 'reference auth_user',
                      update=auth.user_id,
                      readable=False, writable=False),
                Field('tags', 'list:string'))

db.define_table('postcomment',
                Field('post', 'reference post',
                      readable=False, writable=False),
                Field('body', 'text', label=T("Comment")),
                Field('is_approved', 'boolean', default=False,
                      readable=False, writable=False),
                Field('is_deleted', 'boolean', default=False,
                      readable=False, writable=False),
                Field('reply_to', 'reference postcomment',
                      readable=False, writable=False),
                Field('created_on', 'datetime', default=request.now,
                      readable=False, writable=False),
                Field('created_by', 'reference auth_user',
                      default=auth.user_id,
                      readable=False, writable=False),
                Field('modified_on', 'datetime', update=request.now,
                      readable=False, writable=False),
                Field('modified_by', 'reference auth_user',
                      update=auth.user_id,
                      readable=False, writable=False))

db.define_table('contact',
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('email', 'string', requires=[IS_NOT_EMPTY(), IS_EMAIL()]),
                Field('description', 'text', requires=IS_NOT_EMPTY()),
                Field('created_on', 'datetime', default=request.now,
                      readable=False, writable=False))

db.define_table('upload',
                Field('title', 'string', requires=IS_NOT_EMPTY()),
                Field('the_file', 'upload'),
                Field('is_public', 'boolean', default=True),
                Field('created_on', 'datetime', default=request.now,
                      readable=False, writable=False),
                Field('created_by', 'reference auth_user',
                      default=auth.user_id,
                      readable=False, writable=False),
                Field('modified_on', 'datetime', update=request.now,
                      readable=False, writable=False),
                Field('modified_by', 'reference auth_user',
                      update=auth.user_id,
                      readable=False, writable=False))


# check default root user exists or not.
if db(db.auth_user).count() < 1:
    # if not:
    # create groups once.
    db.auth_group.bulk_insert([
        dict(role='Root', description='System user'),
        dict(role='Admin', description='Blog admin'),
        dict(role='Editor', description='Blog editor'),
        dict(role='Moderator', description='Blog moderator'),
        dict(role='User', description='Blog reader')
    ])
    # create default root user.
    db.auth_user.insert(
        **dict(
            first_name='System',
            last_name='User',
            email='root@root.su',
            password=db.auth_user.password.validate('root@root.su')[0]
        )
    )
    # set permission for default user.
    auth.add_membership(user_id=1, group_id=1)

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)

# LANGUAGE
# print request.uri_language
if request.uri_language:
    T.force(request.uri_language)


# CUSTOM HELPERS
def commonmarkIt(text):
    return XML(unicode(commonmark(text.decode('utf-8'))))


# CUSTOM GLOBALS
update_tags_archives(session, db)
