# CS492(E) Human AI Interaction
Repository for Final Project of CS492E, KAIST, 2021 Spring

**doctor-notes**

## About the Course
Humans and AI are more closely interacting than ever before, in all areas of our work, education, and life. As more intelligent machines are entering our lives, their accuracy and performance are not the only important factor that matters. As designers of such technology, we have to carefully consider the user experience of AI in order for AI to be of practical value. In this course, we will explore various dimensions of human-AI interaction, including ethics, explainability, design process involving AI, visualization, human-AI collaboration, recommender systems, and a few notable application areas.

A side goal of this course is to encourage all of us to bridge the gap between the two fields of HCI and AI. As a step toward this vision, we want to encourage students with HCI and AI background to mingle, interact, discuss, and collaborate through this course. We expect most students taking this course to have background knowledge in either HCI or AI through at least intro-level coursework. If you’re unsure if you meet this criterion, please contact the course staff immediately. Having background in both is great, although not required.  

[Course Website](https://human-ai.kixlab.org/)

## About the Final Project
### Our system: Doctor-Notes
The system aims to support users to have helpful notes so that they would be able to remember or recollect the ideas from the lecture. [Our survey](https://docs.google.com/spreadsheets/d/18FxLU3xmcSGTml23OVw57pN_nvVM-6hofVSfdTYVtRQ/edit?usp=sharing) result shows that users have a hard time when they are trying to do two works at a same time: taking notes, listening to the lecture. We tried to solve this problem by letting users concentrate on the lecture and take notes afterward with our service. You can try our system [here](https://drnotes-492e.web.app)

### Contributors
* Junha Hyung
* Jeongeon Park
* Hyunji Lee

### Design Project Milestones
* DP0: Team Formation
* DP1: Ideation
* DP2: Pitch [Slides](https://docs.google.com/presentation/d/18MUD5E3eXFNqXGP2AUoiThn4lr2aBdyAVEYhUwT2unY/edit?usp=sharing)
* DP3: High-fi Prototype [Report](https://demo.hedgedoc.org/Y6VnFUWARveC62BEVaBERA?view)
* DP4: Final Presentation [Slides](https://docs.google.com/presentation/d/1SvtGmtLQXbY220LcE8mowvoa2vEx4V1TWx-ZmMsKgBs/edit?usp=sharing)
* DP5: Final Paper & Video


## About the Repository
### [Front](https://github.com/amy-hyunji/doctor-notes/tree/main/front)
There are five components in the front directory
* [Home.js](./front/src/components/Home.js): Main page that contains all the other components
* [LeftPanel.js](./front/src/components/LeftPanel.js): The panel where lecture recordings are transcribed and shown
* [MiddlePanel.js](./front/src/components/MiddlePanel.js): The panel where summarizations take place
* [RightPanel.js](./front/src/components/RightPanel.js): The panel where user's note takes place
* [NewNote.js](./front/src/components/NewNote.js): The intro page where the user drops the recording file and the note

To run, please refer to [this README](./front/README.md).

### [Server](https://github.com/amy-hyunji/doctor-notes/tree/main/server)
#### Framework & Libraries
* Flask
#### How to run?
* `python app.py`
#### Functions
* *files()*: function that saves audio and user note files from the user
* *upload()*: overall pipeline of our service and return all the information to the user
* *revise()*: called when user revise the script
* *drag()*: called when user wants summarization of specific part of the script
* *summarization()*: function that summarize all the script inside _dict
* *get_score()*: function that returns the score (how relative the summarization is to overall script) of each chunk
* *align_user_note()*: align user notes with script chunks by starting time
* *get_script_from_audio()*
    * 1. convert audio file to mono
    * 2. split the audio into chunks of 50sec (limitation of the google API model)
    * 3. get the text by speech to text google API model
* *initsetting()*: initial setting which loads...
    * 1. summarization model
    * 2. scoring model
    * 3. tokenizer 
 
### [Models](https://github.com/amy-hyunji/doctor-notes/tree/main/keyword)
#### Framework & Libraries
* Python, Pytorch, huggingface, pytorch-lightning
#### How to run?
* We trained two models
  * 1. [T5](https://arxiv.org/abs/1910.10683) 
    * [SNLI](https://nlp.stanford.edu/projects/snli/) dataset
    * train.py, models.py, data.py, jsonl2csv.py
    * `python train.py`
  * 2. [Bert](https://arxiv.org/abs/1810.04805) 
    * [PAWS](https://github.com/google-research-datasets/paws)
    * bert_train.py
    * `python bert_train.py`
#### Explanations
* 4 level threshold for T5 and any threshold for Bert
* Current service is T5. 
* If you want to run the server, contact `alee6868@kaist.ac.kr` for some dependency files and model weights
  

