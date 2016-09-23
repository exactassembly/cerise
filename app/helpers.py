from bson.objectid import ObjectId
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from .user.models import User
from .group.models import Group
import boto3

def flash_errors(formErrors):
    for field, errors in formErrors:
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

def verify_aws(awsID, awsKey):
    client = boto3.client(
        'iam',
        aws_access_key_id=ID,
        aws_secret_access_key=awsKey
    )
    try:
        client.get_user()
        return True
    except ClientError:
        return False

def load_group(current_user, group):
    if current_user.self_group.id == group:
        return current_user.self_group
    elif ObjectId(current_user.id) in Group.objects.get(id=group):
        return Group.objects.get(id=group)
    else:
        raise ValueError('User does not have access to group.')                          

def register_user(form):
    user = User(username=form.username.data, email=form.email.data)
    user.password = generate_password_hash(form.password.data, method='pbkdf2:sha1', salt_length=16)
    if form.group.data and form.ref.data:
        user.type = 'unpaid'
        add_to_group(user, form.group.data, form.ref.data)
    else:
        group = Group(name=form.username.data)
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
