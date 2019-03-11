# Strava Telegram Auth

App is ready to be deployed on Heroku. Attach a Postgres Database to the Webhooks App and create the table before using this app.


##### Deploy Hooks HTTP URL
```
https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_chat_id}&text={{app}}%20({{release}})%20deployed!
```

# Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/panchambharadwaj/strava-telegram-auth)