import json

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.user import User, AccessKey, UserPolicy
from tests.test_base import *


def test_user(user, session):
    for key, value in user['User'].items():
        # TODO: Use datetime object in db
        if key == 'CreateDate':
            value = str(value)
        assert value == getattr(session.db.query(User).all()[0], key)


@pytest.fixture(scope='function')
def inline_user_policy(iam, user) -> t.GetUserPolicyResponseTypeDef:
    iam.put_user_policy(UserName=user_name, PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_user_policy(UserName=user_name, PolicyName='test_policy')


def test_inline_user_policy(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    assert inline_user_policy['PolicyName'] == session.db.query(UserPolicy).first().PolicyName


def test_inline_user_policy_by_user(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    live_name = inline_user_policy['PolicyName']
    user: User = session.db.query(User).first()
    assert live_name == user.inline_policies[0].PolicyName


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
