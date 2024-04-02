import os
import flask
from flask import Flask, render_template, request
import ast
import openai
from openai import OpenAI

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)


app = Flask(__name__)


#route to this function when nothing succeeds the "/" in the url
@app.route('/')
def render_home():

  #Render the home.html page
  return render_template('home.html')



def get_lines(audio_file):
    
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key=os.environ.get('DEEPGRAM_API_KEY'))
        TAG = 'SPEAKER '


        with open(audio_file, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            punctuate = True,
            diarize = True
        )

        lines = []

        # # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        response_json = response.to_json()
        words = ast.literal_eval(response_json)["results"]["channels"][0]["alternatives"][0]["words"]
        speakers = set()
        curr_speaker = 0
        curr_line = ''
        for word_struct in words:
          word_speaker = word_struct["speaker"]
          word = word_struct["punctuated_word"]
          if word_speaker == curr_speaker:
            curr_line += ' ' + word
          else:
            tag = TAG + str(curr_speaker) + ':'
            full_line = tag + curr_line + '\n'
            curr_speaker = word_speaker
            speakers.add(curr_speaker)
            lines.append(full_line)
            curr_line = ' ' + word
        lines.append(TAG + str(curr_speaker) + ':' + curr_line)
        return lines, speakers



    except Exception as e:
        print(f"Exception: {e}")


def detect_sentiment(prompt):
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    system_role = f''' You are a sentiment mining assistant who needs to mine the text of the speaker, and comment on the following: TONE, INTENTION, PSYCHOLOGICAL TRAITS,
    ATTITUDE TOWARDS THE OTHER SPEAKER(S).
    In a separate section titled BIG FIVE PERSONALITY ANALYSIS, rate the speaker on the BIG FIVE PERSONALITY TRAITS: EXTRAVERSION/EXTROVERSION, AGREEABLENESS, OPENNESS, CONSCIENTOUSNESS, and NEUROTICISM.
    Also assign a numerical rating out of 5 in the format RATING:(rating/5) on each of the BIG FIVE PERSONALITY TRAITS.
    '''
    
    response = client.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [{'role':'system', 'content': system_role},
                    {'role':'user', 'content': prompt}],
        temperature = 0)
    return response.choices[0].message.content

def split_text_by_speaker(lines, speakers):
    speaker_text = []
    for i in range(len(speakers)+1):
        speaker_text.append('')
    for line in lines:
        if line.startswith('SPEAKER'):
            speaker_id = int(line[8])
            speaker_text[speaker_id] += line
    return speaker_text

def mine_sentiment(speaker_text):
    sentiments = []
    for speaker in speaker_text:
       if len(speaker) > 1:
          sentiments.append(str('SPEAKER ' + str(speaker_text.index(speaker)) + ':' + '\n') + detect_sentiment(speaker))
    return sentiments


#Use POST method to get form data from the questionnaire
@app.route('/mine_sentiment', methods= ['post'])
def process_submission():
    audio=request.files['musicFile']
    audio_name=audio.filename
    audio.save(audio_name)
    lines, speakers = get_lines(audio_name)
    speaker_text = split_text_by_speaker(lines,speakers)
    sentiments = mine_sentiment(speaker_text)
    return render_template('result.html', data = sentiments)
    


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=3000, debug = False)