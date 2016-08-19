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
                Field('is_public', 'boolean', default=True,
                      comment='Public url is like <b>/getobject/(id)</b>.'),
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
