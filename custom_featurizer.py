from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import GraphComponent
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from typing import Any, Dict, List, Text
from transformers import CamembertTokenizer, CamembertModel
import torch

@DefaultV1Recipe.register([
    "CamemBERTFeaturizer"
])
class CamemBERTFeaturizer(GraphComponent):
    def __init__(self, model_name: Text, tokenizer, model):
        self.model_name = model_name
        self.tokenizer = tokenizer
        self.model = model

    @classmethod
    def create(cls, config: Dict[Text, Any], model_storage: ModelStorage, resource: Resource) -> "CamemBERTFeaturizer":
        model_name = config.get("model_name", "camembert-base")
        tokenizer = CamembertTokenizer.from_pretrained(model_name)
        model = CamembertModel.from_pretrained(model_name)
        return cls(model_name, tokenizer, model)

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            text = message.get("text")
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            message.set("camembert_features", embeddings)
        return messages

    def train(self, training_data: TrainingData) -> None:
        """This method can be expanded if training with CamemBERT embeddings is required."""
        pass

    def persist(self, storage: ModelStorage, resource: Resource) -> None:
        """Persists the component configuration."""
        pass

    @classmethod
    def load(cls, config: Dict[Text, Any], model_storage: ModelStorage, resource: Resource) -> "CamemBERTFeaturizer":
        return cls.create(config, model_storage, resource)
