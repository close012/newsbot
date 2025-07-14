from bs4 import BeautifulSoup, SoupStrainer
import csv
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
import requests
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename='discord.log',encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    user = await bot.fetch_user("196554995460472832")
    await user.send("Online!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command(name='news')
async def news(ctx):
    headers = {'User-Agent':'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.89 Mobile Safari/537.36'}
    try:
        response = requests.get('https://fc.toyamanao.com/news/1/?page=1', headers=headers)
    except requests.exceptions.RequestException as e:
        await ctx.send(e)
    url = "https://fc.toyamanao.com"
    
    database = []
    try:
        with open('database.csv', "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                database.append(row)
                
    except FileNotFoundError as e:
        await ctx.send(e)

    existing_links = set()
    for index in range(len(database)):
        existing_links.add(database[index]["link"])
        
    content = BeautifulSoup(response.content, 'html.parser', parse_only=SoupStrainer(class_="clearfix"))    
    sent = False
    for link in content:
            row = {"link":url+link["href"], "date":link.select(".date")[0].text, "title":link.select(".tit")[0].text}
            if row["link"] in existing_links:
                pass
            else:
                existing_links.add(row["link"])
                database.append(row)
                sent = True
                await ctx.send(row["date"] + " " + row["title"] + "\n" + row["link"])
    if not sent:
        await ctx.send("No news")

    try:
        with open('database.csv', 'w', newline='') as csvfile:
            fieldnames = ['link', 'date', 'title']
            writer = csv.DictWriter(csvfile, fieldnames= fieldnames)
            writer.writeheader()
            writer.writerows(database)
    except FileNotFoundError as e:
        await ctx.send(e)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
