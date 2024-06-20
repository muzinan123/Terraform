import json
import os
import requests

from common.custom_logging import CustomLogger
from requests import exceptions


logger = CustomLogger().logger


terraform_endpoint = os.environ['TERRAFORM_ENDPOINT']


def get_vcs_oauth_token(organization_name, service_provider, token):
    '''
        This function allows you to list all OAuth tokens for a given
        Version Control System (VCS) provider (service provider) in the 
        provided Terraform organization (organization_name).

        Args:
            organization_name (str):        The name of the Terraform organization
            service_provider (str):         The Version Control System (VCS) provider
            token (str):                    Terraform Enterprise API token

        Returns:
            client_token_id (str):          The ID for the Version Control System client token

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/oauth-tokens#list-oauth-tokens
    '''
    logger.info(f"Getting OAuth token for {organization_name} {service_provider}")
    client_id = get_vcs_oauth_client(organization_name, service_provider, token)
    
    try: 
        response = requests.get(
                f"https://{terraform_endpoint}/api/v2/oauth-clients/{client_id}/oauth-tokens",
                headers={"Authorization": f"Bearer {token}"}
            ).json()
    except requests.exceptions.SSLError as e:
        response = requests.get(
                f"http://{terraform_endpoint}/api/v2/oauth-clients/{client_id}/oauth-tokens",
                headers={"Authorization": f"Bearer {token}"},
                verify=False
            ).json()
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to get OAuth token" 

        raise Exception(exception_metadata)

    # TODO: Handle errors
    if response.get('errors'):
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response)
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to get OAuth token."

        raise Exception(exception_metadata)
    else:
        logger.debug(json.dumps(response))
        
        if len(response['data']) > 0:
            for item in response['data']:
                client_token_id = item['id']
        else:
            exception_metadata = dict()
            exception_metadata['Error'] = json.dumps(response)
            exception_metadata['ErrorCode'] = 500
            exception_metadata['Message'] = "Unable to find OAuth token."

            raise Exception(exception_metadata)
            
        return client_token_id


