# deluxedom
A Flask web application to help you find your next 5 letter domain.

The web app uses the [Cloudflare API](https://developers.cloudflare.com/api/operations/registrar-domains-get-domain) to query all domains in the database. 

You need to create a .env file that has the following 3 items:

* API_EMAIL
* API_KEY
* API_ACCOUNT_ID

At this point a database needs to be manually created using the CREATE commands found in app.py at lines 32-55.

TODO:
1. Write up deploy to debian server
2. Create requirements.txt for all pip3 installs
3. Switch database from cs50 library to sqlite3 and create automatically a db if it doesn't exist
4. Add 5 letter pending delete / autorenew period domains page
5. Consider adding 3, 4 letter generated domains (check excel for stats on word formats)
6. Consider adding 6 letter domains