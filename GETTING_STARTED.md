# Getting Started Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd api
pip install -e .
```

This installs:
- FastAPI (web framework)
- SQLModel (database ORM)
- PostgreSQL driver
- PyTorch & torchvision (for model)
- Pillow (image processing)
- And more...

### 2. Test Implementation (No Database Required)

```bash
python test_implementation.py
```

This verifies:
- ✓ All imports work
- ✓ Enums are defined correctly  
- ✓ Mock model can make predictions
- ✓ Image validation works
- ✓ Singleton pattern works

**Expected output:**
```
Quick Implementation Test (No Database Required)
============================================================
Testing imports...
✓ models.py imports successful
✓ model_service.py imports successful
...
🎉 All tests passed! Implementation is working correctly.
```

### 3. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo service postgresql start

# Create database
sudo -u postgres createdb postgres

# Set environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
```

#### Option B: Docker PostgreSQL

```bash
docker run -d \
  --name radiology-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  postgres:15
  
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
```

#### Option C: Cloud Database (Render, Supabase, etc.)

Get your DATABASE_URL from your cloud provider and set it:
```bash
export DATABASE_URL="your_database_url_here"
```

### 4. Initialize Database

```bash
python init_db.py
```

This creates:
- All database tables
- Seeds 16 pathology codes (NO_FINDING, ANY_PATHOLOGY, + 14 NIH classes)

**Expected output:**
```
Creating database tables...
✓ Tables created successfully

Initializing pathologies...
✓ Pathologies initialized

Database initialization complete!
```

### 5. Run Example Usage (Optional)

```bash
python example_usage.py
```

This demonstrates:
- Creating a doctor, patient, exam, and image
- Running predictions
- Storing predictions in database
- Querying stored predictions

### 6. Start API Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Test API

Open your browser to:
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

Or use curl:
```bash
# Health check
curl http://localhost:8000/health

# List pathologies
curl http://localhost:8000/pathologies

# Upload and predict
curl -X POST "http://localhost:8000/predict?threshold=0.5" \
  -F "file=@path/to/xray.png"
```

## Common Issues & Solutions

### Issue: "Import sqlmodel could not be resolved"

**Solution:** Dependencies not installed
```bash
cd api
pip install -e .
```

### Issue: "Connection refused" when connecting to database

**Solution:** PostgreSQL not running or wrong connection string
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Or start it
sudo service postgresql start

# Verify connection string
echo $DATABASE_URL
```

### Issue: "relation does not exist" errors

**Solution:** Database not initialized
```bash
python init_db.py
```

### Issue: "Permission denied" on PostgreSQL

**Solution:** Update connection string with correct credentials
```bash
export DATABASE_URL="postgresql://your_user:your_password@localhost:5432/postgres"
```

### Issue: "Module not found" errors

**Solution:** Make sure you're in the api directory and installed dependencies
```bash
cd api
pip install -e .
```

## Environment Variables

Create a `.env` file in the `api/` directory:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
API_HOST=0.0.0.0
API_PORT=8000
```

Load it before running:
```bash
source .env  # or use python-dotenv
uvicorn main:app --reload
```

## Development Workflow

### 1. Make Changes to Models

Edit `api/models.py`:
```python
class NewModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # ... your fields
```

### 2. Update Database

```bash
python init_db.py  # Recreates tables (development only!)
```

### 3. Add API Endpoints

Edit `api/main.py`:
```python
@app.get("/new-endpoint")
async def new_endpoint(session: Session = Depends(get_session)):
    # Your logic here
    return {"result": "data"}
```

### 4. Test

```bash
# Restart server (with --reload, it auto-restarts)
# Visit http://localhost:8000/docs
# Test your new endpoint
```

## Using Real Images

### NIH Chest X-ray Dataset

1. **Download** from Kaggle:
   https://www.kaggle.com/datasets/nih-chest-xrays/data/data

2. **Extract** the images

3. **Upload via API**:
```python
import requests

with open('path/to/xray.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    )
    print(response.json())
```

### Creating Image Records

```python
from sqlmodel import Session
from database import engine
from models import Image, Exam

with Session(engine) as session:
    # Read image file
    with open('xray.png', 'rb') as f:
        image_bytes = f.read()
    
    # Create image record
    image = Image(
        exam_id=1,  # Use existing exam ID
        filename='xray.png',
        image_bytes=image_bytes,
        mime_type='image/png',
    )
    session.add(image)
    session.commit()
    
    print(f"Created image ID: {image.id}")
```

## Replacing Mock Model with Real PyTorch Model

### 1. Train or Download Model

```python
# train_model.py
import torch
import torchvision.models as models

# Create model
model = models.resnet50(pretrained=True)
model.fc = torch.nn.Linear(model.fc.in_features, 14)  # 14 NIH classes

# Train on NIH dataset
# ... training code ...

# Save weights
torch.save(model.state_dict(), 'xray_model.pth')
```

### 2. Update model_service.py

```python
def _load_model(self) -> nn.Module:
    """Load trained model"""
    import torchvision.models as models
    
    model = models.resnet50(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, 14)
    model.load_state_dict(torch.load('xray_model.pth'))
    model.eval()
    return model.to(self.device)
```

### 3. Update Preprocessing

```python
def preprocess_image(self, image_bytes: bytes) -> torch.Tensor:
    """Preprocess with proper transforms"""
    from torchvision import transforms
    
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], 
                           [0.229, 0.224, 0.225])
    ])
    
    return transform(img)
```

### 4. Update Predictions

```python
def predict_multi_label(self, image_bytes: bytes, threshold: float = 0.5):
    """Real predictions"""
    tensor = self.preprocess_image(image_bytes)
    
    with torch.no_grad():
        outputs = self.model(tensor.unsqueeze(0).to(self.device))
        probabilities = torch.sigmoid(outputs).cpu().numpy()[0]
    
    results = {}
    pathologies = ["ATELECTASIS", "CARDIOMEGALY", ...]
    for i, pathology in enumerate(pathologies):
        prob = float(probabilities[i])
        results[pathology] = (prob >= threshold, prob)
    
    return results
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Example payloads
- Try-it-out functionality

## Production Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.11

WORKDIR /app
COPY api/ /app/

RUN pip install -e .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t radiology-api .
docker run -p 8000:8000 \
  -e DATABASE_URL="your_db_url" \
  radiology-api
```

### Render.com

The `render.yaml` is already configured. Just:
1. Connect your GitHub repo
2. Set DATABASE_URL environment variable
3. Deploy

## Next Steps

- [ ] Integrate with Flower for federated learning
- [ ] Build React frontend (see `ui/` folder)
- [ ] Add authentication/authorization
- [ ] Implement doctor review workflow endpoints
- [ ] Add image upload/download endpoints
- [ ] Train real PyTorch model on NIH dataset
- [ ] Add unit tests with pytest
- [ ] Add API rate limiting
- [ ] Add logging and monitoring

## Support

For issues:
1. Check this guide
2. Check `API_README.md` for detailed API docs
3. Check `IMPLEMENTATION.md` for technical details
4. Review `DATA_MODEL.md` for schema documentation

Happy coding! 🚀
