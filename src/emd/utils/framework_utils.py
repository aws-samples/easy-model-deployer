def get_model_specific_path(model_id: str, model_tag: str, base_path: str) -> str:
    return f"/{model_id}/{model_tag}/{base_path.lstrip('/')}"
