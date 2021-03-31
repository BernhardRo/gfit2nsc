# gfit2nsc
This is a script that reads activities from Google Fit and writes them to Nightscout

## HowTo use it:
1. Install needed Python libaries with: pip install google-auth oauth2client requests arrow
2. Create your needed Google Fit credentials to access the Gfit REST API:
* You need to have a Google account and follow the instructions on https://developers.google.com/fit/rest/v1/get-started:
** Create a project in "https://console.cloud.google.com/flows/enableapi?apiid=fitness&pli=1", e.g. called "gfit2nsc"
** Add OAuth Autorization for type Desktop App and use these credentials as "CLIENT_ID" and "CLIENT_SECRET"
** Authorize yourself to access your Gfit data: "https://developers.google.com/oauthplayground/" -> Expand "Fitness v1". You need "activitiy.read" (first one)
** Authorize OAuth to access your data -> "ACCESS_TOKEN" + "REFRESH_TOKEN"
4. Rename secret-Example.py to secret.py and change it:
* NS_URL and NS_SECRET is your Nightscout URL and secret / API key
* Update the other values according your Gfit credentials
