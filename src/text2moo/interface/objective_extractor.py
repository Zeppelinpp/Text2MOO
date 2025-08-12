import os
from openai import AsyncOpenAI
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from text2moo.models.types import OptimizationGroup
from text2moo.moea import BaseConfig, MOEADConfig, NSGA2Config
from text2moo.prompts.sys_prompts import GEN_MOEAD_CONFIG_PROMPT, GEN_NSGA2_CONFIG_PROMPT


class ExtractorError(Exception):
    """Custom exception for extraction errors."""

    pass


class BaseExtractor(ABC):
    """Abstract base class for different alogithms to extract objectives from text."""

    @abstractmethod
    def extract(self, query: str) -> BaseConfig:
        """Extract objectives from text to specific algorithm's config."""
        pass

    @abstractmethod
    def validate(self, config: BaseConfig) -> bool:
        """Validate if the config is valid."""
        pass


class MOEADExtractor(BaseExtractor):
    """Extractor for MOEAD."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        ollama: Optional[bool] = False,
        ollama_base_url: Optional[str] = None,
    ):
        # set up llm client
        if ollama:
            self.client = AsyncOpenAI(
                base_url=ollama_base_url if ollama_base_url else "http://localhost:11434/v1",
                api_key="ollama"
            )
        if api_key and base_url:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
            )
        else:
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        
        self.model = model if model else os.getenv("MODEL_NAME")
        self.sys_prompts = GEN_MOEAD_CONFIG_PROMPT
        

    def extract(self, query: str, data: OptimizationGroup) -> MOEADConfig:
        """Extract objectives from text to MOEAD config."""
        pass
