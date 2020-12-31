import json
from typing import Iterator

from aws_session_recorder.lib.schema.user import User

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.policy import Policy, PolicyVersion
from tests.test_base import *


# TODO: Test attachments
def test_policy(session, policy: t.GetPolicyResponseTypeDef):
    policy = policy['Policy']
    for key, value in policy.items():
        # TODO: Look into why the db records 0 instead of 1 here
        if key == 'AttachmentCount':
            continue
        assert value == getattr(session.db.query(Policy).all()[0], key)


@pytest.fixture(scope='function')
def list_policies(session: Session, iam: IAMClient) -> t.ListPoliciesResponseTypeDef:
    assert 0 == session.db.query(Policy).count()
    iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy_doc)
    iam.create_policy(PolicyName='test_policy2', PolicyDocument=test_policy_doc)
    return iam.list_policies(Scope='Local')


def test_list_policies(session: Session, list_policies: t.ListPoliciesResponseTypeDef):
    assert len(list_policies['Policies']) == session.db.query(Policy).count()
    assert len(list_policies['Policies']) == 2


@pytest.fixture(scope='function')
def policy_version(iam: IAMClient, policy: t.GetPolicyResponseTypeDef) -> t.GetPolicyVersionResponseTypeDef:
    policy_arn = policy['Policy']['Arn']
    resp: t.ListPolicyVersionsResponseTypeDef = iam.list_policy_versions(PolicyArn=policy_arn)
    first_version = resp['Versions'][0]['VersionId']
    return iam.get_policy_version(PolicyArn=policy_arn, VersionId=first_version)


def test_policy_version(session: Session, policy_version: t.GetPolicyVersionResponseTypeDef):
    assert policy_version['PolicyVersion']['VersionId'] == session.db.query(PolicyVersion).first().VersionId


@pytest.fixture(scope='function')
def user_attachment(iam: IAMClient, user: t.GetUserResponseTypeDef, policy: t.GetPolicyResponseTypeDef) -> t.ListAttachedUserPoliciesResponseTypeDef:
    iam.attach_user_policy(UserName=user['User']['UserName'], PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_user_policies(UserName=user['User']['UserName'])


def test_user_attachment(session: Session, user_attachment: t.ListAttachedUserPoliciesResponseTypeDef):
    assert user_attachment['AttachedPolicies'][0]['PolicyArn'] == session.db.query(User).first().attached_policies[0].PolicyArn

@pytest.fixture(scope='function')
def user_attachment_no_user(session: Session, iam: IAMClient, policy: t.GetPolicyResponseTypeDef) -> t.ListAttachedUserPoliciesResponseTypeDef:
    assert session.db.query(User).count() == 0
    iam.create_user(UserName=user_name)  # Don't list/get this so it doesn't show up in the db
    iam.attach_user_policy(UserName=user_name, PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_user_policies(UserName=user_name)


# Haven't been able to get the User to get created when we only have the UserName, the table should link back to the
# right user if it's retrieved some other way though.
#
# def test_user_attachment_no_user_by_user(session: Session, user_attachment_no_user: t.ListAttachedUserPoliciesResponseTypeDef):
#     assert user_attachment_no_user['AttachedPolicies'][0]['PolicyArn'] == session.db.query(User).first().attached_policies[0].PolicyArn


def test_user_attachment_no_user_by_policy(session: Session, user_attachment_no_user: t.ListAttachedUserPoliciesResponseTypeDef):
    assert user_attachment_no_user['AttachedPolicies'][0]['PolicyArn'] == session.db.query(Policy).first().attached_to_users[0].PolicyArn
