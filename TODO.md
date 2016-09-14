* bootstrap implementation

* refs are just proxies and require explicit saving (i.e. current_user.group.save())

* lots of testing with how ref and list queries work

##* implement permissions for projects

* implement UX for group creation, offering choice between individual and group account

parent.update(pull__subs__id=ObjectId("57d9a9a0c8b9162ff00f7ab6"))

POST schema:

`{'name': 'test', 'steps': [{'step': 'ls', 'workdir': 'memes'}, {'step': 'otherstuff', 'workdir': '~/reddit'}], 'gitrepo': 'test'}`

~700 queries per second iterating through lists of references