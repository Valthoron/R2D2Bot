import io
import json
import os
import random

import discord

from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

PICTURE_HEIGHT = 300
LABEL_SIZE = 30
LABEL_STROKE = 2
LABEL_PADDING = 5


class SpeciesPictures(commands.Cog):
    def __init__(self, bot):
        self._bot: commands.Bot = bot

        with open('data/species_pictures.json', 'r') as jsonfile:
            self._pictures = json.load(jsonfile)
            self._keys = list(self._pictures.keys())

    @commands.command(name="species", aliases=["sp"])
    async def picture_cmd(self, context: commands.Context, *, list: str = ""):
        species_list = list.split()
        images = []
        species_names = []

        for species in species_list:
            for key in self._keys:
                if key.startswith(species):
                    image_path = os.path.join('data/species_pictures', random.choice(self._pictures[key]))
                    img = Image.open(image_path)
                    img = img.resize((int(img.width * (PICTURE_HEIGHT / img.height)), PICTURE_HEIGHT), Image.LANCZOS)
                    images.append(img)
                    species_names.append(key)
                    break

        if images:
            total_width = sum(img.width for img in images)
            new_image = Image.new('RGBA', (total_width, PICTURE_HEIGHT), (255, 255, 255, 0))

            draw = ImageDraw.Draw(new_image)
            font = ImageFont.truetype("arial.ttf", LABEL_SIZE)

            x_offset = 0
            for img, species in zip(images, species_names):
                new_image.paste(img, (x_offset, 0), img.convert('RGBA'))

                text = species.capitalize()
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] + LABEL_PADDING
                text_x = x_offset + (img.width - text_width) / 2
                text_y = PICTURE_HEIGHT - text_height
                draw.text((text_x, text_y), text, font=font, fill="white", stroke_width=LABEL_STROKE, stroke_fill="black")

                x_offset += img.width

            with io.BytesIO() as image_binary:
                new_image.save(image_binary, 'PNG')
                image_binary.seek(0)
                await context.send(file=discord.File(fp=image_binary, filename='picture.png'))

    async def cog_before_invoke(self, context: commands.Context):
        await context.message.delete()


async def setup(bot):
    await bot.add_cog(SpeciesPictures(bot))
