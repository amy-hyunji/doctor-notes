import os
import random
import torch
import re 
import emoji
import pandas as pd
import numpy as np

from soynlp.normalizer import repeat_normalize
from pprint import pprint
from transformers import BertForSequenceClassification, BertTokenizer, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, Dataset, TensorDataset
from torch.optim.lr_scheduler import ExponentialLR
from pytorch_lightning import LightningModule, Trainer, seed_everything 
from pytorch_lightning.callbacks import ModelCheckpoint
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score 

from knockknock import slack_sender
from slack import get_webhook_url, get_channel

os.environ['TRANSFORMERS_CACHE'] = '/mnt/.cache/huggingface/'

class Model(LightningModule):
   def __init__(self, **kwargs):
      super().__init__()
      self.save_hyperparameters() 

      self.bert = BertForSequenceClassification.from_pretrained(self.hparams.pretrained_model)
      self.tokenizer = BertTokenizer.from_pretrained(
               self.hparams.pretrained_tokenizer
            )
   
   def forward(self, **kwargs):
      return self.bert(**kwargs)
      
   def step(self, batch, batch_idx):
      data, labels = batch 
      output = self(input_ids=data, labels=labels)

      loss = output.loss
      logits = output.logits

      preds = logits.argmax(dim=-1)

      labels = list(labels.cpu().numpy())
      preds = list(preds.cpu().numpy())

      return {'loss': loss, 'y_true': labels, 'y_pred': preds}

   def training_step(self, batch, batch_idx):
      return self.step(batch, batch_idx)

   def validation_step(self, batch, batch_idx):
      return self.step(batch, batch_idx)

   def epoch_end(self, outputs, state='train'):
      loss = torch.tensor(0, dtype=torch.float)
      y_true = []
      y_pred = []
      for i in outputs:
         loss += i['loss'].cpu().detach()
         y_true += i['y_true']
         y_pred += i['y_pred']
      loss /= len(outputs)

      self.log(state+"_loss", float(loss), on_epoch=True, prog_bar=True)
      self.log(state+"_acc", accuracy_score(y_true, y_pred), on_epoch=True, prog_bar=True)
      self.log(state+"_precision", precision_score(y_true, y_pred), on_epoch=True, prog_bar=True)
      self.log(state+"_recall", recall_score(y_true, y_pred), on_epoch=True, prog_bar=True)
      self.log(state+"_f1", f1_score(y_true, y_pred), on_epoch=True, prog_bar=True)
      return {'loss': loss}

   def train_epoch_end(self, outputs):
      return self.epoch_end(outputs, state='train')

   def validation_epoch_end(self, outputs):
      return self.epoch_end(outputs, state='val')

   def configure_optimizers(self):
      if self.hparams.optimizer == 'AdamW':
         optimizer = AdamW(self.parameters(), lr=self.hparams.lr)
      elif self.hparams.optimizer == 'AdamP':
         from adamp import AdamP
         optimizer = AdamP(self.parameters(), lr=self.hparams.lr)
      else:
         raise NotImplementedError('Only AdamW and AdamP is Supported!')

      if self.hparams.lr_scheduler == 'cos':
         scheduler = ConsineAnnealingWarmRestarts(optimizer, T_0=1, T_mult=2)
      elif self.hparams.lr_scheduler == 'exp':
         scheduler = ExponentialLR(optimizer, gamma=0.5)
      else:
         raise NotImplementedError('Only cos and exp lr scheduler is Supported!')

      return {'optimizer': optimizer, 'scheduler': scheduler}

   def read_data(self, path):
      if path.endswith('csv'):
         print(f"Loading data set from.. {path}")
         return pd.read_csv(path)
      else:
         raise NotImplementedError("Input should be csv format")

   def preprocess_dataframe(self, df):
      # emojis = ''.join(emoji.UNICODE_EMOJI.keys())
      # pattern = re.compile(f'[^ .,?!/@$%~％·∼()\x00-\x7Fㄱ-{emojis}]+')
      # url_pattern = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
      
      def clean(x):
         # x = pattern.sub(' ', x)
         # x = url_pattern.sub('', x)
         x = x.strip()
         x = repeat_normalize(x, num_repeats=2)
         return x

      df['document'] = df['document'].map(lambda x: self.tokenizer.encode(clean(str(x)), padding='max_length', max_length=self.hparams.max_length, truncation=True))
      return df


   def dataloader(self, path, shuffle=False):
      df = self.read_data(path)
      df = self.preprocess_dataframe(df)
      
      dataset = TensorDataset(torch.tensor(df['document'].to_list(), dtype=torch.long), torch.tensor(df['label'].to_list(), dtype=torch.long))

      return DataLoader(dataset, batch_size=self.hparams.batch_size or self.batch_size, shuffle=shuffle, num_workers=self.hparams.cpu_workers)

   def train_dataloader(self):
      return self.dataloader(self.hparams.train_data_path, shuffle=True)

   def val_dataloader(self):
      return self.dataloader(self.hparams.val_data_path, shuffle=False)

