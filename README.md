# FastAPI Facebook Creatives API

A FastAPI project that integrates with the Facebook Marketing API to fetch, process, and expose creative data. The API aggregates performance metrics, supports features such as token refresh and deduplication, and integrates with Google Cloud Vision for creative feature analysis. This project can be run locally, with Docker, or deployed to Heroku.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Live Demo](#live-demo)
- [Additional Notes](#additional-notes)
- [Future Improvements](#future-improvements)

## Features

- Fetches creative data from the Facebook Marketing API.
- Aggregates performance metrics (impressions, clicks, spend, conversions, CTR).
- Deduplicates creatives by image hash.
- Supports pagination and keyset-based pagination endpoints.
- Integrates with Google Cloud Vision API for feature analysis.
- Uses environment variables for configuration and secrets.

## Installation

### Local Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/fastapi-facebook-creatives.git
   cd fastapi-facebook-creatives

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt

4. **Set up environment variables:**

    Create a .env file in the root directory (see #configuration below).

5. **Run the FastAPI app:**

    ```bash
    uvicorn app.main:app --reload

The application will be available at http://localhost:8000

## Configuration
    The application uses environment variables to configure secrets and API URLs. Create a .env file in the root directory and add your credentials:

    # .env

    ACCESS_TOKEN=your_facebook_access_token
    API_VERSION=v22.0
    CLIENT_ID=your_facebook_app_id
    CLIENT_SECRET=your_facebook_app_secret
    FB_API_URL=https://graph.facebook.com
    DB_URL=mssql+pytds://admin:your_db_password@database-1.your-region.rds.amazonaws.com:1433/your_db_name

## Usage
    Once the application is running, you can use the following endpoints:

 - **GET /fetch-fb-and-store-best-creatives**
    Fetches best performing creatives from the FB API,
    Processes and returns the best creatives sorted by performance metrics.

 - **GET /api/creatives**
    Returns a paginated list of creatives using keyset pagination. Supported query parameters:

    cursor: The last creative id from the previous page (for keyset pagination).

    limit: Maximum number of records to return.

## Live Demo
    http://creatives-api-a56231c8c35c.herokuapp.com/api/creatives

## Additional Notes
 - **CORS:**
    The API uses CORSMiddleware to allow requests from trusted origins (configured in app/main.py).

 - **Secrets Management:**
    All secrets (API keys, database credentials, etc.) are loaded from environment variables. Avoid committing sensitive information to version control.

 - **Database:**
    The project uses SQLAlchemy to interact with a MSSQL database. Ensure your DB_URL is correct and that the necessary drivers are installed.

 - **Google Cloud Credentials:**
    To use the Google Cloud Vision API, the service account JSON is stored in an environment variable (GCLOUD_CREDENTIALS). At runtime, this JSON is written to a temporary file and the GOOGLE_APPLICATION_CREDENTIALS variable is set accordingly.


## Future Improvements

- **Monitoring & Logging:**  
  Integrate tools for monitoring and centralized logging.

- **CI/CD Integration:**  
  Set up automated testing and deployment pipelines for continuous integration.

- **Testing:**  
  Develop tests using Pytest and HTTPX for backend endpoints.  
  This will include unit tests to ensure overall application functionality.

- **API Authentication:**  
  Add authentication and authorization for API endpoints.  
  This could involve implementing Cognito, OAuth2, API keys, or JWT-based authentication to secure access to sensitive endpoints and data.


