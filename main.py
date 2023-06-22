import pandas as pd
import pickle
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],  # Allow both POST and GET requests
    allow_headers=["*"],
)

# Serve static files (e.g., index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the saved pipeline and model
with open('pipeline_model.pkl', 'rb') as file:
    pipeline = pickle.load(file)

# Define the request body model
class PredictionRequest(BaseModel):
    input_data: dict

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post('/predict')
@app.get('/predict')  # Allow GET requests for the "/predict" API
def predict(request: PredictionRequest):
    try:
        # Retrieve the JSON data from the POST request
        input_data = request.input_data

        # Convert string values to appropriate data types
        input_data = {k: float(v) if not isinstance(v, float) else v for k, v in input_data.items()}

        # Create a DataFrame from the input_data dictionary
        df = pd.DataFrame.from_dict([input_data])

        # Perform inference using the loaded pipeline
        predictions = pipeline.predict(df.values)

        # Return the predictions as a JSON response
        response = {'predictions': predictions.tolist()}  # Convert predictions to a list
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Prediction error")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
