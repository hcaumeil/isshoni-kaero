# isshoni-kaero 

## Deploy

### Api

- Go in api folder
- Setup a postgresql
- Generate a private biscuit key at : https://www.biscuitsec.org/docs/tooling/token-generator/
- Install requirement.txt
- Setup following env vars :
```
BISCUIT_KEY="pv_key"
POSTGRESQL_ADDON_DB="db_name"
POSTGRESQL_ADDON_HOST="host_url"
POSTGRESQL_ADDON_PASSWORD=""
POSTGRESQL_ADDON_PORT="6969"
POSTGRESQL_ADDON_URI="magic_url"
POSTGRESQL_ADDON_USER="pg_user"
POSTGRESQL_ADDON_VERSION="15"
```
Start with : uvicorn main:app

### Front end

Go in front-end folder
```
npm i
ng build
ng serve
```

In prod change api url at ```isshoni-kaero/isshoni-kaero/src/environments/environment.ts```

