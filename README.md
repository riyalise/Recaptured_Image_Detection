# Recaptured_Image_Detection
Deep learning-based recaptured image detection system using ResNet-50, Flask, and a custom confidence-based decision engine for image authenticity verification.
# Recaptured Image Detection System Using ResNet-50

## Overview

The **Recaptured Image Detection System** is an end-to-end deep learning application designed to determine whether an image is an original digital image or a recaptured photograph (a photograph taken of another image displayed on a screen or printed medium).

Recaptured image detection is an important problem in digital image forensics, document verification, anti-spoofing systems, biometric security, and media authenticity analysis.

This project combines **Computer Vision**, **Deep Learning**, **Transfer Learning**, **Flask API Development**, and **Frontend Engineering** to create a deployable image authenticity verification system.

---

## Problem Statement

Digital images can be manipulated by displaying them on a screen and photographing them again. Such recaptured images often bypass traditional image verification methods.

The objective of this project is to automatically classify images into:

* **Original Image**
* **Photo of Photo (Recaptured Image)**

while providing confidence-based decision support and manual review recommendations for uncertain cases.

---

# Key Features

### Deep Learning Based Detection

* Transfer Learning using ResNet-50
* Binary Image Classification
* Robust augmentation pipeline
* Class imbalance handling

### Production-Oriented Deployment

* Flask REST API
* Responsive Web Interface
* Drag-and-Drop Image Upload
* Real-time Prediction Results

### Reliability Layer

* Confidence-based decision engine
* Manual review zone for uncertain predictions
* Prediction audit logging
* Input validation and error handling

### Dataset Engineering

* Custom image labeling application
* Keyboard-driven annotation workflow
* Automatic dataset organization

---

# System Architecture

```text
                    User
                      │
                      ▼
          Frontend (HTML/CSS/JS)
                      │
                      ▼
                Flask API
                      │
                      ▼
            Image Validation
                      │
                      ▼
              Preprocessing
                      │
                      ▼
             ResNet-50 Model
                      │
                      ▼
          Probability Prediction
                      │
                      ▼
             Decision Engine
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
  ACCEPT      MANUAL REVIEW     REJECT
 (Original)    (Uncertain)   (Recaptured)
                      │
                      ▼
          Logging + API Response
```

---

# Project Structure

```text
Recaptured_Image_Detection/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── main.js
│
├── src/
│   ├── architecture.py
│   ├── predictor.py
│   ├── transforms.py
│   └── logger.py
│
├── data/
│   ├── uploads/
│   └── logs/
│
├── model/
│   ├── Recaptured_Image_Detection.pth
│   └── results/
│
├── notebook/
│   └── Recaptured_Image_Detection.ipynb
│
├── app.py
├── requirements.txt
└── .env
```

---

# Dataset

The dataset consists of two classes:

| Class          | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| original       | Native digital images                                        |
| photo_of_photo | Recaptured images photographed from screens or printed media |

### Dataset Split

| Set        | Percentage |
| ---------- | ---------- |
| Training   | 70%        |
| Validation | 15%        |
| Testing    | 15%        |

---

# Data Preprocessing


### Purpose

* Improve generalization
* Increase robustness
* Simulate real-world capture conditions
* Reduce overfitting

---

## Evaluation Transform

Used during validation, testing, and deployment.

---

# Model Architecture

## Backbone

**ResNet-50 (ImageNet Pretrained)**

Transfer learning is used to leverage features learned from millions of natural images.

---

# Handling Class Imbalance

Two strategies were implemented:

## 1. Weighted Random Sampling

Training batches are balanced using inverse-frequency sampling.

## 2. Weighted Binary Cross Entropy

```python
BCEWithLogitsLoss(pos_weight=...)
```

This penalizes minority-class errors more heavily.

---

# Training Configuration

| Parameter         | Value               |
| ----------------- | ------------------- |
| Backbone          | ResNet-50           |
| Batch Size        | 64                  |
| Epochs            | 15                  |
| Optimizer         | AdamW               |
| Weight Decay      | 1e-4                |
| Scheduler         | Cosine Annealing LR |
| Early Stopping    | Enabled             |
| Validation Metric | F1 Score            |

---

## Learning Rates

| Layer               | Learning Rate |
| ------------------- | ------------- |
| Layer1 + Layer2     | 5e-6          |
| Layer3 + Layer4     | 1e-5          |
| Classification Head | 1e-4          |

Differential learning rates allow deeper layers to fine-tune gradually while enabling the classifier head to learn faster.

---

# Model Performance

## Test Set Results

