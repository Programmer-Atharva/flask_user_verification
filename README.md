simple flask app to create new user and store data in postgresql db , use some encryption for password , and logout functionality.

demonstration : 

https://github.com/user-attachments/assets/df1bddc7-4080-4b30-abb2-2cef4fb86aa0



prerequisite : postgresql database with table users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(120) NULL,
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

```bash
pip install -r requirements.txt
```

```bash
python app.py db init
```

```text
control+C to stop localhost
```

```bash
python app.py db migrate
```

```text
control+C to stop localhost
```

```bash
python app.py db upgrade
```

