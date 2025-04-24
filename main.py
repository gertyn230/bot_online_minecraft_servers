import os
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Подключение к серверу Minecraft
MC_SERVER = JavaServer.lookup(f"{os.getenv('MC_SERVER_ADDRESS')}:{os.getenv('MC_SERVER_PORT', 25935)}")
SERVER_NAME = os.getenv("MC_SERVER_NAME", "Minecraft")  # Название сервера из .env

@tasks.loop(minutes=1)
async def update_status():
    try:
        status = MC_SERVER.status()
        players = status.players.online
        max_players = status.players.max
        activity = discord.Game(name=f" {SERVER_NAME} ({players}/{max_players})")
    except Exception:
        activity = discord.Game(name="🔴 Сервер оффлайн")
    
    await bot.change_presence(activity=activity)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    if not update_status.is_running():
        update_status.start()

@bot.command(name="онлайн", help="Показать онлайн игроков")
async def online(ctx):
    try:
        status = MC_SERVER.status()
        players = status.players.online
        max_players = status.players.max

        # Получаем список игроков
        player_list = status.raw.get("players", {}).get("sample", [])
        player_names = ", ".join([p["name"] for p in player_list]) if player_list else "Нет игроков"

        embed = discord.Embed(
            title=f"Статус сервера {SERVER_NAME}",
            description=f"🟢 Онлайн: {players}/{max_players} игроков",
            color=0x00ff00
        )
        embed.add_field(name="Игроки онлайн", value=player_names)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"🔴 Ошибка: Сервер недоступен ({e})")

# Проверяем, есть ли токен
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise ValueError("Ошибка: отсутствует DISCORD_TOKEN в .env файле!")

if __name__ == "__main__":
    bot.run(token)
