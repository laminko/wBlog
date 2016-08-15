import CommonMark
from index_ext import update_tags_archives

# LANGUAGE
# print request.uri_language
if request.uri_language:
    T.force(request.uri_language)


# CUSTOM HELPERS
def commonmarkIt(text):
    parser = CommonMark.Parser()
    parsed = parser.parse(text.decode('utf-8'))

    renderer = CommonMark.HtmlRenderer(dict(softbreak="<br/>"))
    html = renderer.render(parsed)
    return XML(unicode(html))


# CUSTOM GLOBALS
update_tags_archives(session, db)


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
