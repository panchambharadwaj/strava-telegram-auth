# Strava Telegram Auth

App that is ready to be deployed on Heroku. Attach a Postgres Dabatase to the app and create the table before using the app.

### Create table

```
heroku run bash --app <app_name>
python app/ddl/create_table.py
```