from discord.ext import commands
import discord
import queue
from gtts import gTTS

from utils.Video import Video
from utils.Spotify import Spotify


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spotify = Spotify()
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

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            return await ctx.send("You cannot use command")

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *, url):

        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if ctx.author.voice is not None:

            async def load_audio(video: Video, silent):
                if not silent:
                    await ctx.send(
                        embed=video.embed_added_to_queue(self._queue.qsize() + 1)
                    )
                self._queue.put(video)

                if not ctx.voice_client.is_playing():
                    await self._play_next_song(ctx)

            if "open.spotify.com/playlist" in url:
                tracks = self.spotify.get_playlist_items_title(url=url)
                for track in tracks:
                    info = Video(track)
                    await load_audio(info, True)
            else:
                info = Video(url)
                await load_audio(info, False)

    @commands.command(aliases=["s"])
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()

    @commands.command(aliases=["r"])
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()

    @commands.command(aliases=["fs"])
    async def skip(self, ctx: commands.Context):
        ctx.voice_client.stop()
