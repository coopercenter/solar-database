# Solar Database

The Virginia Solar Database (VSD) provides a summary of large-scale solar projects proposed for siting approval at the local level in Virginia. It includes projects over 1 MW (with the exception of BARC Community Solar Project in Bath County) that have been advertised for a local public hearing. The database excludes school and government installations and procurement projects (with some exceptions for notable projects such as NASA Wallops, Oceana, and landfill projects such as Campostella).

__Solar Database__: [https://solardatabase.coopercenter.org/](https://solardatabase.coopercenter.org/)

## Development

### Setting up a virtual environment

1. If you do not already have a virtual environment set up for this project, in the terminal run "python3 -m venv .venv" to create the virtual environment
2. Add .venv/ to .gitignore
3. Run "source .venv/bin/activate" to enter the virtual environment
4. Install the required packages with "python3 -m pip install -r requirements.txt"

### Create the hidden variables for connecting to the database

1. Create a new folder named hidden, add hidden/ to .gitignore
2. In the new hidden folder, create name.txt, enter the name of the database you're connecting to
3. Next, create user.txt and enter your database username
4. Create password.txt, enter your database password
5. Add host.txt, and the host server name
6. Finally, create port.txt and add the port number. The default port number is 5432

### Start running the development server!

Enter 'python3 manage.py runserver' to run the development server. If it opens in your browser with the url http://127.0.0.1:8000/, you're good to start updating the solar database webpage in your new development environment!

### Testing features for release
1. When all needed changes have been made and the local server runs successfully, push all your changes to the dev branch. If using Git, in the command line, `run git add file_name` to add the file(s) that have been changed. Next, in the command line, run `git commit 'commit_name'` to name your commit and run `push origin -u dev` to push your changes to the dev branch.

2. The dev branch deploys to the Solar Database web app which includes the preloaded configurations used by the Solar Database to test your changes on the Azure server. If changes are needed for the preloaded configurations, contact Mary Beth Wetherell at [meh4q@virginia.edu](meh4q@virginia.edu) for access. Changes pushed to the dev branch will automatically be deployed to the developer web app and can be tracked in the _Actions_ tab on Github.

      __Solar Database Developer Web App__: [https://va-solar-db-dev.azurewebsites.net](https://va-solar-db-dev.azurewebsites.net/)

3. Checking to ensure the developer Azure site is successful and is prepared for release. Otherwise, if the deployment failed or the server failed to load, address the error as needed, push the changes to your branch, and redeploy the code. For additional help, see [Debugging Tips](#debugging-tips).

### Updating the Data
1. When adding columns or changing their names, start by updating the database names in models.py.
2. If changing or adding objects in models.py, confirm objects used in views.py, plotly_dash.py, data.html and project.html call the correct object names from models.py.
3. Edit column display names in data.html and project.html.

## Debugging Tips

### Deprecated Packages
1. Deprecated packages are outdated past their newest version and should be updated as it may pose both a security risk and result in runtime errors. The runtime error displayed will likely point to the packages that are needing to be updated. 
2. Updating deprecated packages may require changing `import` statements, adding new lines of code in accordance with the documentation of the newest iteration often made in _settings.py_, or changing the version in _requirements.txt_ as indicated after the `==`.

### Package Dependencies
1. As packages are updated, this often results in runtime errors as packages often call on each other and therefore rely on certain versions of a particular package. Therefore, _requirement.txt_ must outline packages that include the correct version of each package's dependencies in order to be successfully deployed.The runtime error displayed will likely outline the package's missing dependencies and their necessary versions.
2. Changing package dependencies is a process of repeated trial and error, involving deprecating as needed after the `==` or changing the order of packages in  _requirement.txt_ to be successful. While the packages may run successfully on your computer, there will likely be errors when deploying on Azure as their operating systems differ. 

### Deployment Failure
1. The error can be found by checking the deployment logs and clicking on the commit ID that was deployed or on the repoistory under actions in the respective workflow.
2. As your computer's operating system likely differs from Azure, the error is likely from the result of a failure in [Package Dependencies](#package-dependencies). 
3. If package dependencies cannot be reconciled, a potential solution is to dockerize the web app by placing it with your computer's operation system but the current iteration of the web app is not dockerized. 

 ### Runtime Errors
 1. If the developer web app or local server displays an error, additional information can be found by setting `DEBUG = TRUE` in _settings.py_ but __must__ set back to `DEBUG = FALSE` before merging your branch with the master branch.
 2. The error is likely the result of [Deprecated Packages](#deprecataed-packages) or updating the code as needed to with the newest iteration of Django.
