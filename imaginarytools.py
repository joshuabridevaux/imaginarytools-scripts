import openai
import json
import requests
from datetime import datetime
import os

useMock = False
openai.api_key = os.getenv('OPENAI_KEY')
model = "gpt-3.5-turbo"
num_images = 1
image_size = "1024x1024"
current_datetime = datetime.now()

response_message_mock = """
{"name": "EcoGauge",
"summary": "EcoGauge is a revolutionary tool designed to help individuals and businesses track and reduce their carbon footprint. With its user-friendly interface and advanced analytics, EcoGauge provides real-time data on energy consumption, waste generation, and carbon emissions. By identifying areas of improvement and suggesting eco-friendly alternatives, EcoGauge empowers users to make informed decisions and take meaningful actions towards a more sustainable future.",
"article": "Introducing EcoGauge: Your Ultimate Companion in the Journey Towards Sustainability\n\nIn today's world, where climate change and environmental degradation are pressing concerns, it is crucial for individuals and businesses to take responsibility for their carbon footprint. That's where EcoGauge comes in - a game-changing tool that revolutionizes the way we track and reduce our impact on the planet.\n\nEcoGauge is not just another carbon footprint calculator; it is a comprehensive platform that provides real-time data and actionable insights. With its user-friendly interface, anyone can easily monitor their energy consumption, waste generation, and carbon emissions. Whether you're an individual looking to make sustainable choices in your daily life or a business aiming to become more eco-friendly, EcoGauge has got you covered.\n\nOne of the key features of EcoGauge is its advanced analytics. The tool analyzes your data and generates personalized reports, highlighting areas where you can make improvements. It suggests eco-friendly alternatives and provides tips on reducing energy consumption and waste generation. By following these recommendations, you can not only reduce your carbon footprint but also save money in the long run.\n\nEcoGauge also allows you to set goals and track your progress over time. Whether you want to reduce your energy consumption by 20% or cut down on waste by implementing recycling programs, EcoGauge helps you stay accountable and motivated. You can even compete with friends or colleagues to see who can achieve the most significant environmental impact.\n\nWith EcoGauge, sustainability becomes a way of life. By making small changes in our daily habits and choices, we can collectively make a big difference. So, why not start your journey towards a greener future today? Sign up for EcoGauge and join the growing community of eco-conscious individuals and businesses. Together, we can create a more sustainable world for generations to come.\n\nRemember, every action counts!"}
"""

mock_image_url = "https://i.imgur.com/NWWQIXz.jpeg"

def read_used_titles():
    with open('used_titles.txt') as f:
        line = f.readline()
    line = line.rstrip('\n')
    return line

def save_used_title(titles):
    file1 = open("used_titles.txt", "w")
    file1.write(f"{titles}")
    file1.close()

def completeChat(messages):
    if useMock:
        return response_message_mock
    else:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            n=1,
            stop=None,
            temperature=0
        )
        #print(f"ChatGPT: {response}") #debug
        return response['choices'][0]['message']['content']

def generate_image_urls(image_prompt, num_images):
    urls = []
    if useMock:
        for x in range(num_images):
            urls.append(mock_image_url)
    else:
        response = openai.Image.create(
            prompt=f"{image_prompt}",
            n=num_images,
            size=image_size
        )
        for x in range(num_images):
            urls.append(response['data'][x]['url'])

    return urls

def save_url_to_file(url, filename):
    img_data = requests.get(url).content
    with open(f"{filename}", 'wb') as handler:
        handler.write(img_data)

def create_post(publish_date, title, image_name, article_text):
    date_text = current_datetime.strftime("%Y-%m-%d")
    filename = f"{date_text}-{title}.md"
    first_sentence = article_text.partition('\n')[0]
    remaining_body = article_text.split("\n",2)[2]
    with open(f"{filename}", 'w') as handler:
        handler.write("---\n")
        handler.write(f"layout: default\n")
        handler.write(f"title: {title}\n")
        handler.write(f"date: {date_text}\n")
        handler.write(f"author: AI\n")
        handler.write("---\n")
        handler.write("\n")
        handler.write(f"# {first_sentence}\n")
        handler.write("\n")
        handler.write(f"![{title}](/imaginarytools/assets/{image_name})\n")
        handler.write("\n")
        handler.write(f"{remaining_body}\n")


#########################################################
#main
#########################################################
previous_ideas = read_used_titles()
prompt = f"""Create the name of an imaginary tool excluding the ideas {previous_ideas}.  Then create a 400 character or less
description of what that tool looks like and a blog article about that tool and
return them following the json format below:
{{
"name": tool name,
"summary": tool description,
"article": article text
}}"""

messages=[
{"role": "user", "content": f"{prompt}"}
]
response = completeChat(messages)
jsonResponse = json.loads(response, strict = False)

#parse into components
print(jsonResponse)
tool_name = jsonResponse['name']
tool_summary = jsonResponse['summary']
tool_article = jsonResponse['article']
print(f"Name: {tool_name}")
print(f"Summary: {tool_summary}")
print(f"Article: {tool_article}")

save_used_title(f"{previous_ideas}, {tool_name}")

#generate image
image_urls = generate_image_urls(tool_summary, num_images)

image_filename = (f"{current_datetime}.jpg")
save_url_to_file(image_urls[0], image_filename)

create_post(current_datetime, tool_name, image_filename, tool_article)
