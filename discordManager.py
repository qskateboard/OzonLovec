import time
from datetime import datetime

import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from pypresence import Presence

import utils

webhook = DiscordWebhook("https://discord.com/api/webhooks/")
success_webhook = DiscordWebhook("https://discord.com/api/webhooks/")
bad_webhook = DiscordWebhook("https://discord.com/api/webhooks/")

v500 = DiscordWebhook("https://discord.com/api/webhooks/")

def start():
    RPC = Presence("855029468376334346")
    RPC.connect()
    RPC.update(state="Trying to catch Playstation 5", details="Ozon Lovec", start=int(datetime.now().timestamp()), large_image="logo")

    embed = DiscordEmbed(title="Lightning", description='', color='03b2f8')
    embed.add_embed_field(name='Status', value="Initialized", inline=False)
    embed.set_footer(text='Lightning ' + datetime.now().strftime("[%H:%M:%S]"),
                     icon_url="https://i.imgur.com/lSxgZm0.png")
    #webhook.add_embed(embed)
    #webhook.execute()

def detected_product(item):
    product = utils.get_product(item['id'])

    embed = DiscordEmbed(title=item['name'],  url=product['url'], description='', color='b3c01f')
    embed.set_thumbnail(url=product['img'])
    embed.add_embed_field(name='Price', value=item['price'], inline=False)
    embed.add_embed_field(name='Status', value='Restock', inline=False)
    embed.add_embed_field(name='Availability', value='{}'.format(str(item['availability'])), inline=False)
    embed.add_embed_field(name='Site', value="[ozon.ru](https://ozon.ru/)", inline=False)
    embed.set_footer(text='V500 ' + datetime.now().strftime("[%H:%M:%S]"),
                     icon_url="https://i.imgur.com/lSxgZm0.png")
    v500.add_embed(embed)
    v500.execute()


def success_checkout(number, time, uid, express=False):
    product = utils.get_product(uid['id'])

    embed = DiscordEmbed(title=product['name'],  url=product['url'], description='', color='eb01cf')
    embed.set_thumbnail(url=product['img'])
    embed.add_embed_field(name='Account', value="||{}||".format(number))
    embed.add_embed_field(name='Price', value=product['price'])
    embed.add_embed_field(name='Time', value=time)
    embed.add_embed_field(name='Availability', value='{}'.format(str(uid['availability'])))
    embed.add_embed_field(name='Express', value=str(express))
    embed.add_embed_field(name='Site', value="[ozon.ru](https://ozon.ru/)")
    embed.set_footer(text='Lightning ' + datetime.now().strftime("[%H:%M:%S]"),
                     icon_url="https://i.imgur.com/lSxgZm0.png")
    success_webhook.add_embed(embed)
    success_webhook.execute()

def bad_checkout(number, time, message, item, express=False):
    product = utils.get_product(str(item['id']))

    embed = DiscordEmbed(title=product['name'],  url=product['url'], color='f30707')
    embed.set_thumbnail(url=product['img'])
    embed.add_embed_field(name='Account', value="||{}||".format(number))
    embed.add_embed_field(name='Time', value=time)
    embed.add_embed_field(name='Price', value=product['price'])
    embed.add_embed_field(name='Availability', value='{}'.format(str(item['availability'])))
    embed.add_embed_field(name='Express', value=str(express))

    embed.add_embed_field(name='Message', value=message)
    #embed.add_embed_field(name='Site', value="[ozon.ru](https://ozon.ru/)")
    embed.set_footer(text='Lightning ' + datetime.now().strftime("[%H:%M:%S]"),
                     icon_url="https://i.imgur.com/lSxgZm0.png")
    bad_webhook.add_embed(embed)
    bad_webhook.execute()