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
from fastapi.responses import Response
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

from fastapi.templating import Jinja2Templates
templates=Jinja2Templates(directory="./templates")

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
        print(f"DataFrame dtypes:\n{df.dtypes}")
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
        
        # Print first row info
        print(f"\nFirst row of data:")
        print(df.iloc[0])
        
        # Make predictions
        print("\nMaking predictions...")
        print(f"DataFrame type before predict: {type(df)}")
        print(f"DataFrame is not dict: {not isinstance(df, dict)}")
        
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
        
        # Generate HTML table
        table_html = df.to_html(classes='table table-striped')
        
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"ERROR during prediction: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"{'='*50}\n")
        raise NetworkSecurityException(e, sys)
   
     
if __name__=="__main__":
    app_run(app, host="0.0.0.0", port=8000)
