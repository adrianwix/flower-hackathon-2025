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

### Option 1: Deploy via Dashboard

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

### Option 2: Deploy via Blueprint (render.yaml)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Blueprint"
3. Connect your repository and select the `api/render.yaml` file
4. Review and create the service

### Free Tier

Render's free tier includes:
- 750 hours/month of running time
- Services spin down after 15 minutes of inactivity
- Automatic SSL certificates
- Custom domains support

Note: Free tier services may experience cold starts (15-30 second delay) after periods of inactivity.
