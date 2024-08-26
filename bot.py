import asyncio
import subprocess
import io
from pydub import AudioSegment
from shazamio import Shazam
from twitchio.ext import commands

# Hardcoded Twitch credentials (yes i know hard coding this is a bad idea for security but lazy coder moment)
TWITCH_TOKEN = 'oauth:'
TWITCH_CHANNELS = ['CHANNELNAMEHERE']
TWITCH_CLIENT_ID = ''

# Capture audio from Twitch stream using Streamlink and FFmpeg
def capture_audio(stream_url):
    streamlink_command = ['streamlink', stream_url, 'audio_only', '-O']
    ffmpeg_command = [
        'ffmpeg', '-i', 'pipe:0', '-f', 'wav', '-ac', '1', '-ar', '44100', 'pipe:1'
    ]
    
    try:
        streamlink_process = subprocess.Popen(streamlink_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=streamlink_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        streamlink_process.stdout.close()  # Allow streamlink_process to receive a SIGPIPE if ffmpeg_process exits
        return ffmpeg_process
    except Exception as e:
        print(f"Error starting audio capture: {e}")
        return None

# Process and segment audio
def get_audio_segment(process, duration=5):
    buffer_size = int(44100 * 2 * duration)  
    try:
        audio_data = process.stdout.read(buffer_size)
        if not audio_data:
            return None
        return AudioSegment.from_wav(io.BytesIO(audio_data))
    except Exception as e:
        print(f"Error processing audio segment: {e}")
        return None

# Recognize music using Shazamio
async def recognize_music(segment):
    shazam = Shazam()
    segment.export('current_segment.wav', format='wav')
    try:
        out = await shazam.recognize('current_segment.wav')
        return out
    except Exception as e:
        print(f"Error during music recognition: {e}")
        return None  # Return None if there's an error during recognition

# token functionality and PING/PONG handling
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=TWITCH_CHANNELS)
        self.process = None  # Initialize process attribute

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_raw_message(self, message):
        if message.content == "PING :tmi.twitch.tv":
            await self._ws.send_pong(message.content)
            print("PONG sent in response to PING")

    @commands.command(name='song')
    async def cmd_song(self, ctx):
        try:
            stream_url = 'https://www.twitch.tv/CHANNELNAMEHEREPLZREPLACE'  # Replace with the actual Twitch channel URL
            self.process = capture_audio(stream_url)
            
            if self.process:
                segment = get_audio_segment(self.process)
                if segment:
                    music_info = await recognize_music(segment)
                    if music_info and 'track' in music_info:
                        song = music_info['track']['title']
                        artist = music_info['track']['subtitle']
                        await ctx.send(f'Currently playing: {song} by {artist}')
                    else:
                        await ctx.send('No song detected.')
                else:
                    await ctx.send('No audio detected.')
            else:
                await ctx.send('Audio capture process is not initialized.')
            
            # Clean up the process
            if self.process:
                self.process.terminate()

        except Exception as e:
            print(f"Error in cmd_song command: {e}")

# Main function to run the bot
async def main():
    bot = Bot()
    await bot.start()