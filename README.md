# Medical AI Assistant Prototype with Personalized FL 


📊 [View Project Presentation](./docs/Presentation1.pdf)


A prototype proposing a federated learning system that combines Personalized FL for privacy-preserving training across hospitals with a Mixture of Experts approach at inference, applied to AI-assisted X-ray pathology detection.


## Problem: 

* Medical data is highly sensitive and legally protected, which makes large-scale centralized model training challenging

* At the same time it is strongly heterogeneous and non-IID: different patient groups, health conditions, devices, workflows, and labeling—so advanced approaches are necessary. 

## Solutions

We explore a real-life solution through two key objectives:

### Objective 1: Personalized Federated Learning for Non-IID Data

Use **Personalized FL** to handle heterogeneous medical data across hospitals. Each site maintains personalized model adaptations while benefiting from collaborative learning using algorithms like FedProx, preserving privacy and accounting for local data distributions.

### Objective 2: Mixture of Experts at Inference

Employ a **Mixture of Experts (MoE)** approach that intelligently combines predictions from multiple specialized models based on patient characteristics, routing each X-ray to the most appropriate experts for improved diagnostic accuracy.

Inspired by ["Personalized Federated Learning via Mixture of Experts with Abductive Learning"](https://www.ijcai.org/proceedings/2025/0610.pdf) (IJCAI 2025).

📊 [View Project Presentation](./docs/Presentation1.pdf)


## 🏥 Overview

This prototype system demonstrates:
- **AI-Assisted Diagnosis**: Multi-label classification for 14 pathology types from chest X-rays
- **Doctor Review Workflow**: Human-in-the-loop validation (AI Act compliant)
- **Full Stack Implementation**: FastAPI backend with SQLModel/PostgreSQL, React frontend, complete patient/exam/image data model
- **Federated Learning**: Implemented by exploring non-IID targeting strategies (FedProx, FedDyn), and comparing use of different models 

- **Personalized Federated Learning**: 🚧 In progress 
- **Mixture of Experts Inference**: 🚧 Proposed approach for future implementation (not implemented due to time limitations) 


Based on the NIH Chest X-ray dataset: https://www.kaggle.com/datasets/nih-chest-xrays/data/data


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
createdb postgres

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