def get_vcs_oauth_client(organization_name, service_provider, token):
    '''
        This function allows you to list Version Control System connections between 
        an organization (organization_name) and a VCS provider (service_provider) 
        like GitHub, GitLab, BitBucket, etc for use when creating or setting up 
        workspaces.

        Args:
            organization_name (str):        The name of the Terraform organization
            service_provider (str):         The Version Control System (VCS) provider
            token (str):                    Terraform Enterprise API token

        Returns:
            client_id (str):                The ID for the Version Control System client
                                            Returns None if no Version Control client is identified
                                            for the provided service provider

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/oauth-clients#list-oauth-clients
    '''
    logger.info(f"Identifying OAuth clients for {organization_name}...")

    headers = dict()
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = "application/vnd.api+json"

    try: 
        response = requests.get(
                f"https://{terraform_endpoint}/api/v2/organizations/{organization_name}/oauth-clients",
                headers=headers
            )
    except requests.exceptions.SSLError as e:
        response = requests.get(
                f"http://{terraform_endpoint}/api/v2/organizations/{organization_name}/oauth-clients",
                headers=headers,
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to identify OAuth client" 

        raise Exception(exception_metadata)
    response_json = response.json()    
    
    if response.status_code == 200:
        logger.debug(json.dumps(response_json))

        if response_json.get("data"):
            for item in response_json['data']:
                if item['attributes']['service-provider'].lower() == service_provider.lower():
                    logger.info(f"Found OAuth client for {service_provider}.")
    
                    client_id = item['id']

                    return client_id
        elif response_json.get("status"):
            exception_metadata = dict()
            exception_metadata['Error'] = json.dumps(response_json)
            exception_metadata['ErrorCode'] = 500
            exception_metadata['Message'] = "Unable to list Terraform Enterprise workspaces."

        return None


def list_workspaces(organization_name, token):
    '''
        This function identifies all existing Terraform Enterprise workspaces
        in the provided Terraform organization (organization_name)

        Args:
            organization_name (str):        The name of the Terraform organization
            token (str):                    Terraform Enterprise API token

        Returns:
            workspace_id (str):             A dictionary of metadata for the existing
                                            Terraform workspaces

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/workspaces#list-workspace
    '''
    existing_workspaces_list = list()
    
    try: 
        response = requests.get(
                f"https://{terraform_endpoint}/api/v2/organizations/{organization_name}/workspaces",
                headers={"Authorization": f"Bearer {token}"}
            )
    except requests.exceptions.SSLError as e:
        response = requests.get(
                f"http://{terraform_endpoint}/api/v2/organizations/{organization_name}/workspaces",
                headers={"Authorization": f"Bearer {token}"},
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to list Terraform Enterprise workspaces" 

        raise Exception(exception_metadata)

    logger.debug(response)

    if response.status_code == 200:
        response = response.json()
        logger.debug(response)
        
        for team in response['data']:
            existing_workspaces_list.append(team)
    elif response.status_code == 404:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response.json())
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Workspaces not found"

        raise Exception(exception_metadata)
    elif response.status_code == 422:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response.json())
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Invalid attribute"

        raise Exception(exception_metadata)
    else:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response.json())
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unknown error - unable to list Terraform Enterprise workspaces" 

        raise Exception(exception_metadata)

    try:
        if response.get("links"):
            response_metadata_links = response['links']

            if response_metadata_links.get("next"):
                next_page_url = response_metadata_links['next']
                current_page_url = response_metadata_links['self']
                last_page_url = response_metadata_links['last']

                while next_page_url is not None:
                    logger.debug(f"Parsing page {response['meta']['pagination']['next-page']} ({next_page_url} of results.")
                    
                    try: 
                        response = requests.get(
                                next_page_url,
                                headers={"Authorization": f"Bearer {token}"}
                            )
                    except requests.exceptions.SSLError as e:
                        response = requests.get(
                                next_page_url,
                                headers={"Authorization": f"Bearer {token}"},
                                verify=False
                            )
                    except requests.exceptions.ConnectionError as e:
                        exception_metadata = dict()
                        exception_metadata['Error'] = e
                        exception_metadata['ErrorCode'] = 502
                        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 
                
                        raise Exception(exception_metadata)
                    except Exception as e:
                        exception_metadata = dict()
                        exception_metadata['Error'] = e
                        exception_metadata['ErrorCode'] = 400
                        exception_metadata['Message'] = "Unable to complete request to list Terraform Enterprise workspaces" 
                
                        raise Exception(exception_metadata)
                        
                    logger.debug(response)
                
                    if response.status_code == 200:
                        response = response.json()
                        logger.debug(response)
                        
                        for team in response['data']:
                            existing_workspaces_list.append(team)
                    elif response.status_code == 404:
                        exception_metadata = dict()
                        exception_metadata['Error'] = json.dumps(response.json())
                        exception_metadata['ErrorCode'] = response.status_code
                        exception_metadata['Message'] = "Workspaces not found"
                        raise Exception(exception_metadata)
                    else:
                        exception_metadata = dict()
                        exception_metadata['Error'] = json.dumps(response.json())
                        exception_metadata['ErrorCode'] = response.status_code
                
                        exception_metadata['Message'] = "Unknown error - unable to list Terraform Enterprise workspaces" 
                        raise Exception(exception_metadata)

                    if response.get("links"):
                        response_metadata_links = response['links']
                        next_page_url = response_metadata_links['next']
                        current_page_url = response_metadata_links['self']
                        last_page_url = response_metadata_links['last']
                    else:
                        next_page_url = None
            else:
                logger.debug("No additional pages to parse")
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to complete pagination of Terraform workspaces."

        raise Exception(exception_metadata)

    logger.info(f"Found {len(existing_workspaces_list)} existing Terraform Enterprise workspaces")    
    return existing_workspaces_list


