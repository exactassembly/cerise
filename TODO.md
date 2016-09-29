* make sure that login view is passing NoneType for ref dict values
* clean up project template
* buildlight definitely needs rewriting
* many views are not using wtfforms for hidden fields

##backburn:

* implement permissions for projects

##notes:

parent.update(pull__subs__id=ObjectId("57d9a9a0c8b9162ff00f7ab6"))

POST schema:

`{'name': 'test', 'steps': [{'step': 'ls', 'workdir': 'memes'}, {'step': 'otherstuff', 'workdir': '~/reddit'}], 'gitrepo': 'test'}`

~700 queries per second iterating through lists of references