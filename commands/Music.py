from discord.ext import commands
import discord
import queue
from gtts import gTTS

from config.config import ICON_URL
from utils.Video import Video


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._queue = queue.Queue()

    async def _play_next_song(self, ctx):
        ctx.voice_client.stop()
        if self._queue.qsize() > 0:
            song = self._queue.get()
            await self._play_song(ctx, song)

    async def _play_song(self, ctx, song: Video):
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        source = await discord.FFmpegOpusAudio.from_probe(song.url, **FFMPEG_OPTIONS)

        ctx.voice_client.play(
            source,
            after=lambda _: self.bot.loop.create_task(self._play_next_song(ctx)),
        )

        # TODO delete when song finish or skip
        await ctx.send(embed=song.embed_now_playing(ctx))

        # await message.add_reaction("⏯")
        # await message.add_reaction("⏭")
        # await message.add_reaction("🔁")

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
    async def play(self, ctx: commands.Context, *, arg):
        print("zareagował")
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if ctx.author.voice is not None:

            async def load_audio(video: Video):
                if self._queue.qsize() > 0:
                    await ctx.send(
                        embed=video.embed_added_to_queue(self._queue.qsize() + 1)
                    )
                self._queue.put(video)

            info = Video(arg)
            await load_audio(info)

            if not ctx.voice_client.is_playing():
                await self._play_next_song(ctx)

    @commands.command(aliases=["s"])
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()

    @commands.command(aliases=["r"])
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()

    @commands.command(aliases=["fs"])
    async def skip(self, ctx: commands.Context):
        ctx.voice_client.stop()

    # @commands.command()
    # async def tts(self, ctx: commands.Context, text):
    #     global gTTS
    #     speech = gTTS(text=text, lang="es-us", slow=False)
    #     speech.save("audio.mp3")

    #     voice = ctx.voice_client

    #     voice.play(discord.FFmpegPCMAudio("audio.mp3"), after=None)
