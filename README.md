# Solar Database

##Setting up to run the app for the first time

### Setting up a virtual environment

* If you do not already have a virtual environment set up for this project, in the terminal run "python3 -m venv .venv" to create the virtual environment
* Add .venv/ to .gitignore
* Run "source .venv/bin/activate" to enter the virtual environment
* Install the required packages with "python3 -m pip install -r requirements.txt"

###Create the hidden variables for connecting to the database

* Create a new folder named hidden, add hidden/ to .gitignore
* In the new hidden folder, create name.txt, enter the name of the database you're connecting to
* Next, create user.txt and enter your database username
* Create password.txt, enter your database password
* Add host.txt, and the host server name
* Finally, create port.txt and add the port number. The default port number is 5432

###Start running the development server!

* Enter 'python3 manage.py runserver' to run the development server. If it opens in your browser with the url http://127.0.0.1:8000/, you're good to start updating the solar database webpage in your new development environment!

##General notes as I work through updating the data and enduring no issues
* when adding columns or changing their names, start in models.py. Columns are then used in 