| Metric                     | Score  |
| -------------------------- | ------ |
| Accuracy                   | 99.29% |
| Precision (Original)       | 99.88% |
| Recall (Original)          | 99.38% |
| F1 Score (Original)        | 99.63% |
| Precision (Photo of Photo) | 86.84% |
| Recall (Photo of Photo)    | 97.06% |
| F1 Score (Photo of Photo)  | 91.67% |
| Macro F1                   | 95.65% |
| Weighted F1                | 99.31% |
| ROC-AUC                    | 0.9781 |
| Average Precision          | 0.9591 |

---



---

# Confidence-Based Decision Engine

Instead of relying solely on a fixed classification threshold, the deployment system introduces a reliability layer.

## Deployment Thresholds

```text
ACCEPT_THRESHOLD = 0.45
REJECT_THRESHOLD = 0.65
```

### Decision Logic

| Probability Range | Decision      |
| ----------------- | ------------- |
| < 0.45            | ACCEPT        |
| 0.45 – 0.65       | MANUAL REVIEW |
| > 0.65            | REJECT        |

### Why This Helps

Traditional binary classifiers force every prediction into one class.

The uncertainty zone allows the system to:

* Flag ambiguous images
* Reduce high-risk errors
* Improve operational reliability
* Support human-in-the-loop verification

---

# Flask Backend

Prediction Workflow
User Uploads Image
        ↓
Frontend Sends Request
        ↓
Flask API Receives Image
        ↓
Image Validation
        ↓
Preprocessing
        ↓
ResNet-50 Inference
        ↓
Decision Engine
        ↓
JSON Response Returned
        ↓
Frontend Displays Result
Flask Features Implemented
Flask REST API
Flask-CORS for frontend-backend communication
Environment-based configuration using .env
Centralized logging system
File upload handling
Error handling (404, 413, 500 responses)
Health monitoring endpoint

---

# Frontend

Built using:

* HTML5
* CSS3
* Vanilla JavaScript

## Features

### Drag-and-Drop Upload

Users can:

* Drag images directly into the upload area
* Browse files manually

### Validation

Checks:

* Supported file type
* File size limits

### Preview System

Displays:

* Image thumbnail
* Filename
* File size

### Result Dashboard

Shows:

* Prediction label
* Confidence score
* Final decision
* Review recommendation
  
<img width="1502" height="907" alt="image" src="https://github.com/user-attachments/assets/2e8f0920-7c6b-4779-bbda-ddb7810c26b2" />


<img width="1502" height="907" alt="image" src="https://github.com/user-attachments/assets/c089ae6d-b917-41c3-93bd-51bb6ed0fde9" />





---

# Logging System

## Application Logs

Records:

* Startup events
* Errors
* Warnings
* API activity

## Prediction Audit Logs

Stores:

* Timestamp
* Filename
* Prediction
* Confidence score
* Decision

This provides traceability and supports future auditing.


---

# Evaluation and Analysis

The evaluation pipeline generates:

### Training Analysis

* Loss Curves
* Accuracy Curves
* F1 Curves

### Classification Analysis

* Confusion Matrix
* Normalized Confusion Matrix
* ROC Curve
* Precision-Recall Curve

### Reliability Analysis

* Confidence Distribution
* Error Distribution
* Threshold Optimization
* Decision Zone Analysis

These visualizations help assess model calibration and real-world deployment readiness.

<img width="2684" height="2278" alt="full_evaluation" src="https://github.com/user-attachments/assets/16088b84-0a8b-43c7-b8a3-4de63ba2f1a3" />
<img width="2684" height="740" alt="extended_analysis" src="https://github.com/user-attachments/assets/25896718-a9d6-4992-a739-1a8b6dee7140" />



---

# Technologies Used

## Machine Learning

* PyTorch
* Torchvision
* Scikit-learn

## Data Processing

* NumPy
* PIL

## Visualization

* Matplotlib
* Seaborn

## Backend

* Flask
* Flask-CORS

## Frontend

* HTML
* CSS
* JavaScript

## Utilities

* tqdm
* dotenv
* logging

---

# Applications

* Digital Image Forensics
* Media Authenticity Verification
* Anti-Spoofing Systems
* Fraud Detection
* Identity Verification
* Document Authentication
* Security and Surveillance Systems

---

# Future Improvements

* Vision Transformers (ViT)
* EfficientNet Comparison
* Explainable AI using Grad-CAM
* ONNX Optimization
* Docker Deployment
* Cloud Hosting
* Multi-Class Recapture Source Detection
* Mobile Application Integration

---

# Author

Developed as a Computer Vision and Deep Learning project focused on image authenticity verification using transfer learning and production-oriented deployment practices.
