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

<br/>

# Guidelines to follow
-  Always activate virtual environment bwfore working on the project

- Don't update any package inside virtual environment

- Each time you install or uninstall a package inside virtual environment, update the requirements.txt file

    `pip freeze > requirements-freeze.txt`

- Reinstall the requirements if you encounter package missing issues

    `pip install -r requirements.txt`

<br/>

# Running the flask app

- Running the flask server

    `flask --app app run`

- Running the server with debug mode

    `flask --app app run --debug`