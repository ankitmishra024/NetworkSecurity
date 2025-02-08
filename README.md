# Network Security: Phishing Detection Project

## 📌 Overview
This project is designed to detect phishing attacks using machine learning. It includes various stages such as data ingestion, validation, transformation, model training, and prediction. The system is built with **FastAPI**, **MongoDB**, and **MLflow** for tracking the model pipeline.

## 🔧 Project Workflow
The project follows a structured pipeline approach:

1. **Data Ingestion**: Fetching and storing phishing data.
2. **Data Validation**: Checking data quality and consistency.
3. **Data Transformation**: Converting raw data into a suitable format.
4. **Model Training**: Training the machine learning model.
5. **Prediction**: Using the trained model to detect phishing attacks.

## 📊 Architecture Diagram
Below is the architecture of different pipelines used in this project.

### **1️⃣ Data Ingestion Pipeline**
```
        Raw Data
           |
           v
    Store in MongoDB
           |
           v
     Train-Test Split
```
- Collects data from different sources.
- Stores it in **MongoDB**.
- Splits data into training and testing sets.

### **2️⃣ Data Validation Pipeline**
```
     Train & Test Data
           |
           v
    Validate Schema
           |
           v
      Check for Nulls
           |
           v
     Generate Report
```
- Ensures data quality.
- Checks for missing values and incorrect formats.
- Generates a validation report.

### **3️⃣ Data Transformation Pipeline**
```
    Validated Data
           |
           v
   Feature Engineering
           |
           v
   Convert to Numpy Array
           |
           v
   Save Preprocessor
```
- Performs feature engineering.
- Converts data into a format suitable for training.
- Saves the preprocessor for future use.

### **4️⃣ Model Training Pipeline**
```
    Transformed Data
           |
           v
    Train Model
           |
           v
  Evaluate Performance
           |
           v
    Save Trained Model
```
- Trains the phishing detection model.
- Evaluates its accuracy.
- Stores the final trained model.

## 🚀 How to Run the Project

1. **Clone the Repository:**
   ```sh
   git clone <repository_url>
   cd network-security-phishing-detection
   ```

2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set Up MongoDB Connection:**
   - Create a `.env` file and add:
     ```env
     MONGODB_URL_KEY=<your_mongodb_connection_string>
     ```

4. **Run the API Server:**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

5. **Train the Model:**
   Open your browser and visit:
   ```
   http://127.0.0.1:8080/train
   ```

6. **Make Predictions:**
   - Upload a CSV file using:
   ```
   http://127.0.0.1:8080/predict
   ```


## 📌 Key Features
✅ **Automated Machine Learning Pipeline**
✅ **FastAPI-based API for Training & Prediction**
✅ **MongoDB for Data Storage**
✅ **MLflow for Model Tracking**
✅ **Scalable and Modular Codebase**

## 🛠️ Tech Stack
- **Python** (FastAPI, Pandas, NumPy, Scikit-learn)
- **MongoDB** (Data Storage)
- **MLflow** (Model Logging)
- **Docker**(Image)
-**Github Action** (CI/CD)
- **AWS S3** (Cloud Storage for Artifacts)
- **AwS ECR** (Deployment of Docker image)
- **AWS EC2** (For Deployment in AWS environment)

---
💡 _This project aims to enhance network security by detecting phishing attacks effectively using ML techniques.


