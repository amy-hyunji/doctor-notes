import pandas as pd

def get_bert_style(sen1_list, sen2_list, label_list):
   ret_dict = {'document': [], 'label': []}
   for (sen1, sen2, label) in zip(sen1_list, sen2_list, label_list):
      sentence = f"{sen1} [SEP] {sen2}"
      ret_dict['document'].append(sentence)
      ret_dict['label'].append(label)
   return ret_dict

train_dataset = pd.read_csv("train.tsv", delimiter='\t')
# print(train_dataset.keys()) # id, sentence1, sentence2, noisy_label
train_dict = get_bert_style(train_dataset['sentence1'], train_dataset['sentence2'], train_dataset['noisy_label'])

dev_dataset = pd.read_csv("./dev.tsv", delimiter='\t')
dev_dict = get_bert_style(dev_dataset['sentence1'], dev_dataset['sentence2'], dev_dataset['noisy_label'])

print("*** Saving to csv file ***")
pd.DataFrame(train_dict).to_csv("./train.csv")
pd.DataFrame(dev_dict).to_csv("./dev.csv")
