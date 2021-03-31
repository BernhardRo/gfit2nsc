# gfit2nsc
This is a script that reads activities from Google Fit and writes them to Nightscout

# HowTo use it:
## Install needed Python libaries with: pip install google-auth oauth2client requests arrow
## Rename secret-Example.py to secret.py and change it:
* NS_URL and NS_SECRET is your Nightscout URL and secret / API key
* For the other values, you need to have a Google account and create these values for yourself. To do so, follwo the instructions on https://developers.google.com/fit/rest/v1/get-started:
** Create a project in "https://console.cloud.google.com/flows/enableapi?apiid=fitness&pli=1", e.g. called "gfit2nsc"
** Add OAuth Autorization for type Desktop App and use these credentials as "CLIENT_ID" and "CLIENT_SECRET"
** Authorize yourself to access your Gfit data: "https://developers.google.com/oauthplayground/" -> Expand "Fitness v1". You need "activitiy.read" (first one)
