import asyncio,os
from datetime import datetime,timedelta
from typing import Union
from ntgcalls import ConnectionNotFound,TelegramServerError
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls,exceptions,types
from pytgcalls.pytgcalls_session import PyTgCallsSession
import config
from SHUKLAMUSIC import LOGGER,YouTube,app
from SHUKLAMUSIC.misc import db
from SHUKLAMUSIC.utils.database import add_active_chat,add_active_video_chat,get_lang,get_loop,group_assistant,is_autoend,music_on,remove_active_chat,remove_active_video_chat,set_loop,get_autoplay
from SHUKLAMUSIC.utils.exceptions import AssistantErr
from SHUKLAMUSIC.utils.formatters import check_duration,seconds_to_min,speed_converter
from SHUKLAMUSIC.utils.inline.play import stream_markup
from SHUKLAMUSIC.utils.stream.autoclear import auto_clean
from strings import get_string

autoend,counter={},{}

async def clear(chat_id:int):
    db[chat_id]=[]
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def init(self):
        PyTgCallsSession.notice_displayed=True
        self.userbot1=Client("SHUKLAAss1",api_id=config.API_ID,api_hash=config.API_HASH,session_string=str(config.STRING1))
        self.one=PyTgCalls(self.userbot1,cache_duration=100)
        self.userbot2=Client("SHUKLAAss2",api_id=config.API_ID,api_hash=config.API_HASH,session_string=str(config.STRING2))
        self.two=PyTgCalls(self.userbot2,cache_duration=100)
        self.userbot3=Client("SHUKLAAss3",api_id=config.API_ID,api_hash=config.API_HASH,session_string=str(config.STRING3))
        self.three=PyTgCalls(self.userbot3,cache_duration=100)
        self.userbot4=Client("SHUKLAAss4",api_id=config.API_ID,api_hash=config.API_HASH,session_string=str(config.STRING4))
        self.four=PyTgCalls(self.userbot4,cache_duration=100)
        self.userbot5=Client("SHUKLAAss5",api_id=config.API_ID,api_hash=config.API_HASH,session_string=str(config.STRING5))
        self.five=PyTgCalls(self.userbot5,cache_duration=100)

    def _build_stream(self,source:str,video:bool,ffmpeg:str|None=None)->types.MediaStream:
        flags="-threads 0"
        if ffmpeg: flags+=f" {ffmpeg}"
        return types.MediaStream(media_path=source,audio_parameters=types.AudioQuality.MEDIUM,video_parameters=types.VideoQuality.HD_720p,audio_flags=types.MediaStream.Flags.REQUIRED,video_flags=types.MediaStream.Flags.AUTO_DETECT if video else types.MediaStream.Flags.IGNORE,ffmpeg_parameters=flags)

    async def _play_on_assistant(self,client,chat_id,stream):
        await client.play(chat_id=chat_id,stream=stream,config=types.GroupCallConfig(auto_start=False))

    async def pause_stream(self,chat_id):
        await (await group_assistant(self,chat_id)).pause(chat_id)

    async def resume_stream(self,chat_id):
        await (await group_assistant(self,chat_id)).resume(chat_id)

    async def stop_stream(self,chat_id):
        assistant=await group_assistant(self,chat_id)
        try:
            await clear(chat_id)
            await assistant.leave_call(chat_id,close=False)
        except: pass

    async def stop_stream_force(self,chat_id):
        for string,client in [(config.STRING1,self.one),(config.STRING2,self.two),(config.STRING3,self.three),(config.STRING4,self.four),(config.STRING5,self.five)]:
            if string:
                try: await client.leave_call(chat_id,close=False)
                except: pass
        try: await clear(chat_id)
        except: pass

    async def speedup_stream(self,chat_id,file_path,speed,playing):
        assistant=await group_assistant(self,chat_id)
        if str(speed)!="1.0":
            base=os.path.basename(file_path)
            chatdir=os.path.join(os.getcwd(),"playback",str(speed))
            os.makedirs(chatdir,exist_ok=True)
            out=os.path.join(chatdir,base)
            if not os.path.isfile(out):
                vs={"0.5":2.0,"0.75":1.35,"1.5":0.68,"2.0":0.5}.get(str(speed),1.0)
                proc=await asyncio.create_subprocess_shell(f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} {out}",stdin=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
                await proc.communicate()
        else: out=file_path
        dur=int(await asyncio.get_event_loop().run_in_executor(None,check_duration,out))
        played,con_seconds=speed_converter(playing[0]["played"],speed)
        duration=seconds_to_min(dur)
        stream=self._build_stream(out,playing[0]["streamtype"]=="video",f"-ss {played} -to {duration}")
        if str(db[chat_id][0]["file"])!=str(file_path): raise AssistantErr("Umm")
        await self._play_on_assistant(assistant,chat_id,stream)
        if not playing[0].get("old_dur"):
            db[chat_id][0]["old_dur"]=db[chat_id][0]["dur"]
            db[chat_id][0]["old_second"]=db[chat_id][0]["seconds"]
        db[chat_id][0].update({"played":con_seconds,"dur":duration,"seconds":dur,"speed_path":out,"speed":speed})

    async def force_stop_stream(self,chat_id):
        assistant=await group_assistant(self,chat_id)
        try: db.get(chat_id).pop(0)
        except: pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try: await assistant.leave_call(chat_id,close=False)
        except: pass

    async def skip_stream(self,chat_id:int,link:str,video:Union[bool,str]=None,image:Union[bool,str]=None):
        assistant=await group_assistant(self,chat_id)
        await self._play_on_assistant(assistant,chat_id,self._build_stream(link,bool(video)))

    async def seek_stream(self,chat_id,file_path,to_seek,duration,mode):
        assistant=await group_assistant(self,chat_id)
        await self._play_on_assistant(assistant,chat_id,self._build_stream(file_path,mode=="video",f"-ss {to_seek} -to {duration}"))

    async def stream_call(self,link):
        assistant=await group_assistant(self,config.LOG_GROUP_ID)
        await self._play_on_assistant(assistant,config.LOG_GROUP_ID,self._build_stream(link,True))
        await asyncio.sleep(.2)
        try: await assistant.leave_call(config.LOG_GROUP_ID,close=False)
        except: pass

    async def join_call(self,chat_id:int,original_chat_id:int,link,video:Union[bool,str]=None,image:Union[bool,str]=None):
        assistant=await group_assistant(self,chat_id)
        language=await get_lang(chat_id)
        _=get_string(language)
        userbot=getattr(assistant,"app",None) or getattr(assistant,"_app",None) or assistant
        ASSISTANT_ID=8708580286
        try:
            await userbot.get_chat_member(chat_id,"me")
        except:
            try: await app.add_chat_members(chat_id,ASSISTANT_ID); await asyncio.sleep(.5)
            except: pass
            try: await app.approve_chat_join_request(chat_id,ASSISTANT_ID); await asyncio.sleep(.3)
            except: pass
            try: await userbot.get_chat_member(chat_id,"me")
            except:
                try:
                    inv=await app.create_chat_invite_link(chat_id)
                    await userbot.join_chat(inv.invite_link)
                    await asyncio.sleep(.5)
                except: pass
        try:
            await self._play_on_assistant(assistant,chat_id,self._build_stream(link,bool(video)))
        except exceptions.NoActiveGroupCall: raise AssistantErr(_["call_8"])
        except (exceptions.NoAudioSourceFound,ConnectionNotFound,TelegramServerError): raise AssistantErr(_["call_10"])
        except: raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video: await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id]={}
            if len(await assistant.get_participants(chat_id))==1: autoend[chat_id]=datetime.now()+timedelta(minutes=1)

    async def change_stream(self,client,chat_id:int):
        check=db.get(chat_id)
        loop=await get_loop(chat_id)
        try:
            if loop==0: popped=check.pop(0)
            else:
                popped=None
                await set_loop(chat_id,loop-1)
            await auto_clean(popped)
            if not check:
                await clear(chat_id)
                return await client.leave_call(chat_id,close=False)
        except:
            try: await clear(chat_id); return await client.leave_call(chat_id,close=False)
            except: return

        queued=check[0]["file"]
        _=get_string(await get_lang(chat_id))
        title=check[0]["title"].title()
        user=check[0]["by"]
        original_chat_id=check[0]["chat_id"]
        streamtype=check[0]["streamtype"]
        videoid=check[0]["vidid"]
        db[chat_id][0]["played"]=0

        if check[0].get("old_dur"):
            db[chat_id][0]["dur"]=check[0]["old_dur"]
            db[chat_id][0]["seconds"]=check[0]["old_second"]
            db[chat_id][0]["speed_path"]=None
            db[chat_id][0]["speed"]=1.0

        video=str(streamtype)=="video"

        if "live_" in queued:
            n,link=await YouTube.video(videoid,True)
            if n==0: return await app.send_message(original_chat_id,_["call_6"])
            try: await self._play_on_assistant(client,chat_id,self._build_stream(link,video))
            except: return await app.send_message(original_chat_id,_["call_6"])
            run=await app.send_message(original_chat_id,_["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}",title[:23],check[0]["dur"],user),reply_markup=InlineKeyboardMarkup(stream_markup(_,chat_id)))
            db[chat_id][0]["mystic"]=run
            db[chat_id][0]["markup"]="tg"

        elif "vid_" in queued:
            mystic=await app.send_message(original_chat_id,_["call_7"])
            try: file_path,direct=await YouTube.download(videoid,mystic,videoid=True,video=video)
            except: return await mystic.edit_text(_["call_6"])
            try: await self._play_on_assistant(client,chat_id,self._build_stream(file_path,video))
            except: return await app.send_message(original_chat_id,_["call_6"])
            await mystic.delete()
            run=await app.send_message(original_chat_id,_["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}",title[:23],check[0]["dur"],user),reply_markup=InlineKeyboardMarkup(stream_markup(_,chat_id)))
            db[chat_id][0]["mystic"]=run
            db[chat_id][0]["markup"]="stream"

        elif "index_" in queued:
            try: await self._play_on_assistant(client,chat_id,self._build_stream(videoid,video))
            except: return await app.send_message(original_chat_id,_["call_6"])
            run=await app.send_message(original_chat_id,_["stream_2"].format(user),reply_markup=InlineKeyboardMarkup(stream_markup(_,chat_id)))
            db[chat_id][0]["mystic"]=run
            db[chat_id][0]["markup"]="tg"

        else:
            try: await self._play_on_assistant(client,chat_id,self._build_stream(queued,video))
            except: return await app.send_message(original_chat_id,_["call_6"])

            if videoid=="telegram":
                link=config.SUPPORT_GROUP
            elif videoid=="soundcloud":
                link=config.SUPPORT_GROUP
            else:
                link=f"https://t.me/{app.username}?start=info_{videoid}"

            run=await app.send_message(original_chat_id,_["stream_1"].format(link,title[:23],check[0]["dur"],user),reply_markup=InlineKeyboardMarkup(stream_markup(_,chat_id)))
            db[chat_id][0]["mystic"]=run
            db[chat_id][0]["markup"]="tg" if videoid in ("telegram","soundcloud") else "stream"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        for string,client in [(config.STRING1,self.one),(config.STRING2,self.two),(config.STRING3,self.three),(config.STRING4,self.four),(config.STRING5,self.five)]:
            if string: await client.start()

    async def decorators(self):
        for string,client in [(config.STRING1,self.one),(config.STRING2,self.two),(config.STRING3,self.three),(config.STRING4,self.four),(config.STRING5,self.five)]:
            if not string: continue
            @client.on_update()
            async def update_handler(_,update:types.Update,_client=client):
                if isinstance(update,types.StreamEnded):
                    if update.stream_type==types.StreamEnded.Type.AUDIO: await self.change_stream(_client,update.chat_id)
                elif isinstance(update,types.ChatUpdate):
                    if update.status in [types.ChatUpdate.Status.KICKED,types.ChatUpdate.Status.LEFT_GROUP,types.ChatUpdate.Status.CLOSED_VOICE_CHAT]:
                        await self.stop_stream(update.chat_id)

SHUKLA=Call()
