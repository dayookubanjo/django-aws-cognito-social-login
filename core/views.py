from django.shortcuts import render
from decouple import config
import base64
import requests
from . import decode_jwt 

# Create your views here.

def index(request):
    print("I'm in!")
    try:

        code = request.GET.get('code')
        # print(code)
        userData = getTokens(code)
        # print(userData)
        context = {'name': userData['name'], 
                    'email': userData['email'],
                    'status': 1,}
        # print(context)
        response = render(request, 'core/index.html' , context)
        response.set_cookie('sessiontoken', userData['id_token'], max_age=60*60*24, httponly=True)

        return response
    except Exception as e:
        token = getSession(request)
        if token is not None:
            userData = decode_jwt.lambda_handler({'token':token}, None)
            context = {'name': userData['name'], 
                    'email': userData['email'],
                    'status': 1,}
            print(context)
            render(request, 'core/index.html' , context)

        print("No code")
        return render(request, 'core/index.html', {'status': 0})

def signout(request):  
    response =  render(request, 'core/index.html', {'status': 0}) 
    response.delete_cookie('sessiontoken')
    return response


def getTokens(code):
    TOKEN_ENDPOINT = config('TOKEN_ENDPOINT')
    REDIRECT_URI = config('REDIRECT_URI')
    CLIENT_ID = config('CLIENT_ID')
    CLIENT_SECRET = config('CLIENT_SECRET')

    encodeData = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}", "ISO_8859-1")).decode("ascii")
    # print(encodeData)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encodeData}'
    }

    body = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    # print(body)
    response = requests.post(TOKEN_ENDPOINT, data=body, headers=headers)
    # print("response", response)
    id_token = response.json()['id_token']
    # print("id_token", id_token)
    userData = decode_jwt.lambda_handler({'token':id_token}, None)
    # print("userData", userData)
    if not userData:
        return False 

    user = {
        'id_token': id_token,
        'name': userData['name'],
        'email': userData['email']
    }

    return user


def getSession(request):
    try:
        response = request.COOKIES["sessiontoken"]
    except:
        return None