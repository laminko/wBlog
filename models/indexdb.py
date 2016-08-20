import os
from plugin_haystack import Haystack # , WhooshBackend


# index_url = os.path.join(
#     os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
#     "index"
# )
#
# hindex = Haystack(db.post, backend=WhooshBackend, indexdir=index_url)

hindex = Haystack(db.post)
hindex.indexes('title', 'body')
