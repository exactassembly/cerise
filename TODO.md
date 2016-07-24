#### buildslave decisions
* ec2latent requires full spinup from AWS image 
    * need to reanalyze ec2-init and compartmentalize base image and init scripts
* ssh exec more agnostic, easier to work with, allows direct awscli start/stop
* ec2 containers also incredibly appealing, allows moving existing docker API calls over to ec2 docker calls

#### vagrant configuration
* need to stage /build, stuff master.cfg into bb-ec2

----

* git token and buildmaster env vars
