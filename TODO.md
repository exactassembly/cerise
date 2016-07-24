#### buildslave decisions
* ec2latent requires full spinup from AWS image 
    * need to reanalyze ec2-init and compartmentalize base image and init scripts
* local slaves + awscli start/stop another option, less bullshit, fits the current non-ephemeral model better
* ec2 containers also incredibly appealing, allows moving existing docker API calls over to ec2 docker calls

#### vagrant configuration
* need to stage /build, stuff master.cfg into bb-ec2

----

* git token and buildmaster env vars
