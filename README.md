# actions-prefect-deploy

## Details

A Github Action to deploy a Prefect flow via [Prefect Projects](https://docs.prefect.io/latest/concepts/projects/#projects). Note - all configuration defined in your `deployment.yaml` will be infered at run time; this means you do **not** need to duplicate cli arguments that are already defined. For example, if your `deployment.yaml` looks like: 
```yaml
description: null
entrypoint: examples/simple/flow.py:call_api
flow_name: null
name: Simple
parameters: {}
schedule: null
tags: []
version: null
work_pool:
  job_variables:
    image: prefecthq/prefect:2-latest
  name: simple-pool
  work_queue_name: null
```
You will not need to pass your work-pool name or the deployment name to this action.

## Requirements

- Access to a [Prefect Cloud Account](https://docs.prefect.io/latest/ui/cloud/#welcome-to-prefect-cloud)
- [Checkout](https://github.com/actions/checkout) - to clone the repo
- [Setup Python](https://github.com/actions/setup-python) - to install prefect & other requirements
- [Prefect Auth](https://github.com/PrefectHQ/actions-prefect-auth) - to log into Prefect Cloud
- (optional) [Docker Login](https://github.com/marketplace/actions/docker-login) / Cloud Docker Registry Login if building and pushing a Docker artifact

## Inputs

| Input | Desription | Required | Default |
|-------|------------|----------|---------|
| additional-args | Any additional arguments to pass to the Prefect Deploy command. Available additional arguments are listed below. | false | |
| entrypoint | The path to a flow entrypoint within a project, in format: `./path/to/file.py:flow_func_name`. | true | |
| requirements-file-path | Path to requirements files to correctly install dependencies for your Prefect flow. | false | `./requirements.txt` |

## Examples

### Simple Prefect Deploy

Deploy a Prefect flow that doesn't have a `push` step defined in the `prefect.yaml`
```yaml
name: Deploy a Prefect flow
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    runs-on: ubuntu-latest
    steps:
      - uses: checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Prefect Auth
        uses: PrefectHQ/actions-prefect-auth@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v1
        with:
          requirements-file-path: ./examples/simple/requirements.txt
          entrypoint: ./examples/simple/flow.py:call_api
          additional-args: --cron '30 19 * * 0'
```
### Basic Docker Auth w/ Prefect Deploy

Deploy a Prefect flow and also build a Docker artifact that pushes to a defined repository in the `prefect.yaml` file.
```yaml
name: Build an Image and Deploy a Prefect flow
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    runs-on: ubuntu-latest
    steps:
      - uses: checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Prefect Auth
        uses: PrefectHQ/actions-prefect-auth@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v1
        with:
          requirements-file-path: ./examples/docker/requirements.txt
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron '30 19 * * 0' --pool docker-pool
```
### GCP Workload Identity w/ Prefect Deploy

Deploy a Prefect flow and also build a Docker artifact that pushes to a defined repository in the `prefect.yaml` file.
```yaml
name: Build an Image and Deploy a Prefect flow
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    permissions:
      # required to obtain Google Cloud service account credentials
      id-token: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: projects/<project_id>/locations/global/workloadIdentityPools/<pool-name>/providers/<provider-name>
          service_account: <gcp_service_account>@<project_id>.iam.gserviceaccount.com

      - name: Configure Google Cloud credential helper
        run: gcloud auth configure-docker --quiet us-east1-docker.pkg.dev

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Prefect Auth
        uses: PrefectHQ/actions-prefect-auth@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v1
        with:
          requirements-file-path: ./examples/docker/requirements.txt
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron '30 19 * * 0' --pool docker-pool
```
## Additional Arguments

| Arg Name | Description | Example |
|----------|-------------|---------|
| --anchor-date | The anchor date for an interval schedule. | |
| --cron | A cron string that will be used to set a CronSchedule on the deployment. | `--cron '30 19 * * 0' `|
| --description | The description to give the deployment. If not provided, the description will be populated from the flow's description. | |
| --interval | An integer specifying an interval (in seconds) that will be used to set an IntervalSchedule on the deployment. | `--interval 60` |
| --name | The name to give the deployment. | `--name 'Test Flow'` |
| --param | An optional parameter override, values are parsed as JSON strings | `--param question=ultimate --param answer=42` |
| --params | An optional parameter override in a JSON string format. | `--params='{"question": "ultimate", "answer": 42}'` |
| --pool | The work pool that will handle this deployment's runs. | `--pool docker-pool` |
| --rrule | An RRule that will be used to set an RRuleSchedule on the deployment. | |
| --tag | One or more optional tags to apply to the deployment - Note: tags are used only for organizational purposes. | |
| --timezone | Deployment schedule timezone string. | `--timezone 'America/New_York'` |
| --variable | One or more job variable overrides for the work pool. | `--variable foo=bar` |
| --version | A version to give the deployment. | |
| --work-queue | The work queue that will handle this deployment's runs. It will be created if it doesn't already exist. | `--work-queue test` |

## Terms & Conditions
See here for the Prefect's [Terms and Conditions](https://www.prefect.io/legal/terms/).
