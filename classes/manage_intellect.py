import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

t=AutoTokenizer.from_pretrained("DeepPavlov/distilrubert-tiny-cased-conversational-v1", model_max_length=512)
m=AutoModel.from_pretrained("DeepPavlov/distilrubert-tiny-cased-conversational-v1")

class Recommender:
    
    def __init__(self, ingridient):
        self.tokenizer = t
        self.rubert_model = m
        self.eda_file = pd.read_csv("1k_food.csv")
        self.ingr = ingridient
        self.recipes = self.eda_file['ingridient_keywords'].to_list()
        self.idxs = [i for i in range(0, len(self.recipes)) if self.ingr.lower() in self.recipes[i].lower()]
        self.idxs = self.idxs[0:min(5, len(self.idxs))]
        score_by_idx = {}
        
        for idx in self.idxs:
            score_by_idx[idx] = self.bert_score(self.eda_file.iloc[idx]['name'], self.ingr)
        
        score_by_idx = dict(sorted(score_by_idx.items(), key=lambda item: item[1]))

        self.result = ""

        self.speech = self.result

        for i in range(0, min(len(score_by_idx), 5)):
            beautiful_params = self.eda_file.iloc[list(score_by_idx.keys())[i]]['list_bzu'].replace("[", "").replace("]", "").replace("'", "").replace("КАЛОРИЙНОСТЬ", "калорий:").replace("ККАЛ", " ккал").replace("БЕЛКИ", "белков:").replace("ГРАММ", "г").replace("ЖИРЫ", "жиров:").replace("УГЛЕВОДЫ", "углеводов:")

            self.result += "\n"+self.eda_file.iloc[list(score_by_idx.keys())[i]]['name'] + " - (" + beautiful_params + ")\n"

            self.speech += "\n"+self.eda_file.iloc[list(score_by_idx.keys())[i]]['name']

    def get_dishes(self):
        return self.result

    def get_speech(self):
        return self.speech

    def embed_bert_cls(self, text, model, tokenizer):
        
        t = tokenizer(text, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            model_output = model(**{k: v.to(model.device) for k, v in t.items()})

        embeddings = model_output.last_hidden_state[:, 0, :]

        embeddings = torch.nn.functional.normalize(embeddings)

        return embeddings[0].cpu().numpy()

    def bert_score(self, query, text):
        query_embed = self.embed_bert_cls(query, self.rubert_model, self.tokenizer)
        text_embed = self.embed_bert_cls(text, self.rubert_model, self.tokenizer)

        return cosine_similarity([text_embed], [query_embed])[0][0]