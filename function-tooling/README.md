# function-tooling

```
  _____                    __  .__                          __                .__  .__                
_/ ____\_ __  ____   _____/  |_|__| ____   ____           _/  |_  ____   ____ |  | |__| ____    ____  
\   __\  |  \/    \_/ ___\   __\  |/  _ \ /    \   ______ \   __\/  _ \ /  _ \|  | |  |/    \  / ___\ 
 |  | |  |  /   |  \  \___|  | |  (  <_> )   |  \ /_____/  |  | (  <_> |  <_> )  |_|  |   |  \/ /_/  >
 |__| |____/|___|  /\___  >__| |__|\____/|___|  /          |__|  \____/ \____/|____/__|___|  /\___  / 
                 \/     \/                    \/                                           \//_____/  
```

## Description

An mPlatform only repo which contains tooling functions which are invoked by AWS Lambdas.

### gitlayer

Many of the tooling functions require Git binaries to execute Git operations, but AWS lambdas do not have git on their path. 

We therefore provide it to the lambda in a layer, e.g. a zip containing the amd64 binary file. This zip should very rarely change, and will be available in an S3 bucket for the Terraform layer resource to refer to. However, if you need to re-create this zip, use the following steps:

- navigate to src/tooling/gitlayer
- build a docker image from the Dockerfile, e.g. `docker build -t gitlayer .` You may need to disable WSS Agent.
- create a volume, e.g. `docker volume create --driver local --opt type=none --opt device=/[some local path]/mount --opt o=bind dist_vol`
- start the container, mounting the volume: `docker run -v dist_vol:/opt/dist gitlayer`
- you should see the contents of /opt/dist from the container in your local 'mount' dir, and therefore you can access the binary zip, which is named gitlayer-amd64.zip
- once you have the zip, you can upload to the relevant S3 bucket using AWS CLI.

## Setup python
If you haven't done it already, [do python setup](https://digital-channels-natwest.atlassian.net/wiki/spaces/MPLAT/pages/54330445/Python+setup)

## Setup poetry for this project
* Create python virtualenv and install project dependencies:
```
poetry install
```
You should get output like this:
```
Creating virtualenv pylibrary-mobile-build-python-xxx-py3.7 in /Users/your-username/Library/Caches/pypoetry/virtualenvs
...
```

* Check the [common noxfile](https://bitbucket-mob.mplatform.co.uk/projects/DLIB/repos/digital-nox/browse/noxfile.py) default sessions (`check_format`, `test`, `bandit`, `osa`) are passing by running:
```
dignox
```

* Run specific session from the [common noxfile](https://bitbucket-mob.mplatform.co.uk/projects/DLIB/repos/digital-nox/browse/noxfile.py) e.g. `build`, `reformat`, `publish`, `package`, `clean` as well as default sessions above:
```
dignox -s build
```

## Setup PyCharm IDE for this project
* Open project in PyCharm. If you open project in a new window PyCharm will setup interpreter for you 
otherwise if you attach project to the other projects, do the step below to add a new interpreter for a project.
* Add python interpreter for this project:
```
In the IDE go to: PyCharm | Preferences | Project: pylibrary-mobile-build-python | Python Interpreter
To add an interpreter, click the settings cog button and choose "Add...".
From the dialog box choose "Poetry Environment" and check "Existing environment".
Interpreter should match pylibrary-mobile-build-python-xxx-py3.7 (the one created by poetry install).
```
* Running the tests in PyCharm should work now.

## Useful commands
Install a new dependency to the poetry virtual environment and automatically add it to pyproject.toml (use this rather than 'pip install' to avoid having to manually update pyproject.toml):
```
poetry add pytest-cov
```

Use the --dev flag to install dependencies that are only needed for development/testing (they will be added to pyproject.toml under tool.poetry.dev-dependencies):
```
poetry add pytest-cov --dev
```

Get the latest versions of all the dependencies and update the poetry.lock file (It is best practise to rerun your unit test after this):
```
poetry update
```

Refresh lock file based on pyproject.toml without updating locked versions:
```
poetry lock --no-update
```

## To test python modules that interact with JIRA, we need to setup our own JIRA API credentials as follows

1. Steps to create a JIRA API token, if you do not already have one:

* Go to https://id.atlassian.com/manage-profile/security/api-tokens 
* Create API Token

2. Store the JIRA credentials into your ~/.zshrc as follows:

```
export JIRA_CLOUD_CREDENTIALS=<your_email_address>:<your_jira_api_token>
```

## To test python modules that interact with Slack, we need to reuse a common Slack BOT token as follows:

1. Get Slack BOT token from AWS Secrets Manager
```
aws secretsmanager get-secret-value --secret-id slack_bot_token --profile mobile-nonprod-admin --query SecretString --output text |jq .slack_bot_token | xargs echo
```
you can also find it here by signing in to appropriate account:

https://eu-west-1.console.aws.amazon.com/secretsmanager/listsecrets?region=eu-west-1&search=all%3Dslack#

2. Store the slack bot token in your ~/.zshrc as follows:

```
export SLACK_BOT_TOKEN=<token_from_secrets_manager>
```

digital-build-scripts/src/main/shell/assume_role.sh --profile rbs-mobile-iam --exporttofile --mfa 996045



Install schedule:
pip install schedule
Install pylibrary: pylibrary is a collection of Python utilities. If you're using the pylibraryaws module, you'll need to install the pylibrary package. You can do this via:
pip install pylibrary
Install slack-sdk: The slack-sdk is the official SDK provided by Slack to interact with their APIs. Install it using:
pip install slack-sdk
