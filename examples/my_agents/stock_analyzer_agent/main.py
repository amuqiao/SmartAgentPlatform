#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stock Analyzer Agent Main Entry"""

import asyncio
import os
import sys
import argparse
import traceback
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from stock_agent import StockAnalyzerAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load configuration from config.json
_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# Global variables
agent = None
stock_config = config


@app.on_event("startup")
async def startup_event():
    """Initialize the agent when the server starts."""
    global agent
    try:
        # Setup toolkit
        toolkit = Toolkit()

        # Get model configuration from config
        model_config = stock_config.get("model_config", {})
        model_name = model_config.get("model_name", "qwen3-max")
        stream = model_config.get("stream", False)
        max_iters = model_config.get("max_iters", 10)

        # Initialize the stock analyzer agent
        agent = StockAnalyzerAgent(
            name="Stock Analyzer Agent",
            model=DashScopeChatModel(
                api_key=os.environ.get("DASHSCOPE_API_KEY"),
                model_name=model_name,
                stream=stream,
            ),
            formatter=DashScopeChatFormatter(),
            memory=InMemoryMemory(),
            toolkit=toolkit,
            max_iters=max_iters,
        )
        print("Stock Analyzer Agent initialized successfully!")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        traceback.print_exc()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the main page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stock_categories": stock_config.get("stock_categories", []),
            "analysis_types": stock_config.get("analysis_types", []),
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    stock_name: str = Form(...),
    stock_code: str = Form(...),
    analysis_type: str = Form(...),
):
    """Endpoint for stock analysis."""
    try:
        if not agent:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "stock_categories": stock_config.get("stock_categories", []),
                    "analysis_types": stock_config.get("analysis_types", []),
                    "error": "Agent not initialized. Please check the server logs.",
                },
            )

        # Call the analyze_stock tool
        tool_response = await agent.analyze_stock(stock_name, stock_code, analysis_type)

        # Extract the analysis result
        analysis_result = (
            tool_response.content[0]["text"]
            if tool_response.content
            else "No analysis result"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "stock_categories": stock_config.get("stock_categories", []),
                "analysis_types": stock_config.get("analysis_types", []),
                "stock_name": stock_name,
                "stock_code": stock_code,
                "analysis_type": analysis_type,
                "analysis_result": analysis_result,
            },
        )
    except Exception as e:
        print(f"Error analyzing stock: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "stock_categories": stock_config.get("stock_categories", []),
                "analysis_types": stock_config.get("analysis_types", []),
                "error": f"Error analyzing stock: {str(e)}",
            },
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Analyzer Agent Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the server on (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    args = parser.parse_args()

    print("Starting Stock Analyzer Agent Server...")
    print(f"Server will run on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(app, host=args.host, port=args.port)
