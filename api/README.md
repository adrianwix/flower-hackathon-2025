# Flower Hackathon API

FastAPI server for the Flower Hackathon project.

## Local Development

1. Install dependencies:
```bash
uv sync
```

2. Run the server:
```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Deployment on Render

### Option 1: Deploy Both Services via Blueprint (Recommended)

A `render.yaml` file is located at the **root of the repository** that configures both the API and UI for deployment.

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Blueprint"
3. Connect your repository and Render will detect the `render.yaml` file
4. Review the services:
   - **flower-hackathon-api**: FastAPI backend
   - **flower-hackathon-ui**: React frontend (static site)
5. Click "Apply" to deploy both services

### Option 2: Deploy API Only via Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: flower-hackathon-api
   - **Root Directory**: `api`
   - **Environment**: Python 3
   - **Build Command**: `pip install uv && uv sync`
   - **Start Command**: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"

### Environment Variables

After deployment, you may want to configure CORS in the API to allow requests from your frontend domain. Update the `allow_origins` in `main.py` with your deployed UI URL.

### Free Tier

Render's free tier includes:
- 750 hours/month of running time
- Services spin down after 15 minutes of inactivity
- Automatic SSL certificates
- Custom domains support

Note: Free tier services may experience cold starts (15-30 second delay) after periods of inactivity.
