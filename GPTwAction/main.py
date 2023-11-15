from flask import Flask, request, jsonify, send_from_directory
import os
import json
from waitress import serve
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import random

# Initialize Flask app
app = Flask(__name__)
# Your API Key
youtube_api_key = os.environ['YOUTUBE_API_KEY']

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=youtube_api_key)


# Function to search YouTube and get video details
def youtube_search(query):
  request = youtube.search().list(part="snippet",
                                  q=query,
                                  maxResults=random.randint(3, 5),
                                  type="video")
  response = request.execute()

  video_details = []
  for item in response['items']:
    video_id = item['id']['videoId']
    video_info_request = youtube.videos().list(part="snippet,statistics",
                                               id=video_id)
    video_info_response = video_info_request.execute()

    if video_info_response['items']:
      video_info = video_info_response['items'][0]
      video_details.append({
          "video_id": video_id,
          "title": video_info['snippet']['title'],
          "views": video_info['statistics']['viewCount'],
          "channel": video_info['snippet']['channelTitle']
      })

  return video_details


# Function to extract transcripts using youtube_transcript_api
def get_transcripts(video_details):
  transcripts = []
  for video in video_details:
    video_id = video["video_id"]
    try:
      # Using youtube_transcript_api to get transcript
      transcript_list = YouTubeTranscriptApi.get_transcript(video_id,
                                                            languages=['en'])
      # Combining the text of all transcript parts into one string
      transcript_text = ' '.join([
          transcript['text'] + " [" + str(transcript['start']) + "sec]"
          for transcript in transcript_list
      ])
    except Exception as e:
      transcript_text = f"Error getting transcript: {e}"

    video['transcript'] = transcript_text
    transcripts.append(video)

  return transcripts


@app.route('/test', methods=['GET'])
def test_api():
  return jsonify({"message": "API is working!"})


# Function to send privacy policy
@app.route('/privacy')
def get_privacy_policy():
  return send_from_directory('.', 'privacy.txt', mimetype='text/plain')


# API endpoint for performing YouTube search
@app.route('/youtube_search', methods=['GET'])
def api_youtube_search():
  query = request.args.get('query', default='', type=str)
  if not query:
    return jsonify({"error": "Query parameter is required"}), 400

  video_details = youtube_search(query)
  transcripts = get_transcripts(video_details)

  return jsonify(transcripts)


# # Main Function
# def main():
#   query = "Chatgpt plugin"
#   video_details = youtube_search(query)
#   transcripts = get_transcripts(video_details)

#   # Once transcripts are generated upload transcripts
#   with open('transcripts.json', 'w') as outfile:
#     json.dump(transcripts, outfile, indent=4)

# Start the Flask app
if __name__ == "__main__":
  #app.run(debug=True)
  serve(app, host='0.0.0.0', port="8080")