@slack_sender(webhook_url=get_webhook_url(), channel=get_channel())
def main():
   
   args = {
      'random_seed': 42,
      'pretrained_model': 'bert-base-uncased',
      'pretrained_tokenizer': 'bert-base-uncased',
      'batch_size': 64, 
      'lr': 5e-6,
      'epoch': 10,
      'max_length': 150,
      'train_data_path': './PAWS/train.csv',
      'val_data_path': './PAWS/dev.csv',
      'optimizer': 'AdamW',
      'lr_scheduler': 'exp',
      'fp16': False,
      'tpu_cores': 0,
      'cpu_workers': 4,
      'gpus': 1
   }

   
   checkpoint_callback = ModelCheckpoint(filename='epoch{epoch}-val_acc{val_acc:.4f}', monitor='val_acc', save_top_k=2, mode='max')

   seed_everything(args['random_seed'])
   model = Model(**args)

   print("~~~ START Training")
   trainer = Trainer(callbacks=[checkpoint_callback], max_epochs=args['epoch'], gpus=args['gpus'])
   trainer.fit(model)

def preprocess_dataframe(df, tokenizer):

   def clean(x):
      x = x.strip()
      x = repeat_normalize(x, num_repeats=2)
      return x

   df['document'] = df['document'].map(lambda x: tokenizer.encode(clean(str(x)), padding='max_length', max_length=150, truncation=True))
   return df

def test():

   args = {
      'random_seed': 42,
      'pretrained_model': 'bert-base-uncased',
      'pretrained_tokenizer': 'bert-base-uncased',
      'batch_size': 16, 
      'lr': 5e-6,
      'epoch': 10,
      'max_length': 150,
      'train_data_path': './PAWS/train.csv',
      'val_data_path': './PAWS/dev.csv',
      'optimizer': 'AdamW',
      'lr_scheduler': 'exp',
      'fp16': False,
      'tpu_cores': 0,
      'cpu_workers': 4,
      'gpus': 1
   }
   seed_everything(args['random_seed'])
   model = Model.load_from_checkpoint(checkpoint_path="./lightning_logs/version_9/checkpoints/epochepoch=1-val_accval_acc=0.9672.ckpt", hparams=args).cuda()
   model.eval()

   tokenizer = BertTokenizer.from_pretrained(args['pretrained_tokenizer']) 

   df = pd.read_csv("./PAWS/dev.csv")
   df = preprocess_dataframe(df, tokenizer) 
   dataset = TensorDataset(torch.tensor(df['document'].to_list(), dtype=torch.long), torch.tensor(df['label'].to_list(), dtype=torch.long))

   dataloader = DataLoader(dataset, batch_size=16, shuffle=False, num_workers=4)
  
   _dict = {'input': df['document'], 'label': df['label'], 'pred': []}

   print("##### Start!")
   for batch in dataloader:
      data, labels = batch 
      output = model(input_ids=data.cuda(), labels=labels.cuda())

      loss = output.loss
      logits = output.logits

      preds = logits.argmax(dim=-1).cpu().numpy()
      _dict['pred'].extend(preds) 
     
   print("##### Done!")
   df = pd.DataFrame(_dict)
   df.to_csv("test.csv")

if __name__ == "__main__":
#main()
   test()
