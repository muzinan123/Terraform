import errno
import json
import os
import shutil

from common.custom_logging import CustomLogger
from git_helper import checkout, commit, push
from jinja2 import Environment, FileSystemLoader
from shutil import copy2

logger = CustomLogger().logger

github_endpoint = os.environ['GITHUB_ENDPOINT']
github_organization = os.environ['GITHUB_ORGANIZATION']


def copy_module(repo, source_path, destination_path, request_id, provider, module_name, replacement_values):
    '''
        This function takes a GitHub repository object (repo) and checks out the a branch (request_id) to copy 
        Infrastructure as Code (IaC) files from a source (source_repository_path) to a destination (destination_path). 
        The function looks for a targeted set of files based on the provider and module_name. Once identified, 
        it pass these identified files to the generate_parameter function to leverage Jinja and replace 
        parameterized values with the replacement_values. After the modules are copied, a push to the 
        remote GitHub branch is made.

        Args:
            repo (obj):                 A GitHub repository object
            source_path (str):          The path to the source project
            destination_path (str):     The path to the destination project
            request_id (str):           A unique identifier tied for the request
            provider (str):             The type of Infrastructure as Code (IaC)
            module_name (str):          The resource provisioned by the Infrastructure as Code (IaC)
            replacement_values (dict):  The values used to replace parameters via Jinja

        Returns:
            branch_name (str):          The name of the Git Branch
    '''
    # Check out a new branch to make changes on
    branch_name = checkout(repo, f"servicecatalog/{request_id}")
    
    # If the appropriate source path is identified for a given module (i.e. EC2, RDS, ELB, etc) or 
    # provider (i.e. Terraform, CloudFormation, etc) then the value is set as the path
    # to break the loop to parse files
    module_path = None
    provider_path = None

    logger.info(f"Looking for the {provider} {module_name} module in {source_path}...")

    if not os.path.isdir(destination_path):
        logger.debug(f"Destination directory {destination_path} did not exist... Creating...")
        os.mkdir(destination_path)

    # Parse through source code for the given `module_name` (i.e. EC2, RDS, ELB, etc.)
    # Capture the path of the source code for the module for additional 
    # parsing for the requested `provider` (i.e. Terraform, CloudFormation, etc)
    try:
        logger.debug(f"Searching for requested module {module_name}")
        for dir_path, dir_names, files in os.walk(source_path):
            if module_path is None:
                for name in dir_names:
                    if name == module_name:
                        module_path = f"{dir_path}/{module_name}"
                        break

        logger.debug(f"Module path: {module_path}")
        logger.debug(os.listdir(source_path))
        logger.debug(os.stat(source_path))
    except Exception as e:
        logger.debug(os.listdir(source_path))
        logger.debug(os.stat(source_path))

        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable find requested module in source code."

        raise Exception(exception_metadata)

    # Parse through the `module_name` source code (i.e. EC2, RDS, ELB, etc.) 
    # Capture the path of the requested `provider` (i.e. Terraform, CloudFormation, etc)
    # to parse for contents to be copied to the destination (`project_repository_path`)
    try:
        logger.debug(f"Searching for requested provider {provider}")
        for _module_path, _module_dir, _module_files in os.walk(module_path):
            if provider_path is None:
                for name in _module_dir:
                    if name == provider:
                        provider_path = f"{_module_path}/{name}"
                        break
        logger.debug(f"Provider path: {provider_path}")
    except Exception as e:
        logger.debug(os.listdir(module_path))
        logger.debug(os.stat(module_path))

        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable find requested provider in source code."

        raise Exception(exception_metadata)

    if provider_path is None:
        exception_metadata = dict()
        exception_metadata['Error'] = "Unable find requested provider in source code."
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable find requested provider in source code."

        raise Exception(exception_metadata)

    # Parse through the `provider` source code (i.e. Terraform, CloudFormation, etc)
    # to identify the necessary code to be copied to the destination (`project_repository_path`)
    # for a given `module_name` (i.e. EC2, RDS, ELB, etc)
    try:
        for _module_path, _module_dir, _module_files in os.walk(provider_path):
            logger.debug(f"Path: {_module_path}")
            logger.debug(f"Directory: {_module_dir}")
            logger.debug(f"Files: {_module_files}")
    
            source_directory = _module_path[len(f"{provider_path}/"):]
    
            # Determine if the code is in the root directory or in a sub-directory
            # Root directory: Copy files from source to destination 
            # Sub-directory:  Validate if the sub-directory needs to be created at the destination 
            #                 and copy the files to the sub-directory at the destination
            if source_directory == provider_path:
                for file in _module_files:
                    source_copy_path = os.path.join(source_directory, file)
                    logger.debug(f"Source File: {source_path}")
                    
                    destination_copy_path = os.path.join(destination_path, file)
                    logger.debug(f"Destination File: {destination_copy_path}")
    
                    copy2(source_copy_path, destination_copy_path)
                    logger.debug(f"File copied to {destination_copy_path}")
            else:
                logger.debug(f"Base Directory: {source_directory}")

                if not os.path.isdir(f"{destination_path}/{source_directory}"):
                    logger.debug(f"Directory {destination_path}/{source_directory} did not exist... Creating...")
                    os.mkdir(f"{destination_path}/{source_directory}")
                else:
                    logger.warn(f"Directory {destination_path}/{source_directory} already exists - contents may be overwritten.")

                for file in _module_files: 
                    source_copy_path = os.path.join(provider_path, source_directory, file)
                    logger.debug(f"Source File: {source_copy_path}")

                    destination_copy_path = os.path.join(f"{destination_path}/{source_directory}", file)
                    logger.debug(f"Destination File: {destination_copy_path}")

                    copy2(source_copy_path, destination_copy_path)
                    logger.debug(f"File copied to {destination_copy_path}")
    except Exception as e:
        logger.debug(os.listdir(provider_path))
        logger.debug(os.stat(provider_path))

        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable find module source code."

        raise Exception(exception_metadata)

    logger.info("Looking for Jinja templates...")

    # Once the `provider` source code for the respective `module_name` is
    # copied to the `project_repository_path`, the destination is parsed to 
    # identify any Jinja templates that need to be rendered
    for dir_path, dir_names, files in os.walk(destination_path):
        for item in files:
            if ".j2" in item or ".jinja" in item:
                file_basename = os.path.basename(item)
                file_basename = os.path.splitext(file_basename)[0]
                logger.debug(f"Base Name: {file_basename}")

                try:
                    rename_files = ["main.tf", "outputs.tf", "README.md"]
                    if file_basename in rename_files:
                        generate_parameter(destination_path, item, destination_path, f"{request_id}-{file_basename}", replacement_values)
                    else:
                        generate_parameter(destination_path, item, destination_path, f"{file_basename}", replacement_values)
                except Exception as e:
                    exception_metadata = dict()
                    exception_metadata['Error'] = e
                    exception_metadata['ErrorCode'] = 500
                    exception_metadata['Message'] = "Unable to render Jinja files."

                    raise Exception(exception_metadata)
    logger.info(f"Source code copied to branch ({branch_name})")
                    
    commit_status = commit(repo, destination_path)
    logger.debug(f"Commit status: {commit_status}")

    if commit_status is True:
        push(repo, branch_name)
        
        return branch_name
    else:
        return None


