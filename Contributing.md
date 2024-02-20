Preferable Python version : 3.11.8

# Setting up for first time
- Clone the repo

    ` git clone https://github.com/Aditya-1208/SurveilHub.git`

- cd into the repository

    `cd SurveilHub`

- Initialize and activate virtual environment

    - Install virtualenv package

      `pip install virtualenv`

    - Create a new virtual environment

      `python -m venv .venv`

    - Activate the virutal environment

      `.venv\Scripts\activate`

-  Install the requirements

    `pip install -r requirements.txt`

## Database setup
- Install the MYSQL database community edition if not installed already

- Connect as root using workbench or mysql shell

- Create a new database for our application

    `CREATE DATABASE surveilhub_dev;`

- Create a new user with limited access scope (optional)

    ```
    CREATE USER 'YOUR_USERNAME'@'%' IDENTIFIED BY 'YOUR_PASSWORD';

    GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, REFERENCES ON surveilhub_dev.* TO 'YOUR_USERNAME'@'%';

    FLUSH PRIVILEGES;
    ```
    - Here replace YOUR_USERNAME and YOUR_PASSWORD with your desired username and password


- Create a new file at root level `.env`

- Populate the file with the following content

    ```
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=YOUR_USERNAME
    DB_PASSWORD=YOUR_PASSWORD
    DB_NAME=surveilhub_dev

    FLASK_APP=app
    FLASK_ENV=development
    ```

    - Here replace YOUR_USERNAME and YOUR_PASSWORD with your previously created username and password
    - Incase you did not create a new user, use `root` as `username` and the corresponding password as `password`

## Test the Database setup

- Run the flask shell from CLI

    `Flask shell`

- Print the db instance

    ```
    from app.extensions import db
    print(db)
    ```

    - You should see a SQLAlchemy instance with your db connection URI, which confirms that the database connection is setup correctly!

## Run migrations

- Run command to migrate existing migrations

    ```
    flask db upgrade
    ```


<br/>

# Guidelines to follow
-  Always activate virtual environment before working on the project

- Don't update any package inside virtual environment

- Each time you install or uninstall a package inside virtual environment, update the requirements.txt file

    `pip freeze > requirements.txt`

- Reinstall the requirements if you encounter package missing issues

    `pip install -r requirements.txt`

<br/>

# Running the flask app

- Running the flask server

    `flask run`

- Running the server with debug mode

    `flask run --debug`

# Changes to the database

- All changes to database must be through migrations only!
    - To create migrations for changes made, run

        `flask db migrate -m "YOUR_MESSAGE"`
    - To apply the migrations

        `flask db upgrade`
    - To reverse last migration

        `flask db downgrade`

- If you create a new model, import it into application factory file to enable the Flask-Migrate to detect the new model/

- In some cases, Flask-Migrate may not be able to detect changes, in such cases, create migration files yourself and add/edit the contents to enforce requried changes!
