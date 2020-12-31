import datetime
import json

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.user import User, AccessKey, UserPolicy
from tests.test_base import *

user_name2 = user_name+"2"


def test_user(user, session):
    for key, value in user['User'].items():
        assert value == getattr(session.db.query(User).all()[0], key)


@pytest.fixture(scope='function')
def user2(iam) -> t.GetUserResponseTypeDef:
    iam.create_user(UserName=user_name2)
    return iam.get_user(UserName=user_name2)


def test_user2(session: Session, user: t.GetUserResponseTypeDef, user2: t.GetUserResponseTypeDef):
    assert session.db.query(User).count() == 2
    assert user_name == session.db.query(User).all()[0].UserName
    assert user_name2 == session.db.query(User).all()[1].UserName


@pytest.fixture(scope='function')
def list_users(session: Session, iam: IAMClient) -> t.ListUsersResponseTypeDef:
    assert 0 == session.db.query(User).count()
    iam.create_user(UserName=user_name)
    iam.create_user(UserName=user_name2)
    return iam.list_users()


def test_list_users(session: Session, list_users: t.ListUsersResponseTypeDef):
    assert len(list_users['Users']) == session.db.query(User).count()
    assert len(list_users['Users']) == 2


@pytest.fixture(scope='function')
def inline_user_policy(iam: IAMClient, user: t.GetUserResponseTypeDef) -> t.GetUserPolicyResponseTypeDef:
    iam.put_user_policy(UserName=user_name, PolicyName='test_policy', PolicyDocument=test_policy_doc)
    return iam.get_user_policy(UserName=user_name, PolicyName='test_policy')


def test_inline_user_policy(session: Session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    assert inline_user_policy['PolicyName'] == session.db.query(UserPolicy).first().PolicyName


def test_inline_user_policy_by_user(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    live_name = inline_user_policy['PolicyName']
    user: User = session.db.query(User).first()
    assert live_name == user.inline_policies[0].PolicyName


@pytest.fixture(scope='function')
def inline_user_policy_list(iam: IAMClient, user: t.GetUserResponseTypeDef) -> t.ListUserPoliciesResponseTypeDef:
    iam.put_user_policy(UserName=user_name, PolicyName='test_policy', PolicyDocument=test_policy_doc)
    return iam.list_user_policies(UserName=user_name)


def test_inline_user_policy_list(session: Session, inline_user_policy_list: t.ListUserPoliciesResponseTypeDef):
    assert inline_user_policy_list['PolicyNames'][0] == session.db.query(UserPolicy).first().PolicyName


def test_inline_user_policy_list_by_user(session: Session, inline_user_policy_list: t.ListUserPoliciesResponseTypeDef):
    live_name = inline_user_policy_list['PolicyNames'][0]
    user: User = session.db.query(User).first()
    assert live_name == user.inline_policies[0].PolicyName

# Listing updates the record but doesn't have a PolicyDocument associated with it, so make sure we don't delete the
# one that already exists with GetUserPolicy.
def test_inline_user_policy_get_then_list(session: Session, inline_user_policy: t.GetUserPolicyResponseTypeDef, inline_user_policy_list: t.ListUserPoliciesResponseTypeDef):
    #TODO: Return hash with UserPolicy.PolicyDocument
    assert inline_user_policy['PolicyDocument'] == json.loads(session.db.query(UserPolicy).first().PolicyDocument)


def test_inline_user_policy_document(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    live_doc = json.dumps(inline_user_policy['PolicyDocument'])
    # TODO: Fix this edge case
    db_doc = json.dumps(json.loads(session.db.query(UserPolicy).first().PolicyDocument))
    assert live_doc == db_doc


@pytest.fixture(scope='function')
def access_keys(iam: IAMClient, user: t.CreateUserResponseTypeDef) -> t.ListAccessKeysResponseTypeDef:
    iam.create_access_key(UserName=user['User']['UserName'])
    return iam.list_access_keys(UserName=user['User']['UserName'])


def test_list_access_keys(session: Session, access_keys: t.ListAccessKeysResponseTypeDef):
    key = access_keys['AccessKeyMetadata'][0]
    assert key['AccessKeyId'] == session.db.query(AccessKey).first().AccessKeyId


def test_user_access_keys(session: Session, access_keys: t.ListAccessKeysResponseTypeDef):
    key = access_keys['AccessKeyMetadata'][0]
    assert key['AccessKeyId'] == session.db.query(User).first().access_keys[0].AccessKeyId