def generate_parameter(input_path, input_file, output_path, output_file, replacement_values):
    '''
        This function takes a path (module_path) to the input file (input_file) and creates a 
        rendered file (output_file) in the output path (output_path) by calling the
        render_template function and passing in the replacement values (replacement_values).

        Args:
            input_path (str):               The path to the input files
            input_file (str):               The input file name
            output_path (str):              The path to the output files
            output_file (str):              The output file name
            replacement_values (dict):      A dictionary containing the key/value
                                            pairs used to replace parameters in the
                                            template_file 

        Returns:
            None
    '''
    logger.debug(f"Updating {output_path}/{input_file} with Jinja values")

    try:
        with open(f"{output_path}/{output_file}", 'w') as f:
            h = render_template(input_path, input_file, replacement_values)

            logger.debug(f'Initiating write function for {input_file}')
            f.write(h)

            logger.debug(f'Closing write function for {input_file}')
            f.close()

            logger.debug(f"Template copied to {output_path}/{output_file}")
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to create destination file."

        raise Exception(exception_metadata)

    os.remove(f"{input_path}/{input_file}")
    logger.debug("Template file removed")

    return


def render_template(path, template_filename, context):
    '''
        This function takes a path and file name (template_filename) & 
        leverages Jinja to render the template by replacing the parameters
        with the corresponding values in the context.

        Args:
            path (str):                 The path where the template is
            template_filename (str):    The name of the template file
            context (dict):             A dictionary containing the key/value
                                        pairs used to replace parameters in the
                                        template_file 
        Returns:
            None
    '''
    try:
        template_environment = Environment(
            loader=FileSystemLoader(path),
            trim_blocks=True
        )
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to render template."

        raise Exception(exception_metadata)

    return template_environment.get_template(template_filename).render(context)


def delete_dir(path):
    '''
        This function deletes the provided directory (path)

        Args:
            path (str):     Local path to delete

        Returns:
            None
    '''
    logger.debug(f"Deleting {path}")

    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable delete directory."

        raise Exception(exception_metadata)


