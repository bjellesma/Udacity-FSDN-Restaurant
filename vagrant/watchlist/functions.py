"""
File: functions.py
Author: William Jellesma

This file houses all of the commonly used functions such as verification for usernames and passwords
"""
#flask imports
from flask import Flask, redirect, request, make_response
#security modules
import random
import hashlib
import hmac
from string import letters
import secure




#OS modules
import os
import re

#app imports
import secure

app = Flask(__name__)

"""
Args: self (class reference), name (string), user_id (integer)

function to create cookie based on user id
"""
def set_secure_cookie(name, user_id):
    response = make_response(redirect('/'))
    cookie_val = make_secure_val(user_id)
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=90)
    response.set_cookie(
        'Watchlist-login',
        '%s=%s' % (name, cookie_val))
    return response
"""
Args: self (class reference), name (string)

function to read cookie of user
"""
def read_secure_cookie(name):
    cookie_val = request.cookies.get(name)
    if cookie_val:
        print "cookie found"
    return cookie_val and check_secure_val(cookie_val)

"""
Args: length (Integer, default = 5)

Returns:
A random string of a specified number of letters for use in salting passwords
"""
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

"""
Args: name (string), pw (string), salt (string, default = None)

Returns:
A comma seperated salt and password hash using sha256 with salt
"""
def make_pw_hash(name, pw, salt = None):
    #if no salt is defined by the user, we will create one
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

"""
Args: name (string), pw (string), hashToCompare (string)

Returns:
True if the user entered password matches our password hash when the user's password is hashed
"""
def checkLoginPassword(name, password, hashToCompare):
    #the salt is the first comma seperated parameter stored
    salt = hashToCompare.split(',')[0]
    return hashToCompare == make_pw_hash(name, password, salt)

#secure value for making cookies
secret = secure.secret



"""
Args: user_id (integer)

Returns:
secure value for use in creating cookies based on the global secret value and the user's id
"""
def make_secure_val(user_id):
    return '%s|%s' % (user_id, hmac.new(secret, str(user_id)).hexdigest())

"""
Args: secure_val (integer)

Returns:
The secure value stored in the cookie if the cookie values match for the client and server
"""
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

#validation variables using regular expressions
#used when registering a new user
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

"""
Args: username (string)

Returns:
True if the username is between 3 and 20 characters and is alphanumeric
"""
def valid_username(username):
    return username and USER_RE.match(username)

"""
Args: password (string)

Returns:
True if the password is between 3 and 20 characters
"""
def valid_password(password):
    return password and PASS_RE.match(password)

"""
Args: email (string)

Returns:
True if the email contains an @ followed by .
"""
def valid_email(email):
    return not email or EMAIL_RE.match(email)
