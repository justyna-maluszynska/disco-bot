from ast import alias
import asyncio
from discord.ext import commands
import youtube_dl
import discord
import queue


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._queue = queue.Queue()

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send('Spierdalaj murzynie.')
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, arg):
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        YDL_OPTIONS = {'format': 'bestaudio'}

        async def load_audio(info):
            url = info['formats'][0]['url']

            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }

            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            self._queue.put(source)

        def play_song():
            song = self._queue.get()
            ctx.voice_client.play(song, after=lambda _: play_song())

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(arg, download=False)
            await load_audio(info)

        if not ctx.voice_client.is_playing():
            await play_song()

    @commands.command(aliases=['s'])
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()

    @commands.command(aliases=['r'])
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()
