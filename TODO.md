* test wsgi deployment, see if yield lines stream is actually blocking and if streams deteriorate correctly
* look into js SSE implementation
* wtforms validators, alphanum, single word, email
* req. aws information

POST schema:

`{'name': 'test', 'steps': [{'step': 'ls', 'workdir': 'memes'}, {'step': 'otherstuff', 'workdir': '~/reddit'}], 'gitrepo': 'test'}`