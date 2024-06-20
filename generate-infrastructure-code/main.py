import cfnresponse
import json
import os
import random
import re
import requests
import traceback
import string

from aws_helper import get_secret_value, assume_role, get_account_alias
from file_management import copy_module, delete_dir
from terraform_helper import search_workspaces, create_workspace, search_terraform_teams, create_terraform_team, add_workspace_team_access, search_team_workspace_access
from requests import exceptions

# AWS API Lambda Layers
from common.custom_logging import CustomLogger

# GitHub API Lambda Layer
# Repository Management helpers
from git_helper import clone, check_team_permissions_for_repository, update_team_repository_permissions
# Code Management helpers
from git_helper import existing_pull_request, create_pull_request, merge_pull_request
# User Management Helpers
from git_helper import search_teams, search_user_team_membership, add_user_to_team, search_repositories, create_repository, create_team

logger = CustomLogger().logger

github_endpoint = os.environ['GITHUB_ENDPOINT']
github_organization = os.environ['GITHUB_ORGANIZATION']
default_github_teams = {
    "Admin": "admin",
    "Application": "maintain",
    "Infrastructure": "maintain",
    "Migration": "triage",
    "ViewOnly": "pull",
}
global_github_teams = {
    "Cloud-Engineering": "admin",
    "Cloud-Operations": "maintain",
    "Landing-Zone": "admin",
    "Migration-Execution": "push"
}

terraform_endpoint = os.environ['TERRAFORM_ENDPOINT']
terraform_organization = os.environ['TERRAFORM_ORGANIZATION']
default_terraform_teams = {
    "Admin": "admin",
    "Infrastructure": "write",
    "Migration": "write",
    "ViewOnly": "read",
}
global_terraform_teams = {
    "Cloud-Engineering": "admin",
    "Cloud-Operations": "write",
    "Landing-Zone": "admin",
    "Migration-Execution": "read"
}

shared_lambda_action_role = os.environ['SHARED_LAMBA_ACTION_ROLE']
environment_abbreviation = {
    "development": "dev",
    "test": "tst",
    "production": "prd"
}


