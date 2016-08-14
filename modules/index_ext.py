import math


def group_by_tags(db):
    simple_where = (db.post.is_draft == False)
    all_tags = db(simple_where).select(
        db.post.tags.lower().with_alias("tags")
    )
    flattened_tags = []
    for each_tag in all_tags:
        flattened_tags.extend(each_tag.tags)
    tags = []
    for each_tag in set(flattened_tags):
        result = db(db.post.tags.contains(each_tag) & simple_where).select(
            db.post.id.count().with_alias('total')
        ).last().as_dict()
        result.update(dict(tag=each_tag.capitalize()))
        tags.append(result)
    return sorted(tags, key=lambda k: k.get('total'), reverse=True)


def group_by_archives(db):
    simple_where = (db.post.is_draft == False)
    archives = db(simple_where).select(
        db.post.id.count().with_alias('total'),
        db.post.created_on.year().with_alias('year'),
        groupby=db.post.created_on.year(),
        orderby=~db.post.created_on.year()
    )
    return archives


def calculate_total_pages(session, db):
    total_row = float(db(db.post.is_draft == False).count())
    return math.ceil(total_row / session.max_record_per_page)


def update_tags_archives(session, db):
    session.max_record_per_page = 5.0
    session.max_pages = calculate_total_pages(session, db)
    session.TAGS = group_by_tags(db)
    session.ARCHIVES = group_by_archives(db)
