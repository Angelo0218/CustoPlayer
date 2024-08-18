import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os
from dotenv import load_dotenv


# 設置意圖
intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

token = os.getenv('DISCORD_BOT_TOKEN')

# 創建機器人實例
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


# YouTube DL 配置
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'updatetime': False,
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # 取播放列表的第一項
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.bot.loop.create_task(self.audio_player_task())
        self.volume = 0.5  # 默認音量

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            current = await self.queue.get()
            current.volume = self.volume  # 直接設置 YTDLSource 的音量
            self.current = current
            self.bot.voice_clients[0].play(current, after=self.toggle_next)
            await self.play_next_song.wait()

    def toggle_next(self, error=None):
        if error:
            print(f'Player error: {error}')
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    @commands.command(name='play', help='播放指定的歌曲')
    async def play(self, ctx, *, url):
        try:
            if not ctx.message.author.voice:
                await ctx.send("您需要先加入一個語音頻道！")
                return

            channel = ctx.message.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
            elif ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                await self.queue.put(player)

            await ctx.send(f'已將 {player.title} 加入播放隊列')
        except Exception as e:
            await ctx.send(f"發生錯誤: {str(e)}")
            print(f"詳細錯誤: {e}")

    @commands.command(name='volume', help='設置音量 (0-100)')
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("未連接到語音頻道。")

        if 0 <= volume <= 100:
            self.volume = volume / 100
            if ctx.voice_client.source:
                ctx.voice_client.source.volume = self.volume
            await ctx.send(f"音量已設置為 {volume}%")
        else:
            await ctx.send("音量必須在 0 到 100 之間")

    @commands.command(name='pause', help='暫停當前播放的歌曲')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("歌曲已暫停")
        else:
            await ctx.send("目前沒有正在播放的歌曲")

    @commands.command(name='resume', help='恢復播放暫停的歌曲')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("歌曲已恢復播放")
        else:
            await ctx.send("沒有暫停的歌曲可以恢復播放")

    @commands.command(name='stop', help='停止播放並清空隊列')
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue = asyncio.Queue()  # 清空隊列
            await ctx.send("已停止播放並清空隊列")
        else:
            await ctx.send("機器人未連接到語音頻道")

    @commands.command(name='now_playing', help='顯示當前正在播放的歌曲')
    async def now_playing(self, ctx):
        if self.current:
            await ctx.send(f"當前正在播放: {self.current.title}")
        else:
            await ctx.send("目前沒有正在播放的歌曲")

    @commands.command(name='queue', help='顯示播放隊列')
    async def show_queue(self, ctx):
        if self.queue.empty():
            await ctx.send("播放隊列為空")
        else:
            queue_list = list(self.queue._queue)
            queue_text = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(queue_list)])
            await ctx.send(f"播放隊列:\n{queue_text}")

    @commands.command(name='help', help='顯示所有可用的命令')
    async def help(self, ctx):
        help_text = "可用的命令:\n\n"
        for command in self.get_commands():
            help_text += f"!{command.name}: {command.help}\n"
        await ctx.send(help_text)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

async def main():
    async with bot:
        await bot.add_cog(MusicBot(bot))
        await bot.start('token')

if __name__ == "__main__":
    asyncio.run(main())

