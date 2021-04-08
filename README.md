# gfit2nsc

This is a script that reads activities from Google Fit and writes them to Nightscout

## HowTo use it

1. Install needed Python libaries with:
   pip install --upgrade google-auth oauth2client requests arrow google-api-python-client google-auth-httplib2 google-auth-oauthlib
2. Create your needed Google Fit credentials to access the Gfit REST API:
  You need to have a Google account and follow the instructions on <https://developers.google.com/fit/rest/v1/get-started>:

* Create a project in "https://console.cloud.google.com/flows/enableapi?apiid=fitness&pli=1"
* Add credentials for Fitness API and "Other UI"
* Setup OAuth consent screen for Fitness API and authorize yourself as test user
* Create OAuth client ID credentials for Desktop App and download it as json file
* Rename the json file to client_secret.json and save it next to this python script (replace available dummy file)
* These steps are also available as screenshots in the folder screenshots

3. Rename secret-Example.py to secret.py and change it:

* NS_URL and NS_SECRET is your Nightscout URL and secret / API key
