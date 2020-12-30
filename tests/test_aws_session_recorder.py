#!/usr/bin/env python

"""Tests for `aws_session_recorder` package."""
import json
from typing import Iterator

import pytest
from moto import mock_iam
from mypy_boto3_iam.client import IAMClient
from mypy_boto3_iam.type_defs import *

from aws_session_recorder.lib import Session, schema

user_name = 'test_user'
role_name = 'test_role'
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
def user(iam) -> GetUserResponseTypeDef:
    iam.create_user(UserName=user_name)
    return iam.get_user(UserName=user_name)


def test_user(user, session):
    for key, value in user['User'].items():
        # TODO: Use datetime object in db
        if key == 'CreateDate':
            value = str(value)
        assert value == getattr(session.db.query(schema.User).all()[0], key)


@pytest.fixture(scope='function')
def role(iam) -> GetRoleResponseTypeDef:
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
def inline_user_policy(iam, user) -> GetUserPolicyResponseTypeDef:
    iam.put_user_policy(UserName=user_name, PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_user_policy(UserName=user_name, PolicyName='test_policy')


def test_inline_user_policy(inline_user_policy: GetUserPolicyResponseTypeDef, session):
    for key, value in inline_user_policy.items():
        if key == 'PolicyDocument':
            # TODO: Fix this edge case
            assert json.dumps(value) == json.dumps(json.loads(getattr(session.db.query(schema.InlinePolicy).all()[0], key)))
            continue
        assert value == getattr(session.db.query(schema.InlinePolicy).all()[0], key)


@pytest.fixture(scope='function')
def user_policy(iam: IAMClient) -> GetPolicyResponseTypeDef:
    resp = iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_policy(PolicyArn=resp['Policy']['Arn'])


#TODO: Test attachments
def test_user_policy(session, user_policy: GetPolicyResponseTypeDef):
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
def policy_version(iam: IAMClient, user_policy: GetPolicyResponseTypeDef) -> GetPolicyVersionResponseTypeDef:
    policy_arn = user_policy['Policy']['Arn']
    resp: ListPolicyVersionsResponseTypeDef = iam.list_policy_versions(PolicyArn=policy_arn)
    first_version = resp['Versions'][0]['VersionId']
    return iam.get_policy_version(PolicyArn=policy_arn, VersionId=first_version)


def test_policy_version(session: Session, policy_version: GetPolicyVersionResponseTypeDef):
    assert policy_version['PolicyVersion']['VersionId'] == session.db.query(schema.PolicyVersion).first().VersionId


@pytest.fixture(scope='function')
def instance_profile(iam: IAMClient) -> GetInstanceProfileResponseTypeDef:
    resp = iam.create_instance_profile(InstanceProfileName='test_instance_profile')
    return iam.get_instance_profile(InstanceProfileName=resp['InstanceProfile']['InstanceProfileName'])


def test_instance_profile(session: Session, instance_profile: GetInstanceProfileResponseTypeDef):
    assert instance_profile['InstanceProfile']['Arn'] == session.db.query(schema.InstanceProfile).first().Arn
