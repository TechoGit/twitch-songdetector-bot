This python based bot will detect songs being played by running them through the Shazama API by using ShazamIO

after the !song command has been requested in twitch chat the bot will download a 5 seceond clip of the stream using Streamlink then converting it to audio file via ffmpeg before processing it through ShazamIO

then if all goes well the bot will output the name of the song and artist in the twitch chat 

If you want to use the python bot, please make sure to have the requirements.txt installed, ffmpeg already
and replace the channel name with the channel then that you're planning to use it with on top of having oauth code for your bot to use in twitch chat 


Known Bugs

The bot won't be able to detect music if the stream goes down or something happens to it, if this does the bot will need to be restarted 

I'm thinking of solving this by making the bot read chat and if it sees the message from StreamElements then it will restart itself as StreamElements will automatically post a message in chat saying X is Live Now with X


This bot is designed for Ravena the Twitch Streamer


