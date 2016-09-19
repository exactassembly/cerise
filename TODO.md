
* implement group creation and management

* transaction tokens

* user refer unpaid user
* decide whether group-paid state exists on user or group, ui for deleting users from group, subscription state tracking
* finish restructuring, imports

##backburn:

* implement permissions for projects

##notes:

parent.update(pull__subs__id=ObjectId("57d9a9a0c8b9162ff00f7ab6"))

POST schema:

`{'name': 'test', 'steps': [{'step': 'ls', 'workdir': 'memes'}, {'step': 'otherstuff', 'workdir': '~/reddit'}], 'gitrepo': 'test'}`

~700 queries per second iterating through lists of references