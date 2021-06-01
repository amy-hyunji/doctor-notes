import pandas as pd
import copy
import sys
import torch

from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset, list_metrics, load_metric

"""
SNLI
input: 'snli hypothesis: X premise: XX'
output: 'contradiction' if 2 'neutral' if 1 else 'entailment'
"""


class NLIDataset(Dataset):
    def __init__(self, tokenizer, type_path, input_length, output_length, model_type):
        self.raw = {"input": [], "output": []}
        self.tokenizer = tokenizer
        self.input_length = input_length
        self.output_length = output_length
        self.model_type = model_type

        if type_path == "train":
            df = pd.read_csv("./train_snli.csv")
        elif type_path == "val":
            df = pd.read_csv("./val_snli.csv")
        else:
            raise NameError("Check type_path of dataset")

        totallen = len(df["label"])

        if model_type == "bert":
            for i in range(totallen):
                _label = df["label"][i]
                if _label == "contradiction":
                    self.raw["output"].append(0)
                elif _label == "neutral":
                    self.raw["output"].append(1)
                elif _label == "entailment":
                    self.raw["output"].append(2)
                else:
                    #print(f"idx: {i}  Check the label: {_label}")
                    continue
                self.raw["input"].append(f"{df['sentence1'][i]} [SEP] {df['sentence2'][i]}")

        elif model_type == "T5":
            for i in range(totallen):
                self.raw["input"].append(
                    f"snli hypothesis: {df['sentence1'][i]} premise: {df['sentence2'][i]}"
                )
                self.raw["output"].append(df["label"][i])

        self.dataset = pd.DataFrame(self.raw)

    def __len__(self):
        return len(self.raw["input"])

    def convert_to_features(self, example_batch, idx):
        input_ = example_batch["input"]
        output_ = example_batch["output"]

        if self.model_type == "T5":
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
        elif self.model_type == "bert":
            source = self.tokenizer.batch_encode_plus(
                [input_],
                max_length=self.input_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            # change 'token_type_ids' in source
            _token_type_ids = copy.deepcopy(source["token_type_ids"])
            source_token_type_ids = []
            for i in range(len(_token_type_ids)):
                _input_ids = source["input_ids"][i]
                _token_ids = []
                first = True
                for elem in _input_ids:
                    if first and elem != 102:
                        _token_ids.append(0)
                    elif first and elem == 102:
                        _token_ids.append(0)
                        first = False
                    else:
                        _token_ids.append(1)
                assert len(_token_ids) == len(_input_ids)
                source_token_type_ids.append(_token_ids)
            source["token_type_ids"] = torch.tensor(source_token_type_ids)
            assert(source['input_ids'].size() == source['token_type_ids'].size())

            targets = torch.tensor(output_).unsqueeze(0)
            
        return source, targets

    def __getitem__(self, idx):
        source, targets = self.convert_to_features(self.dataset.iloc[idx], idx)

        if self.model_type == "T5":
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

        elif self.model_type == "bert":
            return {
                "input": source,
                "label": targets,
            }
