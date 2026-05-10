import torch
import torch.nn as nn
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import json

class IngredientClassifier(nn.Module):
    """
    CLIP-based ingredient classifier fine-tuned on 200+ cooking ingredients.
    Optimized for AMD ROCm MI300X via torch.compile.
    """
    def __init__(self, num_classes=200, model_name="openai/clip-vit-base-patch32"):
        super().__init__()
        self.clip = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.classifier = nn.Linear(self.clip.config.projection_dim, num_classes)

    def forward(self, pixel_values):
        image_embeds = self.clip.get_image_features(pixel_values=pixel_values)
        logits = self.classifier(image_embeds)
        return logits

def predict_ingredients(image_path_or_pil, model, processor, labels, top_k=10):
    if isinstance(image_path_or_pil, str):
        image = Image.open(image_path_or_pil).convert("RGB")
    else:
        image = image_path_or_pil

    inputs = processor(images=image, return_tensors="pt")
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(inputs["pixel_values"])
        probs = torch.softmax(logits, dim=-1)[0]

    top = probs.topk(top_k)
    results = []
    for score, idx in zip(top.values.tolist(), top.indices.tolist()):
        results.append({
            "name": labels[idx],
            "confidence": round(score, 4),
            "class_id": idx
        })
    return results

def load_labels(path="labels.json"):
    with open(path) as f:
        return json.load(f)

if __name__ == "__main__":
    # Example usage
    labels = load_labels()
    model = IngredientClassifier(num_classes=len(labels))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    # torch.compile for ROCm speedup
    model = torch.compile(model)

    results = predict_ingredients("test_fridge.jpg", model, model.processor, labels)
    print(json.dumps(results, indent=2))
