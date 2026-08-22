import os 
import sys
import certifi
ca=certifi.where()
from dotenv import load_dotenv
load_dotenv()
mongo_db_url=os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response, HTMLResponse
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.mains_utils.utils import load_object

from networksecurity.utils.mains_utils.ml_utils.model.estimator import NetworkModel


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from networksecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
   
@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        # Read CSV file
        df = pd.read_csv(file.file)
        print("="*50)
        print("CSV loaded successfully")
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {list(df.columns)}")
        print("="*50)
        
        # Load preprocessor and model
        print("Loading preprocessor...")
        preprocessor = load_object("final_model/preprocessor.pkl")
        print("✓ Preprocessor loaded successfully")
        
        print("Loading model...")
        final_model = load_object("final_model/model.pkl")
        print("✓ Model loaded successfully")
        
        # Initialize NetworkModel
        print("Initializing NetworkModel...")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        print("✓ NetworkModel initialized successfully")
        
        # Make predictions
        print("\nMaking predictions...")
        y_pred = network_model.predict(df)
        print(f"✓ Predictions made successfully")
        print(f"Predictions: {y_pred}")
        
        # Add predictions to dataframe
        df['predicted_column'] = y_pred
        print("✓ Predictions added to dataframe")
        
        # Create output directory if it doesn't exist
        os.makedirs('prediction_output', exist_ok=True)
        df.to_csv('prediction_output/output.csv', index=False)
        print("✓ Output CSV saved successfully")
        
        # Generate HTML table with styling
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)
        
        # Create a complete HTML page with Bootstrap styling
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Network Security - Prediction Results</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{
                    background-color: #f8f9fa;
                    padding: 20px;
                }}
                .container {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    padding: 30px;
                    margin-top: 20px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 10px;
                    text-align: center;
                }}
                .subtitle {{
                    text-align: center;
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 14px;
                }}
                table {{
                    margin-top: 20px;
                }}
                .table-responsive {{
                    margin-top: 20px;
                }}
                .success-badge {{
                    display: inline-block;
                    background-color: #28a745;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 14px;
                    margin-bottom: 20px;
                }}
                .download-btn {{
                    margin-top: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Network Security - Prediction Results</h1>
                <div class="subtitle">Predictions completed successfully</div>
                <div class="success-badge">✓ {len(df)} records processed</div>
                
                <div class="table-responsive">
                    {table_html}
                </div>
                
                <div class="download-btn">
                    <p style="color: #666; margin-top: 30px;">
                        Results saved to: <code>prediction_output/output.csv</code>
                    </p>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        # Return as HTML response
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"ERROR during prediction: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"{'='*50}\n")
        raise NetworkSecurityException(e, sys)
   
     
if __name__=="__main__":
    app_run(app, host="0.0.0.0", port=8000)
