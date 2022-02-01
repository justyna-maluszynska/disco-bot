from discord.ext import commands
import youtube_dl
import discord
import queue


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._queue = queue.Queue()

    async def play_next_song(self, ctx):
        ctx.voice_client.stop()
        song = self._queue.get()
        await self.play_song(ctx, song)

    async def play_song(self, ctx, song):
        embed = discord.Embed(
            title="", description=f"[{song['title']}]({song['url']})", color=0xff8040)
        embed.set_author(name="Radiożyd playing",
                         icon_url="https://cdn-icons-png.flaticon.com/512/609/609982.png")
        embed.add_field(name="Author", value=song['artist'], inline=True)
        embed.add_field(name="Duration", value=song['duration'], inline=True)
        embed.set_thumbnail(url=song['thumbnail'])
        embed.add_field(name="Requested by", value=ctx.author.mention)
        await ctx.send(embed=embed)

        ctx.voice_client.play(
            song['source'], after=lambda _: self.bot.loop.create_task(self.play_next_song(ctx)))

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
            
            embed = discord.Embed(
                title="", description=f"[{info['title']}]({info['url']})", color=0x0080c0)
            embed.set_author(name="Added to queue",
                             icon_url="https://cdn-icons-png.flaticon.com/512/609/609982.png")
            embed.add_field(name="Author", value=info['artist'], inline=True)
            embed.add_field(name="Duration",
                            value=info['duration'], inline=True)
            embed.add_field(name="Position in queue",
                            value=self._queue.qsize()+1, inline=True)
            embed.set_thumbnail(url=info['thumbnail'])
            await ctx.send(embed=embed)

            self._queue.put(
                {'source': source, 'title': info['title'], 'artist': info['uploader'], 'duration': info['duration'], 'thumbnail': info['thumbnail'], 'url': url})

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(arg, download=False)
            await load_audio(info)

        if not ctx.voice_client.is_playing():
            await self.play_next_song(ctx)

    @commands.command(aliases=['s'])
    async def pause(self, ctx: commands.Context):
        ctx.voice_client.pause()

    @commands.command(aliases=['r'])
    async def resume(self, ctx: commands.Context):
        ctx.voice_client.resume()

    @commands.command(aliases=['fs'])
    async def skip(self, ctx: commands.Context):
        ctx.voice_client.stop()
