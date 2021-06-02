import os
import io
import subprocess
import argparse
import torch
import json
import copy
import string
import flask
import pandas as pd

from models import T5FineTuner
from transformers import pipeline
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from torch.utils.data import Dataset, DataLoader

from google.cloud import speech
from flask import (
    Flask,
    abort,
    jsonify,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    make_response,
)
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

UPLOAD_FOLDER = "/mnt/hyunji/doctor-notes/database"
ALLOWED_EXTENSIONS = {"txt", "wav"}

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CORS_HEADERS"] = "Content-Type"


@cross_origin()
@app.route("/")
def home():
    print("####", request.form.to_dict())
    return "Welcome to server!"


@app.route("/files", methods=["POST"])
def files():
    if request.method == "POST":
        print("###### POST")
        audio_file = request.files["audio_file"]
        user_note = request.files["user_note"]
        print(f"** audio_file: {audio_file.filename}")
        print(f"** user_note: {user_note.filename}")
        if audio_file and allowed_file(audio_file.filename):
            audio_filename = secure_filename(audio_file.filename)
            audio_file.save(os.path.join(app.config["UPLOAD_FOLDER"], audio_filename))
            print("Done saving audio_file")
        if user_note and allowed_file(user_note.filename):
            note_filename = secure_filename(user_note.filename)
            user_note.save(os.path.join(app.config["UPLOAD_FOLDER"], note_filename))
            print("Done saving user_note")

        return jsonify({"audio_filename": audio_filename, "note_filename": note_filename})


"""
input: audio file, user notes, min/max length of summarization
output: dict containing `script_start_time`, `script`, `summary`, `score`, `user_note` as keys 
"""


@app.route("/upload", methods=["GET", "POST"])
def upload():

    _dict = {
        "script_start_time": [],
        "script": [],
        "summary": [],
        "score": [],  # 0-1
        "user_note": [],
    }

    if request.method == "POST":
        print("###### POST")
        result = request.json
        print(f"result: {result}")
        print(f"get_json: {request.get_json()}")
        min_length = result["min_length"]
        max_length = result["max_length"]
        audio_filename = result["audio_filename"]
        note_filename = result["note_filename"]
        print(f"min_length: {min_length}, max_length: {max_length}")
        print(f"audio: {audio_filename}, note: {note_filename}")

        _dict, save_name = get_script_from_audio(audio_filename, _dict)
        """
        df = pd.read_csv("MattCutts_2011U_script.csv")
        _dict['script_start_time'] = df['script_start_time']
        _dict['script'] = df['script']
        save_name = "MattCutts_2011U_script"
        """
        _dict = summarization(_dict, min_length, max_length)
        _dict = get_score(_dict)
        _dict = align_user_note(_dict, note_filename, save_name)

        return jsonify(_dict)

    elif request.method == "GET":
        print("###### GET")


"""
input: revised user notes, min/max length of summarization
output: dict containing `script_start_time`, `script`, `summary`, `score`, `user_note` as keys 
"""


@cross_origin(origin="*")
@app.route("/revise", methods=["GET", "POST", "OPTIONS"])
def revise():
    my_res = flask.Response()
    if request.method == "OPTIONS":  # CORS preflight
        print("###### OPTIONS")
        return _build_cors_prelight_response()
    elif request.method == "POST":
        my_res.headers.add("Access-Control-Allow-Origin", "*")
        result = request.form.to_dict()
        print(result)
        _dict = result["dict"]
        min_length = result["min_length"]
        max_length = result["max_length"]
        _dict = summarization(_dict, min_length=min_length, max_length=max_length)
        _dict = get_score(_dict)
        return _dict
    else:
        raise NotImplementedError("GET method is not implemented in revise()")


"""
input: min/max_length, drag_text 
output: summarized text
"""


@cross_origin(origin="*")
@app.route("/drag", methods=["GET", "POST", "OPTIONS"])
def drag():
    my_res = flask.Response()
    ## do summarization
    if request.method == "OPTIONS":  # CORS preflight
        print("###### OPTIONS")
        return _build_cors_prelight_response()
    elif request.method == "POST":
        my_res.headers.add("Access-Control-Allow-Origin", "*")
        result = request.form.to_dict()
        min_length = result["min_length"]
        max_length = result["max_length"]
        drag_text = result["drag_text"]

        _dict = {"script": [drag_text], "summary": []}
        _dict = summarization(_dict, min_length=min_length, max_length=max_length)
        return _dict["summary"][0]
    else:
        raise NotImplementedError("GET method is not implemented in revise()")


# 이걸 어떻게 할지? -> front측에서 진행
"""
@app.route("/threshold", methods=["GET", "POST"])
def threshold():
    return "threshold"
"""


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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


def convert2mono(input_file, output_file):
    try:
        command = ["sox", input_file, "-c", "1", output_file]
        subprocess.Popen(command)
        return True
    except:
        return False


def summarization(_dict, min_length=30, max_length=180):
    try:
        _input = [_script for _script in _dict["script"]]
        _output = summarizer(
            _input, min_length=min_length, max_length=max_length, no_repeat_ngram_size=3
        )
        for _elem in _output:
            _dict["summary"].append(_elem["summary_text"])
        return _dict
    except:
        raise RuntimeError("Error in Summarization")


