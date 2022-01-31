from unicodedata import name
import discord
from discord.ext import commands
from commands.Music import Music

from config import TOKEN


if __name__ == '__main__':
    bot = commands.AutoShardedBot(
        command_prefix="?", help_command=None
    )
    bot.add_cog(Music(bot))
    bot.run(TOKEN)
