import io
import os
import subprocess
import argparse
import torch
import json
import copy
import string
import pandas as pd

from models import T5FineTuner
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import speech
from transformers import pipeline
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from torch.utils.data import Dataset, DataLoader

# convert to google STT input format
def convert2mono(input_file, output_file):
    try:
        command = ["sox", input_file, "-c", "1", output_file]
        subprocess.Popen(command)
        return True
    except:
        return False


class NLIDataset(Dataset):
    def __init__(self, tokenizer, _dict, total_summary):
        self.raw = {"input": []}
        self.input_length = 512
        self.tokenizer = tokenizer

        for elem in _dict["summary"]:
            self.raw["input"].append(
                f"snli hypothesis: {total_summary} premise: {elem}"
            )
        self.dataset = pd.DataFrame(self.raw)

    def __len__(self):
        return len(self.raw["input"])

    def convert_to_features(self, batch, idx):
        input_ = batch["input"]
        source = self.tokenizer.batch_encode_plus(
            [input_],
            max_length=self.input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return source

    def __getitem__(self, idx):
        source = self.convert_to_features(self.dataset.iloc[idx], idx)
        source_ids = source["input_ids"].squeeze()
        src_mask = source["attention_mask"].squeeze()
        return {"source_ids": source_ids, "src_mask": src_mask}


def get_args():
    with open("./t5_base_nli.json") as config_file:
        hparam = json.load(config_file)
    hparam = argparse.Namespace(**hparam)
    args_dict = dict(
        model_type=hparam.model_type,
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
    return args


def main(
    audio_file,
    audio_name,
    user_note,
    summarize_model="t5-base",
    _min_length=20,
    _max_length=100,
):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "1,2"
    _dict = {
        "script_start_time": [],
        "script": [],
        "summary": [],
        "score": [],
        "user_note": [],
    }

    if audio_file is not None:
        _script_dict = {"script_start_time": [], "script": []}
        audio_format = audio_file.split(".")[-1]
        if audio_format != "wav":
            raise NameError("Check in input audio format! It should be .wav file.")
        audio_name = "".join(audio_file.split(".")[:-1])
        print("## Working on {audio_name}.")

        # change audio file to google API input format
        success = convert2mono(audio_file, f"mono_{audio_file}")
        if not success:
            raise ValueError("Audio format is not convertable :(")

        try:
            os.system(
                f"python video-splitter/ffmpeg-split.py -f mono_{audio_file} -s 50"
            )
            os.system(f"mkdir {audio_name}")
            os.system(f"mv mono_{audio_name}-* {audio_name}")
        except:
            raise RuntimeError("Failed to split audio files")

        ## STT
        paths = os.listdir(f"./{audio_name}")
        client = speech.SpeechClient()

        f = open(f"{audio_name}_script.txt", "w")
        print(f"~~ Writing at {audio_name}_script.txt")

        for path_idx, path in enumerate(paths):
            with io.open(os.path.join(audio_name, path), "rb") as audio_file:
                content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            response = client.recognize(config=config, audio=audio)

            _str = ""
            for i, result in enumerate(response.results):
                alternatives = result.alternatives[0]
                f.write(alternatives.transcript)
                temp_str = alternatives.transcript.split('\n')[0] 
                _str += temp_str

            _dict["script"].append(_str)
            _dict["script_start_time"].append(50 * path_idx)
            _script_dict["script"].append(_str)
            _script_dict["script_start_time"].append(50 * path_idx)

        df = pd.DataFrame(_script_dict)
        df.to_csv(f"{audio_name}_script.csv")
        f.close()

    else:
        _script_dict = pd.read_csv(f"{audio_name}_script.csv")
        _dict["script"] = copy.deepcopy(_script_dict["script"])
        _dict["script_start_time"] = copy.deepcopy(_script_dict["script_start_time"])

    ## summarize
    os.environ["TRANSFORMERS_CACHE"] = "/mnt/.cache/huggingface"
    try:
        summarizer = pipeline(
            "summarization",
            model=summarize_model,
            tokenizer=summarize_model,
            framework="pt",
            device=1,
        )
        _input = [_script for _script in _dict["script"]]
        _output = summarizer(
            _input,
            min_length=_min_length,
            max_length=_max_length,
            no_repeat_ngram_size=3,
        )
        for _elem in _output:
            _dict["summary"].append(_elem["summary_text"])
    except:
        raise RuntimeError("Error in summarization")
    print("#### Done summarization")

    ## get score
    print(f"Current cuda device: {torch.cuda.current_device()}")
    total_summary = summarizer(
        "".join(_dict["script"]), min_length=100, max_length=300, no_repeat_ngram_size=3
    )[0]["summary_text"]
    print(f"~~~~ Total summary: {total_summary}")
    # tokenizer = T5Tokenizer.from_pretrained('./keyword')
    tokenizer = T5Tokenizer.from_pretrained("t5-base")
    _sen1 = tokenizer.encode(total_summary)
    config = T5Config()
    model = T5ForConditionalGeneration(config).cuda()
    args = get_args()
    model = T5FineTuner(args)
    model = T5FineTuner.load_from_checkpoint(
        checkpoint_path="./t5_base_nli_lr5.ckpt", hparams=args
    )
    # model.load_state_dict(torch.load("../keyword/outputs/t5_base_nli_lr5/epoch=4-step=374.ckpt"))
    # model = T5ForConditionalGeneration.from_pretrained('./keyword').cuda()
    model.eval()

    dataset = NLIDataset(tokenizer, _dict, total_summary)
    dataloader = DataLoader(
        dataset, shuffle=False, batch_size=10, drop_last=False, num_workers=8
    )

    for batch in dataloader:
        generated_ids = model.model.generate(
            batch["source_ids"].cuda(),
            attention_mask=batch["src_mask"].cuda(),
            use_cache=True,
            max_length=5,
            early_stopping=True,
        )
        preds = tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        for pred in preds:
            if pred == "contradiction":
                _dict["score"] = 0
            elif pred == "entailment":
                _dict["score"] = 1
            else:
                _dict["score"] = 0.5
    print("#### Done Scoring")

    ## match user_note
    ## {'start_time': [], 'note': []}
    note_idx = 0
    note_total_num = len(user_note["start_time"])
    for i, _start in enumerate(_dict["script_start_time"]):
        if note_idx == note_total_num:
            _dict['user_note'].append([]) 
            continue
        _user_note = []
        if i == len(_dict["script_start_time"]) - 1:
            while note_idx < note_total_num:
                _user_note.append(user_note["note"][note_idx])
                note_idx += 1 
        else:
            next_start = _dict["script_start_time"][i + 1]
            print(f"idx: {i}   start time: {_start}   next_start: {next_start}")
            while (
                note_idx < note_total_num and user_note["start_time"][note_idx] < next_start
            ):
                print(f"### NOTE idx: {note_idx} time: {user_note['start_time'][note_idx]} note: {user_note['note'][note_idx]}")
                _user_note.append(user_note["note"][note_idx])
                note_idx += 1
        _dict["user_note"].append(_user_note)
    print("### Done matching user note")

    df = pd.DataFrame(_dict)
    df.to_csv(f"{audio_name}_info.csv")


if __name__ == "__main__":
    user_note = {
        "start_time": [20, 40, 70, 100, 105, 166, 220],
        "note": ["hi", "this", "is", "hyunji", "good", "whow", 'enddd'],
    }
    # main("short.wav", "short", user_note)
    main(None, "short", user_note)
