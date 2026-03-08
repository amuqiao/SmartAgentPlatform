#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stock Analyzer Agent"""

import os
import json
from typing import Type, Optional, Any
import asyncio

from pydantic import BaseModel

from agentscope.agent import ReActAgent
from agentscope._logging import logger
from agentscope.formatter import FormatterBase
from agentscope.memory import MemoryBase
from agentscope.message import (
    Msg,
    ToolUseBlock,
    TextBlock,
    ToolResultBlock,
)
from agentscope.model import ChatModelBase
from agentscope.tool import (
    Toolkit,
    ToolResponse,
)

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROMPT_DIR = os.path.join(_CURRENT_DIR, "prompts")
_CONFIG_PATH = os.path.join(_CURRENT_DIR, "config.json")


class StockAnalysisResult(BaseModel):
    """Stock analysis result model"""

    stock_name: str
    stock_code: str
    analysis_summary: str
    investment_advice: str
    risk_assessment: str


class StockAnalyzerAgent(ReActAgent):
    """
    Stock Analyzer Agent that extends ReActAgent with stock analysis capabilities.
    """

    def __init__(
        self,
        name: str,
        model: ChatModelBase,
        formatter: FormatterBase,
        memory: MemoryBase,
        toolkit: Toolkit,
        sys_prompt: str = None,
        max_iters: int = 10,
    ) -> None:
        """Initialize the Stock Analyzer Agent."""
        # Load default system prompt if not provided
        if sys_prompt is None:
            with open(
                os.path.join(_PROMPT_DIR, "stock_analyzer_sys_prompt.md"),
                "r",
                encoding="utf-8",
            ) as f:
                sys_prompt = f.read()

        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model=model,
            formatter=formatter,
            memory=memory,
            toolkit=toolkit,
            max_iters=max_iters,
        )

        # Register tools
        self.toolkit.register_tool_function(self.analyze_stock)

    async def analyze_stock(
        self, stock_name: str, stock_code: str, analysis_type: str = "comprehensive"
    ) -> ToolResponse:
        """Analyze a stock based on the given analysis type."""
        try:
            # Load analysis prompt based on type
            prompt_file = os.path.join(
                _PROMPT_DIR, f"{analysis_type}_analysis_prompt.md"
            )
            if not os.path.exists(prompt_file):
                # Fallback to comprehensive analysis
                prompt_file = os.path.join(
                    _PROMPT_DIR, "comprehensive_analysis_prompt.md"
                )

            with open(prompt_file, "r", encoding="utf-8") as f:
                analysis_prompt = f.read()

            # Create a specific system prompt for this analysis
            analysis_system_prompt = f"{self.sys_prompt}\n\n重要提示：本次分析的股票是 {stock_name} (代码: {stock_code})，请直接开始分析，不要向用户索要股票信息。"

            # Format the prompt with stock information
            formatted_prompt = analysis_prompt.format(
                stock_name=stock_name, stock_code=stock_code
            )

            # Log the formatted prompt for debugging
            logger.info(
                f"Formatted prompt for {stock_name} ({stock_code}): {formatted_prompt[:100]}..."
            )

            # Create a message with the analysis prompt
            msg = Msg(
                "user",
                content=formatted_prompt,
                role="user",
            )

            # Format the prompt for the model
            prompt = await self.formatter.format(
                msgs=[
                    Msg("system", analysis_system_prompt, "system"),
                    msg,
                ],
            )

            # Get response from the model
            res = await self.model(prompt)

            # Extract the response text
            if self.model.stream:
                analysis_result = ""
                async for content_chunk in res:
                    analysis_result += content_chunk.content[0]["text"]
            else:
                analysis_result = res.content[0]["text"]

            # Return the analysis result
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=analysis_result,
                    ),
                ],
                metadata={
                    "success": True,
                    "stock_name": stock_name,
                    "stock_code": stock_code,
                    "analysis_type": analysis_type,
                },
            )
        except Exception as e:
            logger.error(f"Error analyzing stock: {e}")
            return ToolResponse(
                content=[
                    TextBlock(
                        type="text",
                        text=f"Error analyzing stock: {str(e)}",
                    ),
                ],
                metadata={"success": False},
            )
