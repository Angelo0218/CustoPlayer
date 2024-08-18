import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os
from dotenv import load_dotenv
import logging
import json

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
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
        self.title = data.get('title', 'Unknown')
        self.url = data.get('url', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        if url.startswith('https://music.ajlo.org'):
            # 處理本地音樂文件
            data = {'title': url.split('/')[-1], 'url': url}
            return cls(discord.FFmpegPCMAudio(url), data=data)
        else:
            # 處理 YouTube 或其他在線音源
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                data = data['entries'][0]
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.volume = 0.5
        self.current = None
        self.audio_player_task = None
    
        # 讀取 musicData.json
        with open('musicData.json', 'r', encoding='utf-8') as f:
            self.music_data = json.load(f)
        
        # 創建歌曲字典
        self.song_dict = {song['title'].lower(): f"https://music.ajlo.org{song['url']}" for song in self.music_data}

    async def cog_load(self):
        self.audio_player_task = self.bot.loop.create_task(self.audio_player_loop())
        logger.info("MusicBot cog 已加載")

    async def audio_player_loop(self):
        while True:
            self.play_next_song.clear()
            try:
                self.current = await self.queue.get()
                self.current.volume = self.volume
                self.bot.voice_clients[0].play(self.current, after=self.toggle_next)
                logger.info(f"Now playing: {self.current.title}")
                await self.play_next_song.wait()
            except Exception as e:
                logger.error(f"Error in audio player task: {e}")
                await asyncio.sleep(1)

    def toggle_next(self, error=None):
        if error:
            logger.error(f'Player error: {error}')
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    @commands.command(name='play', help='播放音樂')
    async def play(self, ctx, *, query):
        """播放音樂"""
        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("你需要先加入一個語音頻道。")
                return

        query_lower = query.lower()
        if query_lower in self.song_dict:
            # 如果查詢匹配本地音樂庫中的歌曲
            url = self.song_dict[query_lower]
        else:
            # 如果不匹配，則假設它是一個 YouTube URL 或搜索查詢
            url = query

        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            await self.queue.put(player)
            await ctx.send(f'已將 {player.title} 加入播放隊列')

            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                await self.play_next_song.set()
        except Exception as e:
            await ctx.send(f"發生錯誤：{str(e)}")
            logger.error(f"播放時發生錯誤：{str(e)}")

    @commands.command(name='volume', help='設置音量 (0-100)')
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("未連接到語音頻道。")

        if 0 <= volume <= 100:
            self.volume = volume / 100
            if ctx.voice_client.source:
                ctx.voice_client.source.volume = self.volume
            await ctx.send(f"音量已設置為 {volume}%")
            logger.info(f"Volume set to {volume}%")
        else:
            await ctx.send("音量必須在 0 到 100 之間")

    @commands.command(name='pause', help='暫停當前播放的歌曲')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("歌曲已暫停")
            logger.info("Song paused")
        else:
            await ctx.send("目前沒有正在播放的歌曲")

    @commands.command(name='resume', help='恢復播放暫停的歌曲')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("歌曲已恢復播放")
            logger.info("Song resumed")
        else:
            await ctx.send("沒有暫停的歌曲可以恢復播放")

    @commands.command(name='stop', help='停止播放並清空隊列')
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue = asyncio.Queue()  # 清空隊列
            self.current = None
            await ctx.send("已停止播放並清空隊列")
            logger.info("Playback stopped and queue cleared")
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

    @commands.command(name='skip', help='跳過當前歌曲')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("已跳過當前歌曲")
            logger.info("Song skipped")
        else:
            await ctx.send("目前沒有正在播放的歌曲")

    @commands.command(name='clear', help='清空播放隊列')
    async def clear(self, ctx):
        self.queue = asyncio.Queue()
        await ctx.send("播放隊列已清空")
        logger.info("Queue cleared")

    @commands.command(name='help', help='顯示所有可用的命令')
    async def help(self, ctx):
        help_text = "可用的命令:\n\n"
        for command in self.get_commands():
            help_text += f"!{command.name}: {command.help}\n"
        await ctx.send(help_text)

    @commands.command(name='local_songs', help='顯示可用的本地歌曲列表')
    async def local_songs(self, ctx):
        """顯示可用的本地歌曲列表"""
        song_list = "\n".join(self.song_dict.keys())
        await ctx.send(f"可用的本地歌曲：\n```\n{song_list}\n```")

    @commands.command(name='可以說老婆我愛你嗎', help='播放特定音頻並發送愛心消息')
    async def love_wife(self, ctx):
        # 檢查用戶是否在語音頻道中
        if not ctx.author.voice:
            return await ctx.send("請先加入一個語音頻道！")

        channel = ctx.author.voice.channel
        
        # 連接到語音頻道或移動到用戶所在的頻道
        if ctx.voice_client is None:
            await channel.connect()
        elif ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)

        # 音頻文件路徑
        audio_file = '1134103817437323264.ogg'

        # 檢查文件是否存在
        if not os.path.isfile(audio_file):
            return await ctx.send("抱歉，找不到音頻文件。")

        # 停止當前正在播放的音頻（如果有）
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        # 播放音頻
        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_file))

        # 發送愛心消息
        await ctx.send("❤️❤️❤️ 老婆我愛你！❤️❤️❤️")

async def setup(bot):
    await bot.add_cog(MusicBot(bot))
    logger.info("MusicBot cog 已設置完成")

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    await setup(bot)

bot.run(TOKEN)
