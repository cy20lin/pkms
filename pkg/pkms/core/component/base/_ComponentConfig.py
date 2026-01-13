from pydantic import BaseModel

class ComponentConfig(BaseModel):
    """
    Declarative configuration for a component.

    - Pure data
    - No runtime resources
    """
    type: str