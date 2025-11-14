# Radiology Review API

FastAPI-based API for managing patient health records with a focus on X-ray analysis and AI-assisted pathology detection.

## Features

- **SQLModel-based data models** matching the PostgreSQL schema
- **Mock ML prediction service** for X-ray pathology detection (PyTorch-ready)
- **RESTful API endpoints** for image predictions
- **Database integration** with PostgreSQL
- **NIH Chest X-ray dataset support** with 14 pathology classes

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- (Optional) CUDA-capable GPU for future PyTorch model

### Installation

1. Install dependencies:
```bash
pip install -e .
```

2. Set up database connection (optional - defaults to local PostgreSQL):
```bash
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

3. Initialize the database:
```bash
python init_db.py
```

### Running the API

Start the development server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with API info
- `GET /health` - Health check

### Predictions
- `POST /predict` - Predict pathologies for an uploaded X-ray image
  - Upload file: X-ray image (PNG, JPEG)
  - Query params: `threshold` (default: 0.5)
  - Returns: Predictions without saving to database

- `POST /images/{image_id}/predict` - Run prediction on stored image
  - Path params: `image_id`
  - Query params: `threshold`, `model_version_name`
  - Saves predictions to database

### Data
- `GET /pathologies` - List all available pathology codes
- `GET /model-versions` - List all model versions

## Data Model

The application uses SQLModel (Pydantic + SQLAlchemy) with the following main entities:

- **User** - Doctors and administrators
- **Patient** - Patient records
- **Exam** - Imaging sessions
- **Image** - X-ray images (stored as bytea in PostgreSQL)
- **Pathology** - Master table of pathology codes
- **ModelVersion** - ML model versions (FL rounds)
- **ImagePredictedLabel** - ML predictions
- **DoctorLabel** - Human validation labels

See `DATA_MODEL.md` for the complete schema.

## Model Prediction

The current implementation uses a **mock model** (`MockXRayModel`) that returns random predictions for demonstration purposes.

### Binary Classification
- **Task**: Detect if there is ANY finding (pathology) in the X-ray
- **Output**: Boolean prediction + probability

### Multi-Label Classification
- **Task**: Detect specific pathologies from the NIH dataset
- **Classes**: 14 pathology types
  - Atelectasis, Cardiomegaly, Effusion, Infiltration
  - Mass, Nodule, Pneumonia, Pneumothorax
  - Consolidation, Edema, Emphysema, Fibrosis
  - Pleural Thickening, Hernia

### Future Implementation

To replace the mock with a real PyTorch model:

1. Train a model on the NIH Chest X-ray dataset
2. Save model weights
3. Update `MockXRayModel._load_model()` to load your trained model
4. Update `preprocess_image()` with proper transforms
5. Update prediction methods to use actual model inference

Example model architectures:
```python
import torchvision.models as models

# ResNet
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)

# DenseNet
model = models.densenet121(pretrained=True)
model.classifier = nn.Linear(model.classifier.in_features, num_classes)
```

## Database Configuration

Default connection string:
```
postgresql://postgres:postgres@localhost:5432/radiology_review
```

Set custom connection via environment variable:
```bash
export DATABASE_URL="your_connection_string"
```

## NIH Chest X-ray Dataset

This application is designed to work with the NIH Chest X-ray dataset:
- **Source**: https://www.kaggle.com/datasets/nih-chest-xrays/data/data
- **Size**: 112,120 X-ray images
- **Classes**: 14 disease labels + "No Finding"
- **Format**: PNG images

## Development

### Project Structure
```
api/
├── main.py              # FastAPI application and endpoints
├── models.py            # SQLModel database models
├── database.py          # Database configuration and initialization
├── model_service.py     # ML model prediction service (mock)
├── init_db.py          # Database initialization script
├── pyproject.toml      # Python dependencies
└── README.md           # This file
```

### Adding New Endpoints

1. Import necessary models and dependencies in `main.py`
2. Create endpoint function with proper type hints
3. Use `Depends(get_session)` for database access
4. Return Pydantic models or dictionaries

### Extending the Model

To add new prediction capabilities:

1. Update `model_service.py` with new prediction methods
2. Update database models if needed (e.g., new pathology types)
3. Create corresponding API endpoints in `main.py`

## Docker Deployment

The API includes `render.yaml` for deployment to Render.com or similar platforms.

## License

MIT License - see LICENSE file for details.
