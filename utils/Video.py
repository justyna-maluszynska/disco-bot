import datetime
import youtube_dl
import discord
from discord.ext import commands

from config.config import ICON_URL


YDL_OPTIONS = {"format": "bestaudio/best"}

ytdl = youtube_dl.YoutubeDL(YDL_OPTIONS)


class Video:
    def __init__(self, search_url):
        video = self._extract_info(search_url)
        video_format = video["formats"][0]
        self.url = video_format["url"]
        self.title = video["title"]
        self.author = video["uploader"]
        self.duration = str(datetime.timedelta(seconds=video["duration"]))
        self.seconds_duration = video["duration"]
        self.thumbnail = video["thumbnail"]

    def _extract_info(self, search_url):
        if search_url.startswith("https://www.youtube.com/watch"):
            ytdl.extract_info(search_url, download=False)

        else:
            info = ytdl.extract_info(f"ytsearch:{search_url}", download=False)

        if "entries" in info:
            info = info["entries"][0]

        return info

    def embed_now_playing(self, ctx: commands.Context):
        embed = discord.Embed(
            title="", description=f"[{self.title}]({self.url})", color=0xFF8040
        )
        embed.set_author(
            name="Radiożyd playing",
            icon_url="https://cdn-icons-png.flaticon.com/512/609/609982.png",
        )
        # embed.add_field(name="Author", value=self.author, inline=True)
        embed.add_field(name="Duration", value=self.duration, inline=True)
        embed.set_thumbnail(url=self.thumbnail)
        embed.add_field(name="Requested by", value=ctx.author.mention)

        return embed

    def embed_added_to_queue(self, position):
        embed = discord.Embed(
            title="",
            description=f"[{self.title}]({self.url})",
            color=0x0080C0,
        )
        embed.set_author(name="Added to queue", icon_url=ICON_URL)
        # embed.add_field(name="Author", value=self.author, inline=True)
        embed.add_field(name="Duration", value=self.duration, inline=True)
        embed.add_field(name="Position in queue", value=position, inline=True)
        embed.set_thumbnail(url=self.thumbnail)

        return embed
