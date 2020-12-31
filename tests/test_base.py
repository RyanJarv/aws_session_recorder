#!/usr/bin/env python

"""Tests for `aws_session_recorder` package."""
from typing import Iterator

import pytest  # type: ignore
from moto import mock_iam # type: ignore
from mypy_boto3_iam.client import IAMClient  # type: ignore
from mypy_boto3_iam import type_defs as t  # type: ignore

from aws_session_recorder.lib.session import Session

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


@pytest.fixture(scope='function')
def role(iam) -> t.GetRoleResponseTypeDef:
    iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=test_policy)
    return iam.get_role(RoleName=role_name)


@pytest.fixture(scope='function')
def group(iam, user: t.GetUserResponseTypeDef) -> t.GetGroupResponseTypeDef:
    resp = iam.create_group(GroupName=group_name)
    iam.add_user_to_group(UserName=user['User']['UserName'], GroupName=resp['Group']['GroupName'])
    return iam.get_group(GroupName=group_name)


@pytest.fixture(scope='function')
def instance_profile(iam: IAMClient) -> t.GetInstanceProfileResponseTypeDef:
    resp = iam.create_instance_profile(InstanceProfileName='test_instance_profile')
    return iam.get_instance_profile(InstanceProfileName=resp['InstanceProfile']['InstanceProfileName'])

@pytest.fixture(scope='function')
def policy(iam: IAMClient) -> t.GetPolicyResponseTypeDef:
    resp = iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_policy(PolicyArn=resp['Policy']['Arn'])