def lambda_handler(event, context):
    logger.debug(json.dumps(event))

    current_account_id = context.invoked_function_arn.split(":")[4]
    response_data = dict()

    if event['RequestType'] == "Delete":
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, "CustomResourcePhysicalID")
        return

    # TODO: Check to see if it is a rollback...

    base_path = "/tmp/migration"
    response_data = dict()

    source_repository_owner = "OneTakedaChina"
    source_repository_name = "ecs-cn-cloud-foundation-service-catalog-modules"

    source_repository_path = f"{base_path}/source/{source_repository_name}"

    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    # Get request parameters
    try: 
        request_parameters = event['ResourceProperties']['Parameters']['FindAndReplace']

        stack_arn = event['StackId']
        request_parameters['cloudformation_stack_arn'] = stack_arn

        stack_id = stack_arn.split("/")[1]
        provisioned_product_id = stack_id.split("-")[-2]
        request_parameters['provisioned_product_id'] = provisioned_product_id
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = f"Requests parameter {str(e)} was not provided"
        
        logger.debug(f"ErrorCode: {exception_metadata['ErrorCode']} Error: {e}")
        logger.error(exception_metadata['Message'])

        response_data['ErrorCode'] = exception_metadata['Error']
        response_data['ErrorMessage'] = str(exception_metadata['Message'])

        cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")

        delete_dir(base_path)
        return {'statusCode': exception_metadata['ErrorCode'], 'body': json.dumps({'Message': exception_metadata['Message']})}

    replacement_values = request_parameters
    logger.debug(f"Jinja Replacement Values: {replacement_values}")

    # Setting variables from event
    try:
        apms_id = request_parameters['apms_id']

        application_name = request_parameters['application_name']
        entity_name = request_parameters['entity_name']
        environment = request_parameters['environment'].lower()
        env = environment_abbreviation[environment]

        if not entity_name:
            logger.warn("Empty string provided for `entity_name`...")
            entity_name = random_entity_name()
            logger.warn(f"Randomly generated `{entity_name}` for entity name")

        account_id = event['ResourceProperties']['Parameters']['AccountId']
        provisioner = event['ResourceProperties']['Parameters']['Provisioner'].lower()
        module_name = event['ResourceProperties']['Parameters']['ResourceType'].lower()
        service_provider = event['ResourceProperties']['Parameters']['ServiceProvider']
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = f"Parameter {e} was not provided"

        logger.debug(f"ErrorCode: {exception_metadata['ErrorCode']} Error: {e}")
        logger.error(exception_metadata['Message'])

        response_data['ErrorCode'] = exception_metadata['Error']
        response_data['ErrorMessage'] = str(exception_metadata['Message'])

        cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")

        delete_dir(base_path)

        return {'statusCode': exception_metadata['ErrorCode'], 'body': json.dumps({'Message': exception_metadata['Message']})}

    logger.info(f"APMS ID: {apms_id}  Entity Name: {entity_name}  Provisioner: {provisioner}  Resource Type: {module_name}")

    # Organizations API calls
    # TODO: Push to OrgUnitMetadata
    try:
        # Role assumption to the jump role which enables access to TECCN organization master account
        logger.info("Creating Fuji-Cloud-Engineering-Lambda-Action-Role session")
        shared_lambda_action_session = assume_role(current_account_id, shared_lambda_action_role)

        logger.info("Creating organization master session")
        master_account_session = assume_role("447869545964", "OrganizationReadOnly", shared_lambda_action_session)

        account_alias = get_account_alias(account_id, master_account_session)

        if account_alias is None:
            exception_metadata = dict()
            exception_metadata['Error'] = "Unable to identify account alias"
            exception_metadata['ErrorCode'] = 400
            exception_metadata['Message'] = "Unable to identify account alias"

            raise Exception(exception_metadata)
        else:
            account_alias = "-".join(account_alias.split("-")[0:3])

        project_name = f"{account_alias}-{apms_id.split('-')[-1]}"
        logger.debug(f"Project Name: {project_name}")

        # GitHub Credentials
        logger.info(f"Fetching secret for GitHub Enterprise...")
        github_api_token = get_secret_value("/takeda/cn/github/service_account")

        # Source Repository management
        logger.info(f"Cloning source repository ({source_repository_owner}/{source_repository_name})...")
        clone(source_repository_owner, source_repository_name, source_repository_path, github_api_token)

        # GitHub teams management
        logger.info("Creating default GitHub Enterprise teams")
        github_parent_team_id, github_parent_team_slug = search_teams(source_repository_owner, project_name, github_api_token)
    
        if github_parent_team_slug is None:
            maintainer_list = ['svc-servicecatalog']
            github_parent_team_id, github_parent_team_slug = create_team(source_repository_owner, project_name, maintainer_list, github_api_token, parent_team_id=None)
        else: 
            add_user_to_team(source_repository_owner, github_parent_team_slug, "svc-servicecatalog", github_api_token, "maintainer")

        response_data['GitHubParentTeamName'] = github_parent_team_slug
        
        for team in default_github_teams:
            github_team_name = f"{project_name}-{team}"

            # Create GitHub team if does not exist
            github_team_id, github_team_slug = search_teams(source_repository_owner, github_team_name, github_api_token)
    
            if github_team_slug is None:
                maintainer_list = ['svc-servicecatalog']
                github_team_id, github_team_slug = create_team(source_repository_owner, github_team_name, maintainer_list, github_api_token, github_parent_team_id)
            else: 
                membership = search_user_team_membership(source_repository_owner, "svc-servicecatalog", github_team_slug, github_api_token)

            service_catalog_output_name = f"GitHub{team}TeamName"
            response_data[service_catalog_output_name] = github_team_slug

        # Project repository Configuration
        # Search for existing GitHub repository for the project
        project_repository_full_name = search_repositories(source_repository_owner, project_name, github_api_token)

        # Create the repository if it does not exist
        if project_repository_full_name is None:
            project_repository_full_name = create_repository(source_repository_owner, project_name, github_api_token)

        # Assign results of repository search to common variable
        existing_permissions = check_team_permissions_for_repository(source_repository_owner, github_parent_team_slug, project_name, "pull", github_api_token)
        
        if not existing_permissions:
            update_team_repository_permissions(source_repository_owner, project_name, github_parent_team_slug, "pull", github_api_token)

        logger.info(f"Granting application teams access to GitHub repository.")
        for team in default_github_teams:
            github_team_name = f"{project_name}-{team}"

            # Assign results of repository search to common variable
            existing_permissions = check_team_permissions_for_repository(source_repository_owner, github_team_name, project_name, default_github_teams[team], github_api_token)

            if not existing_permissions:
                update_team_repository_permissions(source_repository_owner, project_name, github_team_name, default_github_teams[team], github_api_token)

        logger.info(f"Granting support teams access to GitHub repository.")
        for team in global_github_teams:
            # Assign results of repository search to common variable
            existing_permissions = check_team_permissions_for_repository(source_repository_owner, team, project_name, global_github_teams[team], github_api_token)

            if not existing_permissions:
                update_team_repository_permissions(source_repository_owner, project_name, team, global_github_teams[team], github_api_token)

        response_data['GitHubRepositoryName'] = project_repository_full_name
        response_data['GitHubRepositoryCloneUrl'] = f"https://{github_endpoint}/{project_repository_full_name}.git"
        response_data['GitHubRepositoryUrl'] = f"https://{github_endpoint}/{project_repository_full_name}"

        # Clone project repository
        repository_path = f"{base_path}/{project_name}"

        logger.info("Cloning project repository...")
        destintion_repository = clone(source_repository_owner, project_repository_full_name, repository_path, github_api_token)

        # Copy code
        project_repository_path = f"{base_path}/{project_name}/{env}"

        # Create branch
        # Copy code
        # Push
        pull_request_branch_name = copy_module(destintion_repository, source_repository_path, project_repository_path, entity_name, provisioner, module_name, replacement_values)
        logger.debug(f"Pull request branch: {pull_request_branch_name}")

        if pull_request_branch_name is not None:
            pull_request_url = existing_pull_request(source_repository_owner, project_repository_full_name, pull_request_branch_name, github_api_token)

            if not pull_request_url:
                pull_request_url = create_pull_request(source_repository_owner, project_repository_full_name, pull_request_branch_name, github_api_token)

            logger.info(pull_request_url)

            merge_pull_request(pull_request_url, "squash", github_api_token)
            message = f"Code for {entity_name} merged to {project_repository_full_name}"
        else: 
            message = f"No code to merge to {project_repository_full_name} for {entity_name}"

        # Terraform creds
        logger.info(f"Fetching secret for Terraform Enterprise...")
        terraform_api_token = get_secret_value("/takeda/cn/terraform/api_token")

        # Terraform workspace
        workspace_name = f"{project_name}-{env}"
        workspace_id = search_workspaces(terraform_organization, workspace_name, terraform_api_token)

        if workspace_id is None:
            logger.debug(f"No workspace found.")
            workspace_id = create_workspace(terraform_organization, workspace_name, f"OneTakedaChina/{project_name}", "github_enterprise", env, terraform_api_token)

        logger.debug(f"Workspace ID: {workspace_id}")
        response_data['TerraformWorkspaceId'] = workspace_id
        response_data['TerraformWorkspaceName'] = workspace_name

        # Terraform teams
        logger.info(f"Granting application teams access to Terraform workspace.")
        for team in default_terraform_teams:
            terraform_team_name = f"{project_name}-{team}"

            # Create Terraform team if does not exist
            team_id = search_terraform_teams(terraform_organization, terraform_team_name, terraform_api_token)

            if team_id is None:
                organization_access = dict()
                organization_access['manage-policies'] = "false"
                organization_access['manage-policy-overrides'] = "false"
                organization_access['manage-workspaces'] = "false"
                organization_access['manage-vcs-settings'] = "false"

                team_id = create_terraform_team(terraform_organization, f"{project_name}-{team}", organization_access, "organization", terraform_api_token)

            existing_access = search_team_workspace_access(team_id, workspace_id, terraform_api_token)
            
            if existing_access is None:
                access_attributes = dict()
                access_attributes['data'] = dict()
    
                data = access_attributes['data']
                data['type'] = "team-workspaces"
                data['attributes'] = dict()
    
                # TODO: Consider integrating custom policies
                data_attributes = data['attributes']
                data_attributes['access'] = default_terraform_teams[team]
    
                data['relationships'] = dict()
                data_relationships = data['relationships']
    
                data_relationships['team'] = dict()
                team_relationship = data_relationships['team']
                team_relationship['data'] = dict()
                team_relationship_data = team_relationship['data']
                team_relationship_data['type'] = "teams"
                team_relationship_data['id'] = team_id
    
                data_relationships['workspace'] = dict()
                workspace_relationship = data_relationships['workspace']
                workspace_relationship['data'] = dict()
                workspace_relationship_data = workspace_relationship['data']
                workspace_relationship_data['type'] = "workspaces"
                workspace_relationship_data['id'] = workspace_id
                logger.info(access_attributes)
    
                add_workspace_team_access(workspace_id, team_id, access_attributes, terraform_api_token)
            elif existing_access is False:
                logger.info("Update permission")

            service_catalog_output_name = f"Terraform{team}TeamName"
            response_data[service_catalog_output_name] = terraform_team_name

        logger.info(f"Granting support teams access to Terraform workspace.")
        for team in global_terraform_teams:
            # Create Terraform team if does not exist
            team_id = search_terraform_teams(terraform_organization, team, terraform_api_token)

            if team_id is None:
                organization_access = dict()
                organization_access['manage-policies'] = "false"
                organization_access['manage-policy-overrides'] = "false"
                organization_access['manage-workspaces'] = "true"
                organization_access['manage-vcs-settings'] = "true"

                team_id = create_terraform_team(terraform_organization, team, organization_access, "organization", terraform_api_token)

            existing_access = search_team_workspace_access(team_id, workspace_id, terraform_api_token)
            
            if existing_access is None:
                access_attributes = dict()
                access_attributes['data'] = dict()
    
                data = access_attributes['data']
                data['type'] = "team-workspaces"
                data['attributes'] = dict()
    
                # TODO: Consider integrating custom policies
                data_attributes = data['attributes']
                data_attributes['access'] = global_terraform_teams[team]
    
                data['relationships'] = dict()
                data_relationships = data['relationships']
    
                data_relationships['team'] = dict()
                team_relationship = data_relationships['team']
                team_relationship['data'] = dict()
                team_relationship_data = team_relationship['data']
                team_relationship_data['type'] = "teams"
                team_relationship_data['id'] = team_id
    
                data_relationships['workspace'] = dict()
                workspace_relationship = data_relationships['workspace']
                workspace_relationship['data'] = dict()
                workspace_relationship_data = workspace_relationship['data']
                workspace_relationship_data['type'] = "workspaces"
                workspace_relationship_data['id'] = workspace_id
                logger.debug(f"Access attributes request: {access_attributes}")
    
                add_workspace_team_access(workspace_id, team_id, access_attributes, terraform_api_token)
            elif existing_access is False:
                logger.info("Update permission")
    except Exception as e:
        logger.debug(traceback.format_exc())
        delete_dir(base_path)

        try: 
            error = e['Error']
            error_code = e['ErrorCode']
            error_message = e['Message']
        except:
            error = str(e)
            error_code = 500
            error_message = "Internal Server Error"

        logger.error(error)
        logger.debug(error_message)

        response_data['Message'] = error_message
        response_data['ErrorCode'] = error_code
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data, "CustomResourcePhysicalID")

        return {'statusCode': error_code, 'body': json.dumps({'Error': error_message})}

    delete_dir(base_path)

    logger.debug(f"CloudFormation Response Data: {response_data}")
    cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, "CustomResourcePhysicalID")

    return {'statusCode': 200, 'body': {'Message': message}}


def random_entity_name():
   letters = string.ascii_lowercase

   return ''.join(random.choice(letters) for i in range(10))


