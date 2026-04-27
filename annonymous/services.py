import json
import requests
from groq import Groq
from django.conf import settings


def generate_roadmap(student, goal):
    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
You are an expert AI learning coach. Create a detailed personalized learning roadmap.

STUDENT PROFILE:
- Name: {student.full_name}
- Experience Level: {student.experience_level}
- Current Skills: {student.skills}
- Interests: {student.interests}

STUDENT GOAL:
{goal}

Respond ONLY with this exact JSON format (no extra text):

{{
  "title": "Short roadmap title",
  "summary": "2-3 sentence personalized summary",
  "total_weeks": 12,
  "weeks": [
    {{
      "week_range": "Week 1-2",
      "topic": "Topic Name",
      "description": "What to learn and why",
      "resources": ["Resource 1", "Resource 2"],
      "youtube_search": "exact search query for YouTube"
    }}
  ],
  "skills_gained": ["skill1", "skill2"],
  "final_outcome": "What student can do after completing this path",
  "tips": ["Tip 1", "Tip 2"]
}}
"""

    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": prompt}],
        max_tokens = 2500,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def fetch_youtube_videos(query, max_results=3):
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        return []
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "q": query + " free full tutorial",
            "type": "video",
            "key": api_key,
            "maxResults": max_results,
            "part": "snippet",
            "order": "relevance",
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        videos = []
        for item in data.get("items", []):
            vid_id = item["id"]["videoId"]
            snip = item["snippet"]
            videos.append({
                "title": snip["title"],
                "channel": snip["channelTitle"],
                "thumbnail": snip["thumbnails"]["medium"]["url"],
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "video_id": vid_id,
            })
        return videos
    except Exception as e:
        print(f"YouTube API error: {e}")
        return []


# def generate_full_path(student, goal):
#     roadmap = generate_roadmap(student, goal)
#     all_videos = {}
#     for week in roadmap.get("weeks", []):
#         search_query = week.get("youtube_search", week["topic"])
#         videos = fetch_youtube_videos(search_query, max_results=2)
#         all_videos[week["week_range"]] = videos
#     return roadmap, all_videos
def generate_full_path(student, goal):
    roadmap = generate_roadmap(student, goal)
    all_videos = {}
    for week in roadmap.get("weeks", []):
        # Try youtube_search first, then topic
        search_query = week.get("youtube_search") or week.get("topic", "programming tutorial")
        print(f"Searching YouTube for: {search_query}")  # ← add this
        videos = fetch_youtube_videos(search_query, max_results=2)
        print(f"Found {len(videos)} videos")  # ← add this
        all_videos[week["week_range"]] = videos
    return roadmap, all_videos