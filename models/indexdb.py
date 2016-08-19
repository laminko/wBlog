from plugin_haystack import Haystack


index = Haystack(db.post)
index.indexes('title', 'body')
