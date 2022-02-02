from discord.ext import commands
import youtube_dl
import discord
import queue
import datetime

from config.config import ICON_URL


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._queue = queue.Queue()

    async def play_next_song(self, ctx):
        ctx.voice_client.stop()
        if self._queue.qsize() > 0:
            song = self._queue.get()
            await self.play_song(ctx, song)

    async def play_song(self, ctx, song):
        embed = discord.Embed(
            title="", description=f"[{song['title']}]({song['url']})", color=0xFF8040
        )
        embed.set_author(
            name="Radiożyd playing",
            icon_url="https://cdn-icons-png.flaticon.com/512/609/609982.png",
        )
        embed.add_field(name="Author", value=song["artist"], inline=True)
        embed.add_field(name="Duration", value=song["duration"], inline=True)
        embed.set_thumbnail(url=song["thumbnail"])
        embed.add_field(name="Requested by", value=ctx.author.mention)
        message = await ctx.send(embed=embed)

        ctx.voice_client.play(
            song["source"],
            after=lambda _: self.bot.loop.create_task(self.play_next_song(ctx)),
        )

        await message.add_reaction("⏯")
        await message.add_reaction("⏭")
        await message.add_reaction("🔁")

        # def check(reaction, user):
        #     return str(reaction.emoji) == "✅"

        # try:
        #     reaction = await self.bot.on_reaction_add("reaction_add", check=check)
        #     print(reaction.emoji)

        # except:
        #     print("wybuchło")

    # @commands.Cog.listener("on_reaction_add")
    # async def on_reaction_add(self, reaction, user):
    #     if reaction.emoji == "✅":
    #         print("hej")

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            return await ctx.send("Spierdalaj murzynie.")

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, arg):
        print("zareagował")
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if ctx.author.voice is not None:
            YDL_OPTIONS = {"format": "bestaudio"}

            async def load_audio(info):
                url = info["formats"][0]["url"]

                FFMPEG_OPTIONS = {
                    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    "options": "-vn",
                }

                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

                title, artist, duration, thumbnail = (
                    info["title"],
                    info["uploader"],
                    str(datetime.timedelta(seconds=info["duration"])),
                    info["thumbnail"],
                )

                embed = discord.Embed(
                    title="",
                    description=f"[{title}]({url})",
                    color=0x0080C0,
                )
                embed.set_author(name="Added to queue", icon_url=ICON_URL)
                embed.add_field(name="Author", value=artist, inline=True)
                embed.add_field(name="Duration", value=duration, inline=True)
                embed.add_field(
                    name="Position in queue", value=self._queue.qsize() + 1, inline=True
                )
                embed.set_thumbnail(url=thumbnail)
                await ctx.send(embed=embed)

                self._queue.put(
                    {
                        "source": source,
                        "title": title,
                        "artist": artist,
                        "duration": duration,
                        "thumbnail": thumbnail,
                        "url": url,
                    }
                )

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(arg, download=False)
                await load_audio(info)

            if not ctx.voice_client.is_playing():
                await self.play_next_song(ctx)

    @commands.command(aliases=["s"])
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()

    @commands.command(aliases=["r"])
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()

    @commands.command(aliases=["fs"])
    async def skip(self, ctx: commands.Context):
        ctx.voice_client.stop()
