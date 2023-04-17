# prefect-project-deploy (WORK IN PROGRESS)
## Details
A Github Action to deploy one or more of your Prefect flow deployments via [Prefect Projects](https://docs.prefect.io/latest/concepts/projects/#projects)

## Requirements
- Access to a [Prefect Cloud Account](https://docs.prefect.io/latest/ui/cloud/#welcome-to-prefect-cloud)
- [Checkout](https://github.com/actions/checkout), [Setup Python](https://github.com/actions/setup-python), & [Docker Login](https://github.com/marketplace/actions/docker-login)/Cloud Docker Registry Login (If building and pushing a Docker artifact)

## Inputs
| Input | Desription | Required | Default |
|-------|------------|----------|---------|
| additional-args | Any additional arguments to pass to the Prefect Deploy command. Available additional arguments are listed below | false | |
| entrypoint | The path to a flow entrypoint within a project, in the format of: `./path/to/file.py:flow_func_name` | true | |
| name | A name to give the deployment | true | |
| prefect-api-key | A Prefect Cloud API Key | true | |
| prefect-workspace | Full handle of workspace, in the format of: `<account_handle>/<workspace_handle>` | true | |
| requirements-file-path | Path to requirements files to correctly install dependencies for your Prefect flow(s) |  true | ./requirements.txt
| work-pool | The work pool that will handle this deployment's runs | true | |
| work-queue | The work queue that will handle this deployment's runs | false | `default` |

## Examples
### Simple Prefect Deploy
Deploy a Prefect flow that doesn't have a `push` step defined in the `prefect.yaml`
```yaml
name: Deploy a Prefect Deployment
on:
  push:
    branches:
      - main
jobs:
  deploy-flow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: checkout@v3

      - name: Setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run Prefect Deploy
        uses: PrefectHQ/prefect-project-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}
          name: simple-deployment
          requirements-file: ./examples/simple/requirements.txt
          work-pool: simple-pool
          entrypoint: ./examples/simple/flow.py:call_api
          additional-args: --cron "30 19 * * 0"
```
### Basic Docker Auth w/ Prefect Deploy
Deploy a Prefect Deployment and also build a Docker image that pushes to a defined repository in the `prefect.yaml` file.
```yaml
name: Build an Image and Deploy a Prefect Deployment
on:
  push:
    branches:
      - main
jobs:
  deploy-flow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: checkout@v3

      - name: Setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/prefect-project-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}
          name: basic-docker-auth-deployment
          requirements-file: ./examples/docker/requirements.txt
          work-pool: docker-pool
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron "30 19 * * 0"
```
### GCP Workload Identity w/ Prefect Deploy
Deploy a Prefect Deployment and also build a Docker image that pushes to a defined repository in the `prefect.yaml` file.
```yaml
name: Build an Image and Deploy a Prefect Deployment
on:
  push:
    branches:
      - main
jobs:
  deploy-flow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: checkout@v3

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: projects/<project_id>/locations/global/workloadIdentityPools/<pool-name>/providers/<provider-name>
          service_account: <gcp_service_account>@<project_id>.iam.gserviceaccount.com

      - name: Configure Google Cloud credential helper
        run: gcloud auth configure-docker --quiet us-docker.pkg.dev

      - name: Setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run Prefect Deploy
        uses: PrefectHQ/prefect-project-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}
          name: gcp-workload-identity-auth-deployment
          requirements-file: ./examples/docker/requirements.txt
          work-pool: docker-pool
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron "30 19 * * 0"
```
## Additional Arguments
| Arg Name      | Description                                                                                                             |
|---------------|-------------------------------------------------------------------------------------------------------------------------|
| --work-queue  | The work queue that will handle this deployment's runs. It will be created if it doesn't already exist. Defaults to `None`. |
| --flow        | The name of a registered flow to create a deployment for. (Use in place of an entrypoint)                               |
| --description | The description to give the deployment. If not provided, the description will be populated from the flow's description. |
| --version     | A version to give the deployment.                                                                                       |
| --tag         | One or more optional tags to apply to the deployment. Note: tags are used only for organizational purposes.             |
| --variable    | One or more job variable overrides for the work pool provided in the format of key=value                                |
| --cron        | A cron string that will be used to set a CronSchedule on the deployment.                                                |
| --interval    | An integer specifying an interval (in seconds) that will be used to set an IntervalSchedule on the deployment.          |
| --anchor-date | The anchor date for an interval schedule                                                                                |
| --rrule       | An RRule that will be used to set an RRuleSchedule on the deployment.                                                   |
| --timezone    | Deployment schedule timezone string e.g. 'America/New_York'                                                             |
| --param       | An optional parameter override, values are parsed as JSON strings e.g. --param question=ultimate --param answer=42      |
| --params      | An optional parameter override in a JSON string format e.g. --params='{"question": "ultimate", "answer": 42}'           |
