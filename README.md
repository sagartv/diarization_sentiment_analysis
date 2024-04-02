## Instructions to run code:
1) Create a new virtual environment using conda/pipenv/any other tool
2) install the packages in the requirements.txt file using "pip install -r requirements.txt"
3) use python3 app.py to run the app.py file and open the browser on port 3000
4) Attach an audio file on the landing page and click "Mine Sentiment"
5) The app will first diarize the audio file, the transcript of it is split and each speaker's text is individually fed into OpenAI's GPT 3.5 for sentiment analysis.
6) You will then get a personality analysis of each speaker through their speech, along with a Big Five Personality Traits analysis.

## Description:
This was an interesting app to build, and I'm glad I got to work with DeepGram's API. The main challenge was setting up DeepGram and OpenAI's api and data structures to line up with each other.
As of this version, the audio file is first transcribed and diarized by DeepGram's API. This transcript is then split up by speaker, and each speaker's speech is individually analyzed by OpenAI's GPT 3.5.
The output contains general analysis of the speaker's tone, psychology and intent, as well as a Big Five Personality
To further improve this, I would like to expose GPT to both speakers conversations to give it more context, as well as update to GPT 4. I would also like to be more creative and analytical with the personality analysis.
