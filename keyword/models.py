import pytorch_lightning as pl
from transformers import (
    AdamW,
    Adafactor,
    T5ForConditionalGeneration,
    T5Tokenizer,
    T5Config,
    get_linear_schedule_with_warmup,
)
import torch
from torch.utils.data import DataLoader
from data import NLIDataset 
from torch.utils.data import RandomSampler

import argparse
import time
import re
import os
import numpy as np
import string
from string import punctuation
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu, sentence_bleu


class T5FineTuner(pl.LightningModule):
    def __init__(self, hparams):
        super(T5FineTuner, self).__init__()
        self.hparams = hparams
        self.model = T5ForConditionalGeneration.from_pretrained(
            hparams.model_name_or_path
        )
        self.tokenizer = T5Tokenizer.from_pretrained(hparams.tokenizer_name_or_path)

        if self.hparams.freeze_embeds:
            self.freeze_embeds()
        if self.hparams.freeze_encoder:
            self.freeze_params(self.model.get_encoder())
            assert_all_frozen(self.model.get_encoder())

        self.step_count = 0
        self.output_dir = self.hparams.output_dir
        self.max_output_length = self.hparams.max_output_length

        self.em_score_list = []
        self.subset_score_list = []

    def normalize_answer(self, s):
        """Lower text and remove punctuation, articles and extra whitespace."""

        def remove_articles(text):
            return re.sub(r"\b(a|an|the)\b", " ", text)

        def white_space_fix(text):
            return " ".join(text.split())

        def remove_punc(text):
            exclude = set(string.punctuation)
            return "".join(ch for ch in text if ch not in exclude)

        def lower(text):
            return text.lower()

        return white_space_fix(remove_articles(remove_punc(lower(s))))

    def exact_match_score(self, prediction, ground_truth):
        return int(
            self.normalize_answer(prediction) == self.normalize_answer(ground_truth)
        )

    def approx_match_score(self, prediction, ground_truth):
        answer = self.normalize_answer(prediction)
        gt = self.normalize_answer(ground_truth)
        match = 0
        answer_words = answer.split(" ")
        gt_words = gt.split(" ")
        for word in answer_words:
            if word in gt_words:
                match += 1
        match /= len(answer_words)
        return match

    def calculate_scores(self, predictions, ground_truths):
        em_score = 0
        subset_match_score = 0

        for i in range(len(predictions)):
            ground_truth = ground_truths[i]
            prediction = predictions[i]
            em_score += self.exact_match_score(prediction, ground_truth)
            subset_match_score += self.approx_match_score(prediction, ground_truth)

        em_score /= len(predictions)
        subset_match_score /= len(predictions)
        return em_score * 100, subset_match_score * 100

    def bleu(self, gen, ref):
        """
        calculate pair wise bleu score. uses nltk implementation
        Args:
            references : a list of reference sentences
            candidates : a list of candidate(generated) sentences
        Returns:
            bleu score(float)
        """
        ref_bleu = []
        gen_bleu = []
        for l in gen:
            gen_bleu.append(l.split())
        for i, l in enumerate(ref):
            ref_bleu.append([l.split()])
        cc = SmoothingFunction()
        score_bleu = corpus_bleu(
            ref_bleu, gen_bleu, weights=(0, 1, 0, 0), smoothing_function=cc.method4
        )
        return score_bleu

    def get_dataset(self, tokenizer, type_path, args):
        if args.mode == "baseline":
            return NLIDataset(
                tokenizer=tokenizer,
                type_path=type_path,
                input_length=args.max_input_length,
                output_length=args.max_output_length,
            )
        else:
            raise NameError("Select the correct mode!")

    def freeze_params(self, model):
        for par in model.parameters():
            par.requires_grad = False

    def freeze_embeds(self):
        """Freeze token embeddings and positional embeddings for bart, just token embeddings for t5."""
        try:
            self.freeze_params(self.model.model.shared)
            for d in [self.model.model.encoder, self.model.model.decoder]:
                freeze_params(d.embed_positions)
                freeze_params(d.embed_tokens)
        except AttributeError:
            self.freeze_params(self.model.shared)
            for d in [self.model.encoder, self.model.decoder]:
                self.freeze_params(d.embed_tokens)

    def lmap(self, f, x):
        """list(map(f, x))"""
        return list(map(f, x))

    def is_logger(self):
        return self.trainer.global_rank <= 0

    def forward(
        self,
        input_ids,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        lm_labels=None,
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=lm_labels,
        )

    def _step(self, batch):
        lm_labels = batch["target_ids"]
        lm_labels[lm_labels[:, :] == self.tokenizer.pad_token_id] = -100
        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            lm_labels=lm_labels,
            decoder_attention_mask=batch["target_mask"],
        )

        loss = outputs[0]
        return loss

    def ids_to_clean_text(self, generated_ids):
        gen_text = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        return self.lmap(str.strip, gen_text)

    def _generative_step(self, batch):

        t0 = time.time()

        generated_ids = self.model.generate(
            batch["source_ids"],
            attention_mask=batch["source_mask"],
            use_cache=True,
            decoder_attention_mask=batch["target_mask"],
            max_length=self.max_output_length,
            num_beams=2,
            early_stopping=True,
        )

        preds = self.ids_to_clean_text(generated_ids)
        targets = self.ids_to_clean_text(batch["target_ids"])

        gen_time = (time.time() - t0) / batch["source_ids"].shape[0]

        loss = self._step(batch)

        self.log(
            "val_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True
        )
        summ_len = np.mean(self.lmap(len, generated_ids))
        em_score, subset_match_score = self.calculate_scores(preds, targets)
        # bleu_score = self.bleu(preds,targets)
        self.em_score_list.append(em_score)
        self.subset_score_list.append(subset_match_score)

        em_score = torch.tensor(em_score, dtype=torch.float32)
        subset_match_score = torch.tensor(subset_match_score, dtype=torch.float32)
        # bleu_score = torch.tensor(bleu_score,dtype=torch.float32)

        self.log("em_score", em_score, prog_bar=True, logger=True)
        self.log("subset_match_score", subset_match_score, prog_bar=True, logger=True)
        # self.log('bleu_score', bleu_score, prog_bar=True, logger=True)

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)
        self.log("loss", loss)
        return loss

    # score logging inside `_generative_step`
    def validation_step(self, batch, batch_idx):
        return self._generative_step(batch)

    def configure_optimizers(self):
        "Prepare optimizer and schedule (linear warmup and decay)"

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p
                    for n, p in model.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [
                    p
                    for n, p in model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]

        # optimizer = AdamW(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)
        optimizer = Adafactor(
            optimizer_grouped_parameters,
            lr=self.hparams.learning_rate,
            scale_parameter=False,
            relative_step=False,
        )
        self.opt = optimizer
        return [optimizer]

    def train_dataloader(self):
        train_dataset = self.get_dataset(
            tokenizer=self.tokenizer, type_path="train", args=self.hparams
        )
        dataloader = DataLoader(
            train_dataset,
            shuffle=True,
            batch_size=self.hparams.train_batch_size,
            drop_last=True,
            num_workers=self.hparams.num_workers,
        )
        return dataloader

    def val_dataloader(self):
        validation_dataset = self.get_dataset(
            tokenizer=self.tokenizer, type_path="val", args=self.hparams
        )
        return DataLoader(
            validation_dataset,
            batch_size=self.hparams.eval_batch_size,
            num_workers=self.hparams.num_workers,
            shuffle=False,
        )

    def on_save_checkpoint(self, checkpoint):
        save_path = os.path.join(self.output_dir, "best_tfmr")
        self.model.config.save_step = self.step_count
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