def search_workspaces(organization_name, workspace_name, token):
    '''
        This function searches existing Terraform Enterprise workspaces (workspace_name) by name
        in the provided Terraform organization (organization_name).

        Args:
            organization_name (str):        The name of the Terraform organization
            token (str):                    Terraform Enterprise API token

        Returns:
            workspace_id (str):             ID of the requested Terraform workspace

        Documentation:
            Terraform API: N/A - See list_workspaces for more details
    '''
    existing_workspaces = list_workspaces(organization_name, token)

    if existing_workspaces:
        logger.debug(f"Existing workspaces: {existing_workspaces}")

        for item in existing_workspaces:
            workspace_id = item['id']
            workspace_attributes = item['attributes']
            
            if workspace_attributes['name'] == workspace_name:
                logger.info(f"Found existing workspace for {workspace_name}.")

                return workspace_id

    logger.warn(f"No Terraform Enterprise workspaces found!")

    return None
    
    
def create_workspace(organization_name, workspace_name, vcs_source_name, vcs_provider, environment, token):
    '''
        This function creates a Terraform Enterprise workspace (workspace_name) in the provided Terraform
        organization (organization_name) with the requested organizational access (organization_access)
        and visibility (visibility)

        NOTE: Workspace creation is restricted to the owners team, teams with the "Manage Workspaces" permission
        and the organization API token.

        Args:
            organization_name (str):        The name of the Terraform organization
            workspace_name (str):           The name of the Terraform workspaces
                                            Can only include letters, numbers, -, and _
            vcs_source_name (dict):         A reference to your Version Control System (VCS)
                                            repository. The expected format is :org/:repo 
                                            where :org and :repo refer to the organization &
                                            repository in your VCS provider
                                            All properties default to false.
            vcs_provider (str):             The Version Control System (VCS) provider
            environment (str):              The TEC environment that the workspace is used for
            token (str):                    Terraform Enterprise API token

        Returns:
            workspace_id (str):             ID of the created Terraform workspace

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/workspaces#create-a-workspace
    '''
    logger.debug(f"Requested Terraform Enterprise Organization: {organization_name}")
    logger.debug(f"Requested Terraform Enterprise Workspace Name: {workspace_name}")

    vcs_oauth_token_id = get_vcs_oauth_token(organization_name, vcs_provider, token)

    body = dict()
    body['data'] = dict()
    
    data = body['data']
    data['type'] = "workspaces"
    data['attributes'] = dict()
    
    data_attributes = data['attributes']
    data_attributes['name'] = workspace_name
    data_attributes['description'] = f"Workspace for {workspace_name}"
    data_attributes['global-remote-state'] = False
    data_attributes['execution-mode'] = "remote" 
    data_attributes['auto-apply'] = True
    data_attributes['working-directory'] = environment
    data_attributes['vcs-repo'] = dict()
    data_attributes['trigger-prefixes'] = f"{environment}/"

    data_attributes['queue-all-runs'] = True
    data_attributes['speculative-enabled'] = True

    vcs_repo = data_attributes['vcs-repo']
    vcs_repo['identifier'] = vcs_source_name
    vcs_repo['oauth-token-id'] = vcs_oauth_token_id
    vcs_repo['branch'] = "main"

    logger.debug(f"Request Body: {json.dumps(body)}")

    headers = dict()
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = "application/vnd.api+json"

    try:
        response = requests.post(
                f"https://{terraform_endpoint}/api/v2/organizations/{organization_name}/workspaces",
                headers=headers,
                data=json.dumps(body)
            )
    except requests.exceptions.SSLError as e:
        response = requests.post(
                f"http://{terraform_endpoint}/api/v2/organizations/{organization_name}/workspaces",
                headers=headers,
                data=json.dumps(body),
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to create Terraform Enterprise workspace" 

        raise Exception(exception_metadata)

    logger.debug(response)

    if response.status_code == 200 or response.status_code == 201:
        response = response.json()
        logger.debug(response)
        
        workspace_id = response['data']['id']
    elif response.status_code == 404:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response.json())
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Page not found"

        raise Exception(exception_metadata)
    elif response.status_code == 422:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response.json())
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Invalid attribute"

        raise Exception(exception_metadata)                        
    else:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response.json())
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise workspaces" 

        raise Exception(exception_metadata)

    return workspace_id

