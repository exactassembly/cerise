from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from .user.models import User
from .group.models import Group, Token
import boto3, os

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

def verify_aws(awsID, awsKey):
    client = boto3.client(
        'iam',
        aws_access_key_id=awsID,
        aws_secret_access_key=awsKey
    )
    try:
        client.get_user()
        return True
    except ClientError:
        return False

def load_group(current_user, group):
    if current_user.self_group.id == ObjectId(group):
        return current_user.self_group
    elif current_user in Group.objects.get(id=group):
        return Group.objects.get(id=group)
    else:
        raise ValueError('User does not have access to group.')                          

def register_user(form, request):
    user = User(username=form.username.data, email=form.email.data)
    user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
    if request.form.get('key') != 'None' and request.form.get('token') != 'None': # 'None' is a string!
        user.type = 'unpaid'
        group = Group.objects.get(referrals__key=request.form.get('key'))
        group.add_to_group(user, request.form.get('key'))
    else:
        group = Group(name=form.username.data)
        group.directory = os.path.join('/build', '_'.join(group.name.split()))
        group.save()        
        user.self_group = group
        user.save()
        group.users.append(user)
        group.save()
        user.save()
        group.create_master()
    return user

def consume_token(token):
    try:
        Token.objects.get(token=token)
        Token.objects.get(token=token).delete()
    except:
        raise ValueError('Token not valid.')
