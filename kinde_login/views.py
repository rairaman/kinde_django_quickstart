from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseBadRequest

# Import the Kinde SDK, dotenv and a few std lib modules
import os, base64
from kinde_sdk.kinde_api_client import GrantType, KindeApiClient
from dotenv import load_dotenv
import uuid

# Call load_dotenv so we can access values from the .env file
load_dotenv()

# For now, we'll just use a dictionary to hold a bunch of clients for each
# user in memory
user_clients = {}

# A few helper functions to manage
# the data coming back from Kinde
def __get_empty_context():
    return {
        "authenticated": False,
        "user_first_name": "",
        "user_last_name": "",
    }

def __get_user_context(user_id):
    context = __get_empty_context()

    user_client = user_clients.get(user_id)

    if user_client is not None:
        is_user_authenticated = user_client.get('kinde_client').is_authenticated()
        user_last_name = user_client.get('user_last_name')
        user_first_name = user_client.get('user_first_name')

        context = {
            "authenticated": is_user_authenticated,
            "user_first_name": user_first_name,
            "user_last_name": user_last_name,
            "user_full_name": user_first_name + ' ' + user_last_name,
            "user_initials": user_first_name[0] + f"{user_last_name[0] if user_last_name is not None else user_first_name[1]}"
        }

    return context

def __get_new_kinde_client():
    return KindeApiClient(
        domain=os.getenv("KINDE_ISSUER_URL"),
        callback_url=os.getenv("KINDE_CALLBACK_URL"),
        client_id=os.getenv("KINDE_CLIENT_ID"),
        client_secret=os.getenv("KINDE_CLIENT_SECRET"),
        grant_type=GrantType.AUTHORIZATION_CODE,
    )

# The main page!
def index(request):
    context = __get_empty_context()

    if request.session.get('user_id') is not None:
        user_id = request.session.get('user_id')
        context = __get_user_context(user_id)

    return render(request, "kinde_login/index.html", context)

def other(request):
    context = __get_empty_context()

    if request.session.get('user_id') is not None:
        user_id = request.session.get('user_id')
        context = __get_user_context(user_id)

    return render(request, "kinde_login/other.html", context)

# What gets run when you sign in
def login(request):
    context = __get_empty_context()

    # Check if there's a session for this user
    if request.session.get('user_id') is None:
        state = str(uuid.uuid4()).replace('-','')
        request.session['login_redirect'] = request.GET.get('next', reverse('index'))
        request.session['login_state'] = state

        kinde_client = __get_new_kinde_client()
        return redirect(kinde_client.get_login_url(state=state))
    else:
        user_id = request.session.get('user_id')
        context = __get_user_context(user_id)
        return render(request, "kinde_login/index.html", context)

# What gets run when you register
def register(request):
    # Check if there's a session for this user
    if request.session.get('user_id') is None:
        kinde_client = __get_new_kinde_client()
        return redirect(kinde_client.get_register_url())
    else:
        user_id = request.session.get('user_id')
        context = __get_user_context(user_id)
        return render(request, "kinde_login/index.html", context)

# When your user is done authenticating in Kinde
# Kinde calls this route back
def callback(request):
    context = __get_empty_context()

    received_state = request.GET.get('state')

    if received_state != request.session.get('login_state'):
        return HttpResponseBadRequest("Invalid state")

    if request.session.get('user_id') is None:

        kinde_client = __get_new_kinde_client()

        kinde_client.fetch_token(authorization_response=request.build_absolute_uri())
        user_details = kinde_client.get_user_details()
        user_id = user_details['id']
        request.session['user_id'] = user_id
        user_clients[user_id] = {
            "kinde_client": kinde_client,
            "authenticated": True,
            "user_first_name": user_details['given_name'],
            "user_last_name": user_details['family_name'],
        }

        # Redirect to the saved URL
        redirect_url = request.session.get('login_redirect', reverse('index'))
        
        # Clean up session variables
        del request.session['login_redirect']
        del request.session['login_state']

        return redirect(redirect_url)

    else:
        user_id = request.session.get('user_id')
        context = __get_user_context(user_id)

    return render(request, "kinde_login/index.html", context)

# What gets run when you logout
def logout(request):
    index_path = request.build_absolute_uri('/kinde_login/')
    user_id = request.session.get('user_id')
    kinde_client = user_clients.get(user_id).get('kinde_client')
    request.session.clear()
    user_clients[user_id] = None

    return redirect(kinde_client.logout(redirect_to=index_path))