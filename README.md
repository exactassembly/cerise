# cerise
Docker based Yocto build environments

## usage:
`python3 cerise.py`

## configuration:
Relies on variable `CERISE_CONFIG` being set to location of configuration file.

```
MONGODB_SETTINGS = {
	'db': 'DATABASE_NAME',
	'username': 'DATABASE_USERNAME',
	'password': 'DATABASE_PASSWORD'
}

SECRET_KEY='YOUR_SECRET_KEY'
```