import argparse
from argparse import ArgumentParser
import os

os.environ["TRANSFORMERS_CACHE"] = "/mnt/.cache/huggingface"
import json
import random
import numpy as np
import pandas as pd
import torch
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger

from transformers import (
    AdamW,
    Adafactor,
    T5ForConditionalGeneration,
    T5Tokenizer,
    T5Config,
    get_linear_schedule_with_warmup,
)

import textwrap
from tqdm.auto import tqdm

from models import T5FineTuner
from knockknock import slack_sender
from slack import get_webhook_url, get_channel


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


@slack_sender(webhook_url=get_webhook_url(), channel=get_channel())
def main(args, train_params):
    set_seed(42)
    model = T5FineTuner(args)
    trainer = pl.Trainer(**train_params)
    trainer.fit(model)
    return "Done HAI"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config", default=None, type=str)
    arg_ = parser.parse_args()
    if arg_.config == None:
        raise NameError("Input a config file!")

    # Getting configurations
    with open(arg_.config) as config_file:
        hparam = json.load(config_file)
    hparam = argparse.Namespace(**hparam)

    # Setting gpus to use
    # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  # see issue #152
    # os.environ["CUDA_VISIBLE_DEVICES"] = hparam.CUDA_VISIBLE_DEVICES

    # Logging into WANDB
    if hparam.wandb_log:
        wandb_logger = WandbLogger(
            project=hparam.wandb_project, name=hparam.wandb_run_name
        )
    else:
        wandb_logger = None

    # Setting configurations
    args_dict = dict(
        output_dir=hparam.output_dir,  # path to save the checkpoints
        dataset=hparam.dataset,
        model_name_or_path=hparam.model,
        mode=hparam.mode,
        tokenizer_name_or_path=hparam.model,
        max_input_length=hparam.input_length,
        max_output_length=hparam.output_length,
        freeze_encoder=False,
        freeze_embeds=False,
        learning_rate=hparam.learning_rate,
        weight_decay=0.0,
        adam_epsilon=1e-8,
        warmup_steps=0,
        train_batch_size=hparam.train_batch_size,
        eval_batch_size=hparam.train_batch_size,
        num_train_epochs=hparam.num_train_epochs,
        gradient_accumulation_steps=hparam.gradient_accumulation_steps,
        n_gpu=hparam.ngpu,
        num_workers=hparam.num_workers,
        resume_from_checkpoint=hparam.resume_from_checkpoint,
        valid_on_recentQA=hparam.valid_on_recentQA,
        val_check_interval=1.0,
        early_stop_callback=False,
        fp_16=False,  # if you want to enable 16-bit training then install apex and set this to true
        opt_level="O1",  # you can find out more on optimisation levels here https://nvidia.github.io/apex/amp.html#opt-levels-and-properties
        max_grad_norm=1.0,  # if you enable 16-bit training then set this to a sensible value, 0.5 is a good default
        seed=101,
        check_validation=hparam.check_validation,
        checkpoint_path=hparam.checkpoint_path,
    )
    args = argparse.Namespace(**args_dict)

    ## Define Checkpoint function
    if args.mode in ["baseline"]:
        checkpoint_callback = pl.callbacks.ModelCheckpoint(
            dirpath=args.output_dir, monitor="val_loss", mode="min", save_top_k=2
        )
    else:
        raise NameError("Select the correct mode!")

    ## If resuming from checkpoint, add an arg resume_from_checkpoint
    train_params = dict(
        accumulate_grad_batches=args.gradient_accumulation_steps,
        gpus=args.n_gpu,
        max_epochs=args.num_train_epochs,
        precision=16 if args.fp_16 else 32,
        amp_level=args.opt_level,
        resume_from_checkpoint=args.resume_from_checkpoint,
        gradient_clip_val=args.max_grad_norm,
        checkpoint_callback=checkpoint_callback,
        val_check_interval=args.val_check_interval,
        logger=wandb_logger,
        accelerator=hparam.accelerator,
    )

    main(args, train_params)
