import pandas as pd

from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset, list_metrics, load_metric

"""
SNLI
input: 'snli hypothesis: X premise: XX'
output: 'contradiction' if 2 'neutral' if 1 else 'entailment'
"""

class NLIDataset(Dataset):
    def __init__(self, tokenizer, type_path, input_length, output_length):
        self.raw = {"input": [], "output": []}
        self.tokenizer = tokenizer
        self.input_length = input_length
        self.output_length = output_length
   
        if type_path == "train":
           df = pd.read_csv("./train_snli.csv")
        elif type_path == "val": 
           df = pd.read_csv('./val_snli.csv')
        else:
           raise NameError("Check type_path of dataset")
        
        totallen = len(df['label'])
        for i in range(totallen):
           self.raw['input'].append(f"snli hypothesis: {df['sentence1'][i]} premise: {df['sentence2'][i]}")
           self.raw['output'].append(df['label'][i])

        self.dataset = pd.DataFrame(self.raw)

    def __len__(self):
        return len(self.raw["input"])

    def convert_to_features(self, example_batch, idx):
        input_ = example_batch["input"]
        output_ = example_batch["output"]

        source = self.tokenizer.batch_encode_plus(
            [input_],
            max_length=self.input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        targets = self.tokenizer.batch_encode_plus(
            [output_],
            max_length=self.output_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return source, targets

    def __getitem__(self, idx):
        source, targets = self.convert_to_features(self.dataset.iloc[idx], idx)

        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()

        return {
            "source_ids": source_ids,
            "source_mask": src_mask,
            "target_ids": target_ids,
            "target_mask": target_mask,
        }

