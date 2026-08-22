## Network Security ML pipeline for phishing data

An end-to-end Machine Learning and MLOps project for detecting malicious network activity, covering data ingestion, preprocessing, model training, evaluation, artifact management, experiment tracking, containerization, and cloud deployment.

## Features

- Data ingestion, validation, and transformation
- ML model training and evaluation
- MLflow experiment/model tracking
- MongoDB integration
- AWS S3 for ML artifact storage
- Docker containerization
- Amazon ECR for container images
- AWS EC2 deployment
- GitHub Actions CI/CD with a self-hosted EC2 runner

## Architecture

```text
Dataset
   ↓
Ingestion → Validation → Transformation → Training → Evaluation
                                             ↓
                                           MLflow
                                             ↓
                                         AWS S3
                                             ↓
                                           Docker
                                             ↓
                                         Amazon ECR
                                             ↓
                                      AWS EC2 / CI-CD
```

## Tech Stack

**Python | Pandas | NumPy | Scikit-learn | MLflow | MongoDB | AWS S3 | Amazon ECR | EC2 | Docker | GitHub Actions**

## Project Structure

```text
Network-Security/
├── .github/workflows/
├── components/
├── configuration/
├── entity/
├── exception/
├── logger/
├── pipeline/
├── utils/
├── artifacts/
├── Dockerfile
├── requirements.txt
├── setup.py
└── main.py
```

## Local Setup


git clone <REPOSITORY_URL>
cd Network-Security

conda create -n networksecurity python=3.11
conda activate networksecurity

pip install -r requirements.txt
python main.py


Configure required AWS and MongoDB settings through environment variables or a local `.env` file. Never commit credentials or secrets.

## Docker


docker build -t networksecurity .
docker run -p 8080:8080 networksecurity


## CI/CD

The GitHub Actions pipeline automates:

```text
Git Push
   ↓
Build Docker Image
   ↓
Push to Amazon ECR
   ↓
EC2 Self-Hosted Runner
   ↓
Pull Image
   ↓
Run Container
```

### Deployment Status

The CI/CD infrastructure is implemented through the ECR and EC2 runner stages. The final container deployment is **still being completed**.

## Future Improvements

- Complete and verify the final EC2 container deployment
- Add automated tests and health checks
- Add Docker vulnerability scanning
- Add CloudWatch monitoring
- Add model/data drift monitoring
- Add automated retraining and rollback

## Author

**Swagat Pati**

