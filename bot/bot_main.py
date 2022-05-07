import os
import asyncio
import random

import discord
from discord import Intents
from discord.ext import commands, tasks

from load_environment import load_environment
from bot_functions import discord_message_analysis, bad_word_finder, select_answer, image_selection
from xur_destiny2 import XurChecker


load_environment()

CHANNEL_ID = os.getenv('CHANNEL_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PREFIX = '!'

bot = commands.Bot(command_prefix=PREFIX, intents=Intents.all())
bot.intents.members = True
bot.remove_command('help')

xur_checker = XurChecker()


@bot.event
async def on_ready():
    print(f'{bot.user.name} в сети.')
    is_xur_arrived.start()


@bot.event
async def on_member_join(member):
    await member.send(f'Рад тебя видеть, {member.mention}, добро пожаловать! '
                      f'Можешь ознакомиться со списком доступных команд !help и обязательно прочти наши !rules. '
                      f'Мой баннхаммер не знает пощады!')

    guest_role = discord.utils.get(member.guild.roles, id=780843833817563166)
    await member.add_roles(guest_role)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{ctx.author.mention}, команда не идентифицирована. Введите корректную команду.')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, низкий уровень доступа. В использовании команды отказано.')

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, команда введена неверно. Пропущен аргумент данной команды.')


@bot.event
async def on_message(message):
    message_author = message.author

    if message_author != bot.user and not message.content.startswith('!'):
        try:
            result = discord_message_analysis(message)
        except UnboundLocalError:
            result = -1

        if result == 'hello':
            await message.channel.send(f'{message_author.mention}, привет!')
        elif result == 'by':
            await message.channel.send(f'До скорого, {message_author.mention}!')
        elif result == 'bad':
            bad_word = bad_word_finder(message)
            answer = select_answer()
            await message.channel.send(f'Выявлен нарушитель священного пункта № 1 правил Общества '
                                       f'в связи с использованием "{bad_word}"!')
            await message.channel.send(f'{message_author.mention} {answer}')
        elif result == 'help':
            await message.channel.send(f'{message_author.mention}, хочешь узнать список команд? Напиши !help в чат.')

    await bot.process_commands(message)


@bot.command()
async def help(ctx):
    await ctx.channel.purge(limit=1)

    embed = discord.Embed(
        colour=discord.Color.gold(),
        title='Навигация по командам:'
    )

    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

    embed.add_field(name=f'{PREFIX}help', value='Выводит список команд.', inline=False)
    embed.add_field(name=f'{PREFIX}rules', value='Выводит список правил сервера.', inline=False)
    embed.add_field(name=f'{PREFIX}boobs', value='Безмерно радует всех Сиськолюбов.', inline=False)
    embed.add_field(name=f'{PREFIX}xur', value='Сообщает местонахождение Зура.', inline=False)
    embed.add_field(name=f'{PREFIX}duel @target_name',
                    value='Позволяет вызвать на дуэль и испытать удачу. Проигравший отправляется в мут на 60 секунд.',
                    inline=False)

    await ctx.send(embed=embed)


@bot.command(aliases=['правила', 'Правила'])
async def rules(ctx):
    await ctx.channel.purge(limit=1)

    embed = discord.Embed(
        colour=discord.Color.gold(),
        title='Правила сервера:'
    )

    embed.set_author(
        name=bot.user.name,
        icon_url=bot.user.avatar_url
    )

    embed.add_field(
        name='Пункт № 0.',
        value='Всегда уважай Великий Разум!',
        inline=False
    )
    embed.add_field(
        name='Пункт № 1.',
        value='Мы здесь отдыхаем, поэтому будь дружелюбнее.',
        inline=False
    )
    embed.add_field(
        name='Пункт № 2.',
        value='Запрещено быть душным мудилой и говорить "можно скажу?" в голосовом чате.',
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount_to_delete=2):
    await ctx.channel.purge(limit=amount_to_delete)


@bot.command(aliases=['бан', 'Бан'])
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)

    mute_role = discord.utils.get(ctx.message.guild.roles, id=780439303603355648)
    await member.add_roles(mute_role)

    await ctx.send(f'Великий Разум пожелал, чтобы {member.mention} немного помолчал.')
    await member.send(f'Фреймы призваны помогать людям, поэтому я здесь. Тебя забанил {ctx.author.name}. '
                      f'Причина мне неизвестна, однако Великий Разум ничего не делает просто так!')


@bot.command(aliases=['разбан', 'Разбан'])
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)

    mute_role = discord.utils.get(ctx.message.guild.roles, id=780439303603355648)
    await member.remove_roles(mute_role)

    await ctx.send(f'Великий Разум сжалился над {member.mention} и он снова может говорить.')
    await member.send(f'Ты снова можешь говорить. '
                      f'Пожалуйста, для твоего блага, постарайся больше не раздражать Великий Разум.')


@bot.command(aliases=['дуэль', 'Дуэль'])
async def duel(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)

    duelist1 = ctx.author.name
    duelist2 = member.name
    duelists = [duelist1, duelist2]

    mute_role = discord.utils.get(ctx.message.guild.roles, id=780439303603355648)

    await ctx.send(f'{duelist1} бросает перчатку вызова {duelist2}. Приготовиться к дуэли! '
                   f'Великий Разум назначил меня вашим секундантом.')
    await ctx.send(f'3!')
    await ctx.send(f'2!')
    await ctx.send(f'1!')
    await ctx.send(f'Начинайте дуэль!')

    winner = random.choice(duelists)
    loser = duelist2 if duelist1 == winner else duelist1

    await ctx.send(f'Победил {winner}! Бездыханное тело {loser} ждет своего призрака. Или он более не достоин Света?!')

    if loser == duelist2:
        await member.add_roles(mute_role)
        await asyncio.sleep(60)
        await member.remove_roles(mute_role)
    else:
        await ctx.author.add_roles(mute_role)
        await asyncio.sleep(60)
        await ctx.author.remove_roles(mute_role)

    await ctx.send(f'Призрак в очередной раз вдохнул жизнь в {loser}.')


@bot.command(aliases=['сиськи', 'Сиськи'])
async def boobs(ctx):
    await ctx.channel.purge(limit=1)

    image_url = image_selection()

    embed = discord.Embed(
        colour=discord.Color.gold(),
        description='Решил порадовать друзей.'
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

    # Проверка URL изображения. Если длина менее 20 символов, значит изображение не спарсилось и нужно вывести ошибку.
    if len(image_url) < 25:
        embed.add_field(
            name='Но у него ничего не вышло!',
            value='Видимо, все девочки заняты, попробуй позже <:harold:970308021546795038>',
            inline=False
        )
    else:
        embed.set_image(url=image_url)

    await ctx.send(embed=embed)


@bot.command(aliases=['зур', 'Зур'])
async def xur(ctx):
    await ctx.channel.purge(limit=1)

    xur_location = xur_checker.get_xur_location()

    await ctx.send(f'{ctx.author.mention} {xur_location}')


@tasks.loop(hours=1)
async def is_xur_arrived():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(CHANNEL_ID))

    if xur_checker.is_xur_here():
        if not xur_checker.message_is_sent:
            xur_location = xur_checker.get_xur_location()
            await channel.send(f'{xur_location}')
            xur_checker.message_is_sent = True
    if not xur_checker.is_xur_here():
        xur_checker.message_is_sent = False


if __name__ == '__main__':
    bot.run(BOT_TOKEN)
