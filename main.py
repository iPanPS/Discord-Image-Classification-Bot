import discord
from discord.ext import commands
import random
import os
import requests
import uuid
from keras.preprocessing import image
from keras.models import load_model
import numpy as np

description = '''An example bot to showcase the discord.ext.commands extension
module.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

#function get_class

def get_class(model_path, label_path, image_path):
    # load model
    model = load_model(model_path)

    # load label
    with open(labels_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Preprocess the image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Rescale the image

    # Inferensi
    predictions = model.predict(img_array)


    predict_idx = np.argmax(predictions, axis=1)
    predict_label = labels[predict_idx[0]]

    return predict_label

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hi! I am a bot {bot.user}!')

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)

@bot.command()
async def meme(ctx):
    img_name = random.choice(os.listdir('images'))
    with open(f'images/{img_name}','rb') as f:
        # Mari simpan file perpustakaan/library Discord yang dikonversi dalam variabel ini!
                    picture = discord.File(f)
   # Kita kemudian dapat mengirim file ini sebagai tolok ukur!
    await ctx.send(file=picture)
    
def get_duck_image_url():    
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']


@bot.command('duck')
async def duck(ctx):
    '''Setelah kita memanggil perintah bebek (duck), program akan memanggil fungsi get_duck_image_url'''
    image_url = get_duck_image_url()
    await ctx.send(image_url)

def get_meme_image_url():    
    url = 'https://meme-api.com/gimme'
    res = requests.get(url)
    data = res.json()
    return data['url']


@bot.command('random-meme')
async def randmeme(ctx):
    image_url = get_meme_image_url()
    await ctx.send(image_url)


# untuk check input dari user kirim attachment
@bot.command(name='upload_image')
async def upload_image(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]

        if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            unique_filename = f"{uuid.uuid4()}_{attachment.filename}"
            file_path = f"images/{unique_filename}"

            await attachment.save(file_path)

            # Proses integrasi AI
            model_path = "keras_model.h5"
            labels_path = "labels.txt"
            result = get_class(model_path,labels_path, file_path)

            # Inform user the result from AI
            await ctx.send(f"Your AI Predict: {result}")


            # Inform the user that the image has been saved
            # await ctx.send(f"Image saved as {unique_filename}")
        else:
            # Inform the user that the attachment is not an image
            await ctx.send("The attached file is not an image. Please upload a .png, .jpg, .jpeg, or .gif file.")
    else:
        # Inform the user that no attachment was found
        await ctx.send("No attachment found in the message. Please upload an image.")

bot.run("tokn")
