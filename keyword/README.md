## Info
Train code of T5-base on SNLI dataset

## Dataset
`wget https://nlp.stanford.edu/projects/snli/snli_1.0.zip`
* run `json2csv.py` to convert jsonl to csv which is the input format of the training code

## Setting
```
pip install sentencepiece
pip install pytorch_lightning==1.2.6
pip install transformers
pip install wandb
```
* supports multi-gpu training

## Train hyperparameter
`t5_base_nli.json`

## Run
`python train.py --config [config file]`