def get_score(_dict):
    total_summary = summarizer(
        "".join(_dict["script"]),
        min_length=100,
        max_length=300,
        no_repeat_ngram_size=3,
    )[0]["summary_text"]

    dataset = NLIDataset(tokenizer, _dict, total_summary)
    dataloader = DataLoader(
        dataset, shuffle=False, batch_size=10, drop_last=False, num_workers=8
    )
    print("~!~!~!~ generate!")

    for batch in dataloader:
        generated_ids = model.model.generate(
            batch["source_ids"].to("cuda:0"),
            attention_mask=batch["src_mask"].to("cuda:0"),
            use_cache=True,
            max_length=5,
            early_stopping=True,
        )
        preds = tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        print(f"~!~!~! Pred: {preds}")
        for pred in preds:
            if pred == "contradiction":
                _dict["score"].append(0)
            elif pred == "entailment":
                _dict["score"].append(1)
            elif pred == "neutral":
                _dict["score"].append(0.5)
            else:
                print(f"#### pred: {pred}")
                _dict["score"].append(0.5)
    return _dict


def align_user_note(_dict, user_notes_name, audio_name):
    # get dict from user_notes
    user_note = {"start_time": [], "note": []}
    with open(os.path.join(UPLOAD_FOLDER, user_notes_name)) as f:
        lines = f.readlines()
        for line in lines:
            line = line.split("\n")[0]
            print(line)
            _time, _note = line.split("\t")
            _time = int(_time.split(":")[0])
            print(f"time: {_time}, note: {_note}")
            user_note["start_time"].append(_time)
            user_note["note"].append(_note)

    note_idx = 0
    note_total_num = len(user_note["start_time"])
    for i, _start in enumerate(_dict["script_start_time"]):
        if note_idx == note_total_num:
            _dict["user_note"].append([])
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
                note_idx < note_total_num
                and user_note["start_time"][note_idx] < next_start
            ):
                print(
                    f"### NOTE idx: {note_idx} time: {user_note['start_time'][note_idx]} note: {user_note['note'][note_idx]}"
                )
                _user_note.append(user_note["note"][note_idx])
                note_idx += 1
        _dict["user_note"].append(_user_note)

    df = pd.DataFrame(_dict)
    df.to_csv(os.path.join(UPLOAD_FOLDER, f"{audio_name}_info.csv"))

    return _dict


"""
input - audio file
output - dict {'script_start_time': [], 'script': []}, audio_name

Functions
- convert .wav file to mono type
- split the audio file to 50 sec
- get the script by google API
- return dict containing the script and its starting time 
"""


def get_script_from_audio(audio, _script_dict, write_script=False):
    _dict = {"script_start_time": [], "script": []}

    ## convert input `audio` file to google API input format
    try:
        audio_name = "".join(audio.split(".")[:-1])
        print(f"## Working on {audio_name}")

        success = convert2mono(os.path.join(UPLOAD_FOLDER, audio), f"mono_{audio}")
        if not success:
            raise ValueError("Audio format is not convertible")

        os.system(f"python video-splitter/ffmpeg-split.py -f mono_{audio} -s 50")
        audio_path = os.path.join(UPLOAD_FOLDER, audio_name)
        os.system(f"mkdir {audio_path}")
        os.system(f"mv mono_{audio_name}-* {audio_path}")
    except:
        raise RuntimeError("Failed to convert the files into google API input format")

    ## STT
    try:
        paths = os.listdir(audio_path)
        client = speech.SpeechClient()

        if write_script:
            f = open(os.path.join(UPLOAD_FOLDER, f"{audio_name}_script.txt"), "w")
            print(f"Writing at {audio_name}_script.txt")

        for path_idx, path in enumerate(paths):
            with io.open(os.path.join(audio_path, path), "rb") as audio_file:
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
                if write_script:
                    f.write(alternatives.transcript)
                temp_str = alternatives.transcript.split("\n")[0]
                _str += temp_str

            _dict["script"].append(_str)
            _dict["script_start_time"].append(50 * path_idx)
            _script_dict["script"].append(_str)
            _script_dict["script_start_time"].append(50 * path_idx)

        df = pd.DataFrame(_dict)
        df.to_csv(f"{audio_name}_script.csv")
        if write_script:
            f.close()
    except:
        raise RuntimeError("Failed in STT")

    return _script_dict, audio_name


def initsetting(summarize_model="t5-base"):
    print("**** Initial Setting ****")
    # load summarizer model
    summarizer = pipeline(
        "summarization",
        model=summarize_model,
        tokenizer=summarize_model,
        framework="pt",
        device=1,
    )
    print("**** Done Loading Summarizer ****")

    # load tokenizer and model for scoring
    tokenizer = T5Tokenizer.from_pretrained("t5-base")
    config = T5Config()
    model = T5ForConditionalGeneration(config).to("cuda:0")
    args = get_args()
    model = T5FineTuner(args)
    model = T5FineTuner.load_from_checkpoint(
        checkpoint_path="./t5_base_nli_lr5.ckpt", hparams=args
    )
    model.eval()
    model.to("cuda:0")
    print("**** Done Loading T5 ****")

    return summarizer, tokenizer, model


if __name__ == "__main__":
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "1,2"
    os.environ["TRANSFORMERS_CACHE"] = "/mnt/.cache/huggingface"

    summarizer, tokenizer, model = initsetting()
    """
    _dict = {'script_start_time': [], 'script': [], 'summary': [], 'score': [], 'user_note': []}
    # _dict, save_name = get_script_from_audio("MattCutts_2011U_copy.wav", _dict)
    df = pd.read_csv("MattCutts_2011U_copy_script.csv")
    _dict['script_start_time'] = df['script_start_time']
    _dict['script'] = df['script']
    _dict = summarization(_dict, 30, 150)
    _dict = get_score(_dict)
    _dict = align_user_note(_dict, "myNotes.txt", "MattCutts_2011U_copy")
    df = pd.DataFrame(_dict)
    df.to_csv(os.path.join(UPLOAD_FOLDER, "MattCutts_2011U_copy_info.csv"))
    """
    app.run(host="0.0.0.0", port=8887, debug=True)
