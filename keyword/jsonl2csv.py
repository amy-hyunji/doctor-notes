import json_lines
import sys
import pandas as pd

ret_dict = {'sentence1': [], 'sentence2': [], 'label': []}
with open('./snli_1.0/snli_1.0_test.jsonl') as f:
   for i, item in enumerate(json_lines.reader(f)):
      ret_dict['sentence1'].append(item['sentence1'])
      ret_dict['sentence2'].append(item['sentence2'])
      ret_dict['label'].append(item['gold_label'])

totalnum = int(len(ret_dict['sentence1']))
trainnum = int(totalnum*0.9)

print(f"## of train dataset: {trainnum}")      
print(f"## of val dataset: {totalnum-trainnum}")      
df = pd.DataFrame({'sentence1': ret_dict['sentence1'][:trainnum], 'sentence2': ret_dict['sentence2'][:trainnum], 'label': ret_dict['label'][:trainnum]})
df.to_csv("./train_snli.csv")
df = pd.DataFrame({'sentence1': ret_dict['sentence1'][trainnum:], 'sentence2': ret_dict['sentence2'][trainnum:], 'label': ret_dict['label'][trainnum:]})
df.to_csv("./val_snli.csv")
