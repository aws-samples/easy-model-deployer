from pydantic import BaseModel,Field
from typing import Optional
import os

class ClientBase(BaseModel):
    model_id: Optional[str] = None
    """The model id deployed by emd."""

    model_tag: Optional[str] = ""
    """The model tag."""

    model_stack_name: Optional[str] = None
    """The name of the model stack deployed by emd."""

    class Config:
        """Configuration for this pydantic object."""
        extra = "allow"


    def invoke(self,pyload:dict):
        raise NotImplementedError


    def invoke_async(self, pyload:dict):
        raise NotADirectoryError
