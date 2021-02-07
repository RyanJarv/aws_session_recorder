import pytest
import typing

from aws_session_recorder.lib.schema.group import Group
from aws_session_recorder.lib.schema.role import Role
from aws_session_recorder.lib.schema.user import User
from tests.test_base import test_policy_doc, role_name, group_name, user_name

# These are used by pytest
from tests.test_base import session, user, iam, policy, group, role  # noqa: F401

if typing.TYPE_CHECKING:
    from mypy_boto3_iam.client import IAMClient  # type: ignore
    from mypy_boto3_iam import type_defs as t  # type: ignore

from aws_session_recorder.lib.session import Session

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.policy import Policy, PolicyVersion


# TODO: Test attachments
def test_policy(session, policy: 't.GetPolicyResponseTypeDef'):
    policy = policy['Policy']
    for key, value in policy.items():
        # TODO: Look into why the db records 0 instead of 1 here
        if key == 'AttachmentCount':
            continue
        assert value == getattr(session.db.query(Policy).all()[0], key)


@pytest.fixture(scope='function')
def list_policies(session: Session, iam: 'IAMClient') -> 't.ListPoliciesResponseTypeDef':
    assert 0 == session.db.query(Policy).count()
    iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy_doc)
    iam.create_policy(PolicyName='test_policy2', PolicyDocument=test_policy_doc)
    return iam.list_policies(Scope='Local')


def test_list_policies(session: Session, list_policies: 't.ListPoliciesResponseTypeDef'):
    assert len(list_policies['Policies']) == session.db.query(Policy).count()
    assert len(list_policies['Policies']) == 2


@pytest.fixture(scope='function')
def policy_version(iam: 'IAMClient', policy: 't.GetPolicyResponseTypeDef') -> 't.GetPolicyVersionResponseTypeDef':
    policy_arn = policy['Policy']['Arn']
    resp: t.ListPolicyVersionsResponseTypeDef = iam.list_policy_versions(PolicyArn=policy_arn)
    first_version = resp['Versions'][0]['VersionId']
    return iam.get_policy_version(PolicyArn=policy_arn, VersionId=first_version)


def test_policy_version(session: Session, policy_version: 't.GetPolicyVersionResponseTypeDef'):
    assert policy_version['PolicyVersion']['VersionId'] == session.db.query(PolicyVersion).first().VersionId


@pytest.fixture(scope='function')
def user_attachment(iam: 'IAMClient', user: 't.GetUserResponseTypeDef',
                    policy: 't.GetPolicyResponseTypeDef') -> 't.ListAttachedUserPoliciesResponseTypeDef':
    iam.attach_user_policy(UserName=user['User']['UserName'], PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_user_policies(UserName=user['User']['UserName'])


def test_user_attachment(session: Session, user_attachment: 't.ListAttachedUserPoliciesResponseTypeDef'):
    assert user_attachment['AttachedPolicies'][0]['PolicyArn'] == session.db.query(User).first().attached_policies[0].PolicyArn


@pytest.fixture(scope='function')
def user_attachment_no_user(session: Session, iam: 'IAMClient',
                            policy: 't.GetPolicyResponseTypeDef') -> 't.ListAttachedUserPoliciesResponseTypeDef':
    iam.create_user(UserName=user_name)  # Don't list/get this so it doesn't show up in the db
    iam.attach_user_policy(UserName=user_name, PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_user_policies(UserName=user_name)


# Haven't been able to get the User to get created when we only have the UserName, the table should link back to the
# right user if it's retrieved some other way though.
#
# def test_user_attachment_no_user_by_user(session: Session, user_attachment_no_user: 't.ListAttachedUserPoliciesResponseTypeDef'):
#     assert user_attachment_no_user['AttachedPolicies'][0]['PolicyArn'] == session.db.query(User).first().attached_policies[0].PolicyArn


def test_user_attachment_no_user_by_policy(session: Session,
                                           user_attachment_no_user: 't.ListAttachedUserPoliciesResponseTypeDef'):
    assert user_attachment_no_user['AttachedPolicies'][0]['PolicyArn'] == session.db.query(Policy).first().attached_to_users[
        0].PolicyArn


@pytest.fixture(scope='function')
def role_attachment(iam: 'IAMClient', role: 't.GetRoleResponseTypeDef',
                    policy: 't.GetPolicyResponseTypeDef') -> 't.ListAttachedRolePoliciesResponseTypeDef':
    iam.attach_role_policy(RoleName=role['Role']['RoleName'], PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_role_policies(RoleName=role['Role']['RoleName'])


def test_role_attachment(session: Session, role_attachment: 't.ListAttachedRolePoliciesResponseTypeDef'):
    assert role_attachment['AttachedPolicies'][0]['PolicyArn'] == session.db.query(Role).first().attached_policies[0].PolicyArn


@pytest.fixture(scope='function')
def role_attachment_no_role(
    session: Session,
    iam: 'IAMClient',
    policy: 't.GetPolicyResponseTypeDef'
) -> 't.ListAttachedRolePoliciesResponseTypeDef':
    # Don't list/get this so it doesn't show up in the db
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=test_policy_doc
    )
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_role_policies(RoleName=role_name)


def test_role_attachment_no_role_by_policy(session: Session,
                                           role_attachment_no_role: 't.ListAttachedRolePoliciesResponseTypeDef'):
    assert role_attachment_no_role['AttachedPolicies'][0]['PolicyArn'] == session.db.query(Policy).first().attached_to_roles[
        0].PolicyArn


@pytest.fixture(scope='function')
def group_attachment(
    iam: 'IAMClient', group: 't.GetUserResponseTypeDef',
    policy: 't.GetPolicyResponseTypeDef'
) -> 't.ListAttachedGroupPoliciesResponseTypeDef':
    iam.attach_group_policy(GroupName=group['Group']['GroupName'], PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_group_policies(GroupName=group['Group']['GroupName'])


def test_group_attachment(session: Session, group_attachment: 't.ListAttachedGroupPoliciesResponseTypeDef'):
    assert group_attachment['AttachedPolicies'][0]['PolicyArn'] == session.db.query(Group).first().attached_policies[
        0].PolicyArn


@pytest.fixture(scope='function')
def group_attachment_no_group(session: Session, iam: 'IAMClient',
                              policy: 't.GetPolicyResponseTypeDef') -> 't.ListAttachedGroupPoliciesResponseTypeDef':
    iam.create_group(GroupName=group_name)  # Don't list/get this so it doesn't show up in the db
    iam.attach_group_policy(GroupName=group_name, PolicyArn=policy['Policy']['Arn'])
    return iam.list_attached_group_policies(GroupName=group_name)


def test_group_attachment_no_group_by_policy(session: Session,
                                             group_attachment_no_group: 't.ListAttachedGroupPoliciesResponseTypeDef'):
    assert group_attachment_no_group['AttachedPolicies'][0]['PolicyArn'] == \
           session.db.query(Policy).first().attached_to_groups[0].PolicyArn
