simple flask app to create new user and store data in postgresql db , use some encryption for password , and logout functionality.

demonstration : 



https://github.com/user-attachments/assets/94371f9d-177d-4405-8a15-349d34020704




prerequisite : postgresql database with table users

```sql
CREATE TABLE users (
    email VARCHAR(120) PRIMARY KEY UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(128) NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```


now open terminal in flask app then : 

```bash
    python -m venv venv
```

```bash
    source venv/bin/activate
```

install -r requirements.txt and node js for tailwind inside venv


```bash
    python app.py db init
```

> control+C to stop localhost

```bash
    python app.py db migrate
```

> control+C to stop localhost

```bash
    python app.py db upgrade
```

