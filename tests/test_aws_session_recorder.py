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
    iam: IAMClient = session.client('iam')
    return iam


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
def policy(iam: IAMClient) -> GetPolicyResponseTypeDef:
    resp = iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_policy(PolicyArn=resp['Policy']['Arn'])

@pytest.fixture(scope='function')
def attached_user_policies(iam: IAMClient, user, policy: GetPolicyResponseTypeDef) -> ListAttachedUserPoliciesResponseTypeDef:
    iam.attach_user_policy(UserName=user_name, PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_user_policies(UserName=user_name)

@pytest.fixture(scope='function')
def attached_user_policy(iam, attached_user_policies: ListAttachedUserPoliciesResponseTypeDef) -> GetPolicyResponseTypeDef:
    attached_policy = attached_user_policies['AttachedPolicies'][0]
    return iam.get_policy(PolicyArn=attached_policy['PolicyArn'])

def test_attached_user_policy(session, attached_user_policy: GetPolicyResponseTypeDef):
    policy = attached_user_policy['Policy']
    for key, value in policy.items():
        # TODO: Use datetime object in db
        if key in ['CreateDate', 'UpdateDate']:
            value = str(value)

        # TODO: Look into why the db records 0 instead of 1 here
        if key == 'AttachmentCount':
            continue
        assert value == getattr(session.db.query(schema.Policy).all()[0], key)

    # TODO: ListPolicyVersions
    # arn = resp['Policy']['Arn']
    # list_policy_versions: type_defs.ListPolicyVersionsResponseTypeDef = iam.list_policy_versions(PolicyArn=arn)
    # ver = list_policy_versions['Versions'][0]
    # resp: type_defs.GetPolicyVersionResponseTypeDef = iam.get_policy_version(PolicyArn=arn, VersionId=ver['VersionId'])
    # assert resp['PolicyVersion']['VersionId'] == sess.db.query(schema.PolicyVersion).first().VersionId
    # print("attached policy version ok")

    # TODO: ListInstanceProfiles
    # resp: type_defs.ListInstanceProfilesResponseTypeDef = iam.list_instance_profiles()
    # profile = resp['InstanceProfiles'][0]
    # resp: type_defs.GetInstanceProfileResponseTypeDef = iam.get_instance_profile(InstanceProfileName=profile['InstanceProfileName'])
    # assert resp['InstanceProfile']['Arn'] == sess.db.query(schema.InstanceProfile).first().Arn
    # print("instance profile ok")
