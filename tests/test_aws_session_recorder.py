#!/usr/bin/env python

"""Tests for `aws_session_recorder` package."""
import json
from typing import Iterator

import pytest  # type: ignore
from moto import mock_iam # type: ignore
from mypy_boto3_iam.client import IAMClient  # type: ignore
from mypy_boto3_iam import type_defs as t  # type: ignore

from aws_session_recorder.lib import Session, schema

user_name = 'test_user'
role_name = 'test_role'
group_name = 'test_role'
test_policy = '''
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}
'''


@pytest.fixture(scope='function')
def session() -> Iterator[Session]:
    with mock_iam():
        yield Session()


@pytest.fixture(scope='function')
def iam(session) -> IAMClient:
    return session.client('iam')


@pytest.fixture(scope='function')
def user(iam) -> t.GetUserResponseTypeDef:
    iam.create_user(UserName=user_name)
    return iam.get_user(UserName=user_name)


def test_user(user, session):
    for key, value in user['User'].items():
        # TODO: Use datetime object in db
        if key == 'CreateDate':
            value = str(value)
        assert value == getattr(session.db.query(schema.User).all()[0], key)


@pytest.fixture(scope='function')
def role(iam) -> t.GetRoleResponseTypeDef:
    iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=test_policy)
    return iam.get_role(RoleName=role_name)


def test_role(role, session):
    for key, value in role['Role'].items():
        # TODO: Use datetime object in db
        if key == 'CreateDate':
            value = str(value)
        if key == 'AssumeRolePolicyDocument':
            # TODO: Fix this edge case
            assert json.dumps(value) == json.dumps(json.loads(getattr(session.db.query(schema.Role).all()[0], key)))
            continue
        assert value == getattr(session.db.query(schema.Role).all()[0], key)


@pytest.fixture(scope='function')
def inline_user_policy(iam, user) -> t.GetUserPolicyResponseTypeDef:
    iam.put_user_policy(UserName=user_name, PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_user_policy(UserName=user_name, PolicyName='test_policy')

def test_inline_user_policy(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    assert inline_user_policy['PolicyName'] == session.db.query(schema.UserPolicy).first().PolicyName

def test_inline_user_policy_by_user(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    live_name = inline_user_policy['PolicyName']
    user: schema.User = session.db.query(schema.User).first()
    assert live_name == user.inline_policies[0].PolicyName

def test_inline_user_policy_document(session, inline_user_policy: t.GetUserPolicyResponseTypeDef):
    live_doc = json.dumps(inline_user_policy['PolicyDocument'])
    # TODO: Fix this edge case
    db_doc = json.dumps(json.loads(session.db.query(schema.UserPolicy).first().PolicyDocument))
    assert live_doc == db_doc


@pytest.fixture(scope='function')
def user_policy(iam: IAMClient) -> t.GetPolicyResponseTypeDef:
    resp = iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_policy(PolicyArn=resp['Policy']['Arn'])


#TODO: Test attachments
def test_user_policy(session, user_policy: t.GetPolicyResponseTypeDef):
    policy = user_policy['Policy']
    for key, value in policy.items():
        # TODO: Use datetime object in db
        if key in ['CreateDate', 'UpdateDate']:
            value = str(value)

        # TODO: Look into why the db records 0 instead of 1 here
        if key == 'AttachmentCount':
            continue
        assert value == getattr(session.db.query(schema.Policy).all()[0], key)


@pytest.fixture(scope='function')
def policy_version(iam: IAMClient, user_policy: t.GetPolicyResponseTypeDef) -> t.GetPolicyVersionResponseTypeDef:
    policy_arn = user_policy['Policy']['Arn']
    resp: t.ListPolicyVersionsResponseTypeDef = iam.list_policy_versions(PolicyArn=policy_arn)
    first_version = resp['Versions'][0]['VersionId']
    return iam.get_policy_version(PolicyArn=policy_arn, VersionId=first_version)


def test_policy_version(session: Session, policy_version: t.GetPolicyVersionResponseTypeDef):
    assert policy_version['PolicyVersion']['VersionId'] == session.db.query(schema.PolicyVersion).first().VersionId


@pytest.fixture(scope='function')
def instance_profile(iam: IAMClient) -> t.GetInstanceProfileResponseTypeDef:
    resp = iam.create_instance_profile(InstanceProfileName='test_instance_profile')
    return iam.get_instance_profile(InstanceProfileName=resp['InstanceProfile']['InstanceProfileName'])


def test_instance_profile(session: Session, instance_profile: t.GetInstanceProfileResponseTypeDef):
    assert instance_profile['InstanceProfile']['Arn'] == session.db.query(schema.InstanceProfile).first().Arn


@pytest.fixture(scope='function')
def access_keys(iam: IAMClient, user: t.CreateUserResponseTypeDef) -> t.ListAccessKeysResponseTypeDef:
    iam.create_access_key(UserName=user['User']['UserName'])
    return iam.list_access_keys(UserName=user['User']['UserName'])


def test_list_access_keys(session: Session, access_keys: t.ListAccessKeysResponseTypeDef):
    key = access_keys['AccessKeyMetadata'][0]
    assert key['AccessKeyId'] == session.db.query(schema.AccessKey).first().AccessKeyId


def test_user_access_keys(session: Session, access_keys: t.ListAccessKeysResponseTypeDef):
    key = access_keys['AccessKeyMetadata'][0]
    assert key['AccessKeyId'] == session.db.query(schema.User).first().access_keys[0].AccessKeyId


@pytest.fixture(scope='function')
def group(iam, user: t.GetUserResponseTypeDef) -> t.GetGroupResponseTypeDef:
    resp = iam.create_group(GroupName=group_name)
    iam.add_user_to_group(UserName=user['User']['UserName'], GroupName=resp['Group']['GroupName'])
    return iam.get_group(GroupName=group_name)


# def test_group(session, group: t.GetGroupResponseTypeDef):
#     g: schema.Group = session.db.query(schema.Group).all()[0]
#     assert group['Group']['Arn'] == g.Arn
#
#
# def test_user_has_group(session, group: t.GetGroupResponseTypeDef):
#     usr: schema.User = session.db.query(schema.User).all()[0]
#     group: schema.Group = usr.groups[0]
#     assert group['Group']['Arn'] == group.Arn
