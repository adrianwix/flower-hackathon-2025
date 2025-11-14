# Flower Hackathon - Radiology Review System

A comprehensive application for managing patient health records with AI-assisted X-ray pathology detection, built for a hackathon using Federated Learning with Flower.

## 🏥 Overview

This system provides:
- **Patient & X-ray Management**: Full data model for patients, exams, and X-ray images
- **AI-Assisted Diagnosis**: ML model predictions for 14 pathology types
- **Doctor Review Workflow**: Human-in-the-loop validation (AI Act compliant)
- **Federated Learning Ready**: Integration with Flower framework for privacy-preserving ML
- **RESTful API**: FastAPI backend with SQLModel/PostgreSQL
- **Modern UI**: React frontend (in development)

Based on the NIH Chest X-ray dataset: https://www.kaggle.com/datasets/nih-chest-xrays/data/data

## 📁 Project Structure

```
flower-hackathon/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # SQLModel database models
│   ├── database.py        # Database configuration
│   ├── model_service.py   # ML prediction service (mock)
│   ├── init_db.py         # Database initialization script
│   ├── example_usage.py   # Usage examples
│   └── pyproject.toml     # Python dependencies
├── coldstart/             # Federated Learning implementation
│   ├── evaluate.py
│   └── cold_start_hackathon/
│       ├── client_app.py
│       ├── server_app.py
│       └── task.py
├── ui/                    # React frontend
│   └── src/
├── DATA_MODEL.md          # Complete database schema documentation
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (for UI)
- (Optional) CUDA GPU for future PyTorch model training

### Backend Setup

1. **Install API dependencies:**
```bash
cd api
pip install -e .
```

2. **Set up PostgreSQL database:**
```bash
# Create database
createdb radiology_review

# Or use custom connection string
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

3. **Initialize database:**
```bash
python init_db.py
```

4. **Run the API:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access API documentation:**
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

```bash
cd ui
npm install
npm run dev
```

## 📊 Data Model

The system implements a comprehensive medical imaging data model with:

### Core Entities
- **User**: Doctors and administrators
- **Patient**: Patient demographics and IDs
- **Exam**: Imaging sessions/visits
- **Image**: X-ray images (stored as bytea in PostgreSQL)

### ML & Review Workflow
- **Pathology**: Master table of disease codes (14 NIH classes + "No Finding")
- **ModelVersion**: ML model versions (FL rounds/snapshots)
- **ImagePredictedLabel**: AI predictions with probabilities
- **DoctorLabel**: Human validation labels (AI Act: human in the loop)

### Review Status Workflow
```
pending → in_review → completed
```

See [DATA_MODEL.md](DATA_MODEL.md) for complete SQL schema.

## 🤖 Model Prediction

### Current Implementation (Mock)

The system includes a **mock prediction service** that simulates ML predictions:

```python
from model_service import get_model

model = get_model()
predictions = model.predict_all(image_bytes, threshold=0.5)
```

### Prediction Types

1. **Binary Classification**: Finding vs No Finding
   - Single probability output
   - Threshold-based decision

2. **Multi-Label Classification**: 14 Pathology Types
   - Atelectasis, Cardiomegaly, Effusion, Infiltration
   - Mass, Nodule, Pneumonia, Pneumothorax
   - Consolidation, Edema, Emphysema, Fibrosis
   - Pleural Thickening, Hernia

### Future: Real PyTorch Model

To replace the mock with a trained model:

1. **Train on NIH Dataset**:
```python
import torchvision.models as models

model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 14)  # 14 pathology classes
# Train on NIH Chest X-ray dataset
```

2. **Update `model_service.py`**:
   - Implement `_load_model()` to load trained weights
   - Update `preprocess_image()` with proper transforms
   - Replace mock predictions with actual inference

3. **Integrate with Flower**:
   - Use FL to train across multiple sites
   - Preserve patient privacy
   - Track model versions per FL round

## 🔌 API Endpoints

### Predictions
```bash
# Predict on uploaded image (no storage)
POST /predict
  - file: image file
  - threshold: float (default: 0.5)

# Predict on stored image (save to DB)
POST /images/{image_id}/predict
  - threshold: float
  - model_version_name: string

# List pathologies
GET /pathologies

# List model versions
GET /model-versions
```

### Example Usage

```bash
# Upload and predict
curl -X POST "http://localhost:8000/predict?threshold=0.5" \
  -F "file=@xray.png"

# Predict stored image
curl -X POST "http://localhost:8000/images/1/predict?threshold=0.5"
```

## 🧪 Example Code

Run the example script to see the system in action:

```bash
cd api
python example_usage.py
```

This demonstrates:
- Creating users, patients, exams, and images
- Running predictions
- Querying stored predictions
- Database operations

## 🌸 Federated Learning with Flower

The `coldstart/` directory contains Flower integration for federated learning:

- **Client App**: Local model training on hospital data
- **Server App**: Aggregates model updates from clients
- **Task**: Defines the ML task and data processing

This enables:
- Privacy-preserving training across multiple hospitals
- No central data storage required
- Model improvement through collaborative learning

## 🗄️ Database Schema

Key relationships:
```
User (Doctor)
  └── creates → Exam
                  └── contains → Image
                                   ├── predicted by → ImagePredictedLabel
                                   │                    └── references → Pathology
                                   │                    └── references → ModelVersion
                                   └── reviewed by → DoctorLabel
                                                      └── references → Pathology
                                                      └── labeled by → User
```

## 🛠️ Development

### Adding New Features

1. **New Database Model**: Update `models.py` with SQLModel classes
2. **New Endpoint**: Add to `main.py` with proper type hints
3. **New Prediction Type**: Extend `model_service.py`

### Database Migrations

For schema changes:
```bash
# Drop and recreate (development only)
python init_db.py

# Or use Alembic for production migrations
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📦 Dependencies

### Backend (Python)
- **FastAPI**: Modern web framework
- **SQLModel**: SQL databases with Pydantic models
- **PostgreSQL**: Relational database
- **PyTorch**: Deep learning framework (for future model)
- **Pillow**: Image processing
- **Flower**: Federated learning framework

### Frontend (TypeScript)
- **React**: UI framework
- **Vite**: Build tool
- **TypeScript**: Type safety

## 🚢 Deployment

### Docker
```bash
# Build
docker build -t radiology-api ./api

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  radiology-api
```

### Render.com
The project includes `render.yaml` for easy deployment to Render.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📚 Resources

- **NIH Chest X-ray Dataset**: https://www.kaggle.com/datasets/nih-chest-xrays/data/data
- **Flower Framework**: https://flower.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/

## 🏆 Hackathon Goals

- ✅ Implement complete data model with SQLModel
- ✅ Create mock prediction service (PyTorch-ready)
- ✅ Build RESTful API with FastAPI
- ⏳ Integrate real PyTorch model
- ⏳ Implement Flower federated learning
- ⏳ Build React UI for doctor review workflow
- ⏳ Deploy to cloud platform

---

Built with ❤️ for the Flower Hackathon 2025
