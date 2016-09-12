* bootstrap implementation

* refs are just proxies and require explicit saving (i.e. current_user.group.save())

* lots of testing with how ref and list queries work

##* use IDs for all updates

##* implement permissions for projects

* construct account pages with (id, name) tuples from list comprehensions

POST schema:

`{'name': 'test', 'steps': [{'step': 'ls', 'workdir': 'memes'}, {'step': 'otherstuff', 'workdir': '~/reddit'}], 'gitrepo': 'test'}`

~700 queries per second iterating through lists of references