def list_terraform_teams(organization_name, token):
    '''
        This function lists the Terraform Enterprise teams within the organization (organizaton_name)

        Args:
            organization_name (str):               The name of the Terraform organization

        Returns:
            existing_teams_list (list (dict)):     A list of dictionaries containing metadata
                                                   of the existing Terraform team 

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/teams#list-teams
    '''
    existing_teams_list = list()

    try: 
        response = requests.get(
                f"https://{terraform_endpoint}/api/v2/organizations/{organization_name}/teams",
                headers={"Authorization": f"Bearer {token}"}
            )
    except requests.exceptions.SSLError as e:
        response = requests.get(
                f"http://{terraform_endpoint}/api/v2/organizations/{organization_name}/teams",
                headers={"Authorization": f"Bearer {token}"},
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to list Terraform Enterprise teams" 

        raise Exception(exception_metadata)

    logger.debug(response)
    response_json = response.json()

    if response.status_code == 200:
        logger.debug("The request was successful")
        logger.debug(response_json)
        
        for team in response_json['data']:
            existing_teams_list.append(team)
    elif response.status_code == 404:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Workspace not found or user unauthorized to perform action"
        raise Exception(exception_metadata)
    else:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise team" 

        raise Exception(exception_metadata)

    try:
        if response_json.get("links"):
            response_metadata_links = response_json['links']

            if response_metadata_links.get("next"):
                next_page_url = response_metadata_links['next']
                current_page_url = response_metadata_links['self']
                last_page_url = response_metadata_links['last']

                while next_page_url is not None:
                    logger.debug(f"Parsing page {response_json['meta']['pagination']['next-page']} ({next_page_url} of results.")

                    try: 
                        response = requests.get(
                                next_page_url,
                                headers={"Authorization": f"Bearer {token}"}
                            )
                    except requests.exceptions.SSLError as e:
                        response = requests.get(
                                next_page_url,
                                headers={"Authorization": f"Bearer {token}"},
                                verify=False
                            )
                    except requests.exceptions.ConnectionError as e:
                        exception_metadata = dict()
                        exception_metadata['Error'] = e
                        exception_metadata['ErrorCode'] = 502
                        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

                        raise Exception(exception_metadata)
                    except Exception as e:
                        exception_metadata = dict()
                        exception_metadata['Error'] = e
                        exception_metadata['ErrorCode'] = 400
                        exception_metadata['Message'] = "Unable to complete request to list Terraform teams."                    

                        raise Exception(exception_metadata)

                    logger.debug(response)
                    response_json = response.json()

                    if response.status_code == 200:
                        logger.debug(response_json)
                        
                        for team in response_json['data']:
                            existing_teams_list.append(team)
                    elif response.status_code == 404:
                        exception_metadata = dict()
                        exception_metadata['Error'] = json.dumps(response_json)
                        exception_metadata['ErrorCode'] = response.status_code
                        exception_metadata['Message'] = "Workspace not found or user unauthorized to perform action"
                        raise Exception(exception_metadata)
                    else:
                        exception_metadata = dict()
                        exception_metadata['Error'] = json.dumps(response_json)
                        exception_metadata['ErrorCode'] = response.status_code
                        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise team" 

                        raise Exception(exception_metadata)   
                    
                    if response_json.get("links"):
                        response_metadata_links = response_json['links']
                        next_page_url = response_metadata_links['next']
                        current_page_url = response_metadata_links['self']
                        last_page_url = response_metadata_links['last']
                    else:
                        next_page_url = None
            else:
                logger.debug("No additional pages to parse")
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to complete pagination of Terraform teams."

        raise Exception(exception_metadata)

    logger.debug(f"Found {len(existing_teams_list)} existing Terraform Enterprise teams")    
    return existing_teams_list


def search_terraform_teams(organization_name, team_name, token):
    '''
        This function searches for an existing Terraform Enterprise team (team_name)
        by name in the provided Terraform organization (organization_name).

        Args:
            organization_name (str):        The name of the Terraform organization
            team_name (str):                The name of the team
                                            Can only include letters, numbers, -, and _
            token (str):                    Terraform Enterprise API token

        Returns:
            team_id (str):                  ID of the requested Terraform team
                                            Returns None if no team is found

        Documentation:
            Terraform API - N/A - see list_terraform_teams for more details
    '''
    logger.info(f"Searching for {team_name} in {organization_name}")

    existing_teams = list_terraform_teams(organization_name, token)

    if existing_teams:
        logger.debug(existing_teams)

        for item in existing_teams:
            team_id = item['id']
            team_attributes = item['attributes']
            
            if team_attributes['name'] == team_name:
                logger.info(f"Found existing Terraform Enterprise team for {team_name}.")

                return team_id

    logger.warn(f"No Terraform Enterprise team found!")
    
    return None
    
    
def create_terraform_team(organization_name, team_name, organization_access, visibility, token):
    '''
        This function creates a Terraform Enterprise team (team_name) in the provided Terraform
        organization (organization_name) with the requested organizational access (organization_access)
        and visibility (visibility)

        Args:
            organization_name (str):        The name of the Terraform organization
            team_name (str):                The name of the team
                                            Can only include letters, numbers, -, and _
            organization_access (dict):     Settings for the team's organization access. 
                                            All properties default to false.
            visibility (str):               The team's visibility. 
                                            Must be "secret" or "organization"
            token (str):                    Terraform Enterprise API token

        Returns:
            team_id (str):                  ID of the created Terraform team

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/teams#create-a-team
    '''
    logger.debug(f"Requested Team Name: {team_name}")

    body = dict()
    body['data'] = dict()
    
    data = body['data']
    data['type'] = "teams"
    data['attributes'] = dict()
    
    data_attributes = data['attributes']
    data_attributes['name'] = team_name
    data_attributes['visibility'] = visibility

    data_attributes['organization-access'] = organization_access

    logger.debug(f"Request Body: {json.dumps(body)}")

    headers = dict()
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = "application/vnd.api+json"

    try:
        response = requests.post(
                f"https://{terraform_endpoint}/api/v2/organizations/{organization_name}/teams",
                headers=headers,
                data=json.dumps(body)
            )
    except requests.exceptions.SSLError as e:
        response = requests.post(
                f"http://{terraform_endpoint}/api/v2/organizations/{organization_name}/teams",
                headers=headers,
                data=json.dumps(body),
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to create Terraform Enterprise team" 

        raise Exception(exception_metadata)        
        
    logger.debug(response)
    response_json = response.json()
    
    if response.status_code == 200 or response.status_code == 201:
        team_id = response_json['data']['id']

        logger.info(f"Terraform Enterprise team ({team_id}) created")
        logger.debug(json.dumps(response_json))

        return team_id
    elif response.status_code == 400:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Bad Request - Invalid parameters" 

        raise Exception(exception_metadata)     
    # 404 - Not Found can also indicate insufficient privileges
    elif response.status_code == 404:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unable to find Terraform Enterprise team" 

        raise Exception(exception_metadata)   
    elif response.status_code == 422:
        exception_metadata = dict()

        if response_json['errors'][0].get('detail'):
            exception_metadata['Error'] = response_json['errors'][0]['detail']
        else:
            exception_metadata['Error'] = json.dumps(response_json)

        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Malformed request body" 

        raise Exception(exception_metadata)
    elif response.status_code == 500:   
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unable to create Terraform Enterprise team" 

        raise Exception(exception_metadata)   
    else:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise team" 

        raise Exception(exception_metadata)   


def list_team_access_to_workspace(workspace_id, token):
    '''
        This function list the teams that have access  to the provided Terraform workspace (workspace_id).

        NOTE: A team-workspace resource represents a team's local permissions on a specific workspace. 
        Teams can also have organization-level permissions that grant access to workspaces, 
        and Terraform Enterprise uses whichever access level is higher

        Args:
            workspace_id (str):                             The workspace ID to grant access to
            token (str):                                    Terraform Enterprise API token

        Returns:
            existing_workspace_access_list (list (dict)):   A list of dictionaries containing metadata
                                                            of the Terraform teams with access

        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/team-access#list-team-access-to-a-workspace
    '''
    existing_workspace_access_list = list()

    headers = dict()
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = "application/vnd.api+json"

    try:
        response = requests.get(
                f"https://{terraform_endpoint}/api/v2/team-workspaces?filter%5Bworkspace%5D%5Bid%5D={workspace_id}",
                headers=headers
            )
    except requests.exceptions.SSLError as e:
        response = requests.get(
                f"https://{terraform_endpoint}/api/v2/team-workspaces?filter%5Bworkspace%5D%5Bid%5D={workspace_id}",
                headers=headers,
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to list Terraform Enterprise team access to workspace" 

        raise Exception(exception_metadata)        

    logger.debug(response)
    response_json = response.json()

    if response.status_code == 200:
        logger.debug(response_json)
        
        for workspace in response_json['data']:
            existing_workspace_access_list.append(workspace)
    # 404 - Not Found can also indicate insufficient privileges
    elif response.status_code == 404:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unable to find Terraform Enterprise workspaces" 

        raise Exception(exception_metadata)   
    else:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise team" 

        raise Exception(exception_metadata)   
                
    try:
        if response_json.get("links"):
            response_metadata_links = response_json['links']
            
            if response_metadata_links.get("next"):
                next_page_url = response_metadata_links['next']
                current_page_url = response_metadata_links['self']
                last_page_url = response_metadata_links['last']
        
                while next_page_url is not None:
                    logger.debug(f"Parsing page {response_json['meta']['pagination']['current-page']} of results.")
        
                    try: 
                        response = requests.get(
                            next_page_url,
                            headers={"Authorization": f"Bearer {token}"}
                        )
                    except requests.exceptions.SSLError as e:
                        response = requests.get(
                            next_page_url,
                            headers={"Authorization": f"Bearer {token}"},
                            verify=False
                        )
                    except requests.exceptions.ConnectionError as e:
                        exception_metadata = dict()
                        exception_metadata['Error'] = e
                        exception_metadata['ErrorCode'] = 502
                        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

                        raise Exception(exception_metadata)
                    except Exception as e:
                        exception_metadata = dict()
                        exception_metadata['Error'] = e
                        exception_metadata['ErrorCode'] = 400
                        exception_metadata['Message'] = "Unable to complete request to list Terraform workspace permissions"

                        raise Exception(exception_metadata)
                    
                    logger.debug(response)
                    response_json = response.json()

                    if response.status_code == 200:
                        logger.debug(response_json)
                        
                        for workspace in response_json['data']:
                            existing_workspace_access_list.append(workspace)
                    # 404 - Not Found can also indicate insufficient privileges
                    elif response.status_code == 404:
                        exception_metadata = dict()
                        exception_metadata['Error'] = json.dumps(response_json)
                        exception_metadata['ErrorCode'] = response.status_code
                        exception_metadata['Message'] = "Unable to find Terraform Enterprise workspaces" 

                        raise Exception(exception_metadata)   
                    else:
                        exception_metadata = dict()
                        exception_metadata['Error'] = json.dumps(response_json)
                        exception_metadata['ErrorCode'] = response.status_code
                        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise team" 

                        raise Exception(exception_metadata)
                    
                    if response_json.get("links"):
                        response_metadata_links = response_json['links']
                        next_page_url = response_metadata_links['next']
                        current_page_url = response_metadata_links['self']
                        last_page_url = response_metadata_links['last']
                    else:
                        next_page_url = None
            else:
                logger.debug("No additional pages to parse")
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to complete pagination of Terraform workspace permissions."

        raise Exception(exception_metadata)

    logger.debug(f"Found {len(existing_workspace_access_list)} Terraform Enterprise teams with access to workspace.")    
    return existing_workspace_access_list


def search_team_workspace_access(team_id, workspace_id, token):
    '''
        This function will search to see if the provided team (team_id) 
        has access to the provided Terraform workspace (workspace_id).

        Args:
            team_id (str):              The team ID to grant access for
            workspace_id (str):         The workspace ID to grant access to
            access_attributes (dict):   The access configuration for the 
                                        team
            token (str):                Terraform Enterprise API token

        Returns:
            :boolean:                   Returns True if the access is present
                                        Returns None if access is not present
    '''
    logger.info(f"Searching for Terraform Enterprise team ({team_id}) access to workspace ({workspace_id})")
    
    response = list_team_access_to_workspace(workspace_id, token)

    logger.debug(response)
    for item in response:
        access = item['attributes']['access']
        logger.debug(f"Access: {access}")
        _team_id = item['relationships']['team']['data']['id']
        
        if _team_id == team_id:
            logger.debug(f"Found existing permission for workspace ")

            return True

    logger.warn(f"{team_id} does not have access to {workspace_id}")

    return None


def add_workspace_team_access(workspace_id, team_name, access_attributes, token):
    '''
        This function will grant the provided team (team_name) the requested
        access (access_attributes) to the Terraform Enterprise workspace. 

        Args:
            workspace_id (str):         The workspace ID to grant access to
            team_name (str):            The team name to grant access for
            access_attributes (dict):   The access configuration for the 
                                        team
            token (str):                Terraform Enterprise API token

        Returns:
            None
        
        Documentation:
            Terraform API: https://www.terraform.io/cloud-docs/api-docs/team-access#add-team-access-to-a-workspace
    '''
    logger.debug(f"Adding access to {workspace_id} for {team_name}")

    logger.debug(f"Request Body: {json.dumps(access_attributes)}")

    headers = dict()
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = "application/vnd.api+json"

    try:
        response = requests.post(
                f"https://{terraform_endpoint}/api/v2/team-workspaces",
                headers=headers,
                data=json.dumps(access_attributes)
            )
    except requests.exceptions.SSLError as e:
        response = requests.post(
                f"http://{terraform_endpoint}/api/v2/team-workspaces",
                headers=headers,
                data=json.dumps(access_attributes),
                verify=False
            )
    except requests.exceptions.ConnectionError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 502
        exception_metadata['Message'] = "Unable to connect to Terraform Enterprise" 

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to complete request to add team access Terraform Enterprise workspace" 

        raise Exception(exception_metadata)

    logger.debug(response)
    response_json = response.json()

    if response.status_code == 200 or response.status_code == 201:
        logger.debug(f"Access added for {team_name}")

        return
    # 404 - Not Found can also indicate insufficient privileges
    elif response.status_code == 404:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unable to add team access to Terraform Enterprise workspace"

        raise Exception(exception_metadata)   
    elif response.status_code == 422:
        exception_metadata = dict()

        if response_json['errors'][0].get('detail'):
            exception_metadata['Error'] = response_json['errors'][0]['detail']
        else:
            exception_metadata['Error'] = json.dumps(response_json)

        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Malformed request body" 

        raise Exception(exception_metadata)   
    else:
        exception_metadata = dict()
        exception_metadata['Error'] = json.dumps(response_json)
        exception_metadata['ErrorCode'] = response.status_code
        exception_metadata['Message'] = "Unknown error - unable to create Terraform Enterprise team" 

        raise Exception(exception_metadata)


