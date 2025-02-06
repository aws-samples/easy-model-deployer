import sys
sys.path.append("src/pipeline")
from dmaa.models import Model 
import json 

print(json.dumps(Model.get_supported_models(),indent=2,ensure_ascii=False))