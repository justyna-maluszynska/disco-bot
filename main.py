from discord.ext import commands
from commands.Music import MusicPlayer

from config.config import TOKEN


if __name__ == '__main__':
    bot = commands.AutoShardedBot(
        command_prefix="?", help_command=None
    )
    bot.add_cog(MusicPlayer(bot))
    bot.run(TOKEN)
