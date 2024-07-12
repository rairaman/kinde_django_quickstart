# Kinde Django quickstart
This quickstart repo starts a Django application with routes setup to register and login to a Kinde Business

## Instructions
1. Clone the repo and run `pip install -r requirements.txt`
1. Make a copy of the `.env_sample` file and rename the copied file to `.env`
1. In the `.env` file, populate the details using a Kinde Backend Application, for e.g.
    ```
    KINDE_CLIENT_ID=123456
    KINDE_CLIENT_SECRET=AbcDef1345
    KINDE_ISSUER_URL=https://mysuperbusiness.kinde.com
    KINDE_CALLBACK_URL=http://127.0.0.1:8000/kinde_login/callback
    KINDE_LOGOUT_URL=http://127.0.0.1:8000/kinde_login/
    ```
1. Add the callback URL and logout URL to your backend application in Kinde
1. Run the Django app: `python manage.py runserver`
1. Navigate to `http://localhost:8000/kinde_login` to login

Note: 
More information on the Python SDK and Django with Kinde can be found at
- https://kinde.com/docs/developer-tools/python-sdk/
- https://kinde.com/blog/engineering/set-up-django-authentication-with-kinde/
