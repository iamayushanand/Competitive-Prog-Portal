import requests
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
            LoginManager,
            current_user,
            login_required,
            login_user,
            logout_user,
            )
from oauthlib.oauth2 import WebApplicationClient
import json
import utilities 
import os
from user import User
from dotenv import load_dotenv
app = Flask(__name__)
app.secret_key=os.urandom(24)

load_dotenv();
login_manager=LoginManager()
login_manager.init_app(app)
#Configuration for google oauth 
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
            "https://accounts.google.com/.well-known/openid-configuration"
            )

client=WebApplicationClient(GOOGLE_CLIENT_ID)

#gets the user object and stores it in session. Refer to flask_login docs.
@login_manager.user_loader
def load_user(user_id):
    dbuser=utilities.users.get(user_id)
    user=User(user_id,dbuser[1],dbuser[2])
    return user

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

#The home page
@app.route('/')
def index():
    return render_template("index.html")

#google oauth login client endpoint
@app.route('/login')
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
                    authorization_endpoint,
                    redirect_uri=request.base_url + "/callback",
                    scope=["openid", "email", "profile"],
                )
    return redirect(request_uri)

#Handles callback from google oauth
@app.route('/login/callback')
def callback():
    code=request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
                    token_endpoint,
                    authorization_response=request.url,
                    redirect_url=request.base_url,
                    code=code
                    )
    token_response = requests.post(
                    token_url,
                    headers=headers,
                    data=body,
                    auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
                    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    id_str=userinfo_response.json()['sub']
    email=userinfo_response.json()['email']
    name=userinfo_response.json()['given_name']
    #adds user to db
    utilities.add_user(id_str)
    utilities.update_user(id_str,{"email":email,"name":name})
    user=User(id_str,name,email) 
    #refer flask_login doc.
    login_user(user)
    return redirect(url_for("index")) 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
if __name__ == "__main__":
    app.run(ssl_context="adhoc")
