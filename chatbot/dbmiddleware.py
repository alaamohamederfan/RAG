from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import pyodbc  # Use pyodbc for Azure SQL Server
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database connection string
# Ensure that you have the correct driver name
connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=localhost\\SQLEXPRESS;Database=master;Trusted_Connection=yes;"


class ConnectDB(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            logging.info("Attempting to connect to the database.")
            # Open a new connection for each request
            conn = pyodbc.connect(connection_string)
            logging.info("Connection successful.")

            # Store connection in request state
            request.state.db = conn
            
            # Process the request
            response = await call_next(request)
            
            return response
        except pyodbc.Error as e:
            logging.error(f"Database connection error: {e.args}")  # Log error details
            raise HTTPException(status_code=404, detail="Database connection failed")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")  # Log unexpected errors
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            if hasattr(request.state, 'db') and request.state.db is not None:
                request.state.db.close()  # Ensure the connection is closed
                logging.info("Database connection closed.")