# Strava Telegram Auth

App is ready to be deployed on Heroku. Attach a Postgres Database to the app and create the table before using.

### Create table

```
$ heroku run bash --app <app_name>
$ python app/ddl/create_table.py
$ exit
```

##### Deploy Hooks HTTP URL
```
https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_chat_id}&text={{app}}%20({{release}})%20deployed!
```