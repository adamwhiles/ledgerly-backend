# ledgerly-backend

This is the Python/Flask backend for the ledgerly-frontend which is what makes up ledgerly.online

## Requirements

Python, Flask, Flask-SQLAlchemy, Flask-Login, SimpleJSON, dotenv, MySQL Database

File in the root folder called **.env** with the following variables set
```
DBHOST=
DB=
DBUSER=
DBPASS=
DBURI=mysql+pymysql://
SECRET=
```
## Usage

Create a virtual environment for the app and install all of the requirements. Enter the virtual environment.
```
flask run
```


## License
[MIT](https://choosealicense.com/licenses/mit/)
