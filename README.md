## Instructions for set-up
### 1. Clone this repository:
```
git clone https://github.com/IDinsight/experiments-engine.git
```

### 2. Make environment files

Navigate to `deployment/docker-compose`. Copy the template `.env` files to create a `.base.env` and `.backend.env` files

### 3. Set-up a conda environment

Navigate to the root of this repository and run `make fresh-env`

### 4. Run the app:

  There are a couple of ways you can do this:

  #### a. For local development:

  To install the necessary dependencies in the root directory run the commands:

  `conda activate exp_engine` to activate virtual environment.

  `pip install -r requirements-dev.txt` to install development dependencies.

  `pip install -r requirements-docs.txt` to install docs-related tools.

  Move to backend folder and install backend dependencies:

  `cd backend`

  `pip install -r requirements.txt`

  Now, move to frontend folder to install frontend dependencies:

  `cd ../frontend`

  `npm install`

  From the root of the repository run `make run-backend`, and in a separate terminal session `make run-frontend`.

  #### b. For dev Docker deployment:

  From the root of the repository run `make dev-inst-start`. This will start the following containers:

  - _backend_: This is the container that runs the FastAPI app. You can access the Swagger UI on `localhost/api/docs` (Depending on BACKEND_ROOT_PATH in `.base.env`)
  - _caddy_: This is the container that runs Caddy reverse proxy for the app. All the requests are routed via Caddy
  - _relational_db_: Postgres DB for the ExE app
  - _frontend_: Admin app front end
  - _redis_: Redis in memory-store for the ExE app

  You will find the app running on `localhost` now. By default (based on default values in `Caddyfile` and `.base.env`) you can access

  - `https://localhost` for the frontend
  - `https://localhost/api/docs` for API documentation


  You can make changes to the "backend" or "frontend" code, and changes will be reflected instantly in the deployed containers when you save the file.

  To stop the application run `make dev-inst-stop`. To restart, run `make dev-inst-restart` after changing env variables. To restart after deleting Docker images and orphan containers, do `dev-inst-soft-reset`. To restart after deleting images, containers and volumes, do `dev-inst-hard-reset`.

  #### c. For prod Docker deployment:

  You can run `server-*` commands (following the same naming convention as for the dev Docker deployments above, for the corresponding functionality).

  There's no hot reload for prod deployments.

### 4. Explore!
Log in with the admin credentials and experiment :)
