from transformers import AutoModelWithLMHead, AutoTokenizer

"""
article: input article to summarize. max length should be 512
min_output: minimum length of the summary
max_output: maximum length of the summary
model: ['t5-base', 't5-large']
"""

def get_summary(article, min_output, max_output, model='t5-base')

    model = AutoModelWithLMHead.from_pretrained(model).cuda()
    tokenizer = AutoTokenizer.from_pretrained(model)

    inputs = tokenizer.encode('summarize: ' + article,  return_tensors='pt', max_length=512).cuda()
    output = model.generate(inputs, max_length=max_output, min_length=min_output, length_penalty=1.0, num_beams=4, early_stopping=True, no_repeat_ngram_size=3)
    return tokenizer.decode(output[0])
