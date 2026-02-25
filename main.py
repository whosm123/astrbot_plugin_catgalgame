from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_catgalgame", "Makari", "一个基于 AstrBot 的猫娘galgame插件", "0.0.1")
class MyPlugin(Star):

    admins = ["2642677199"]
    players = ["3248876632","2642677199"]
    love_levels = {"2642677199":5,"3248876632":0}

    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info("message_chain: %s",message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    @filter.command_group("admin")
    def admin(self):
        """管理员指令组，仅管理员可使用"""
        pass

    @admin.group("love_level")
    def love_level(self):
        """管理玩家的好感度"""
        pass

    @love_level.command("set")
    async def set_love_level(self,event: AstrMessageEvent,user_id:str,love_level : int):
        """设置玩家的好感度"""
        sender_id = event.get_sender_id()
        if sender_id not in self.admins:
            logger.warn("QQ号 %s 访问管理员接口 love_level.set_love_level 失败：权限不足",sender_id)
            yield event.plain_result(f"您（{sender_id}）不是管理员，无权限设置好感度。")

        if user_id in self.love_levels:
            logger.info("正在将 %s 的好感度设置为 %d",user_id,love_level)
            if not -5 <= love_level <= 5 :
                logger.info("管理员 %s 设置好感度失败：仅能设置-5 ~ 5之间的好感度。",sender_id)
                yield event.plain_result("设置失败：仅能设置-5 ~ 5之间的好感度。")
            else:
                self.love_levels[user_id] = love_level
                logger.info("管理员 %s 设置好感度成功：%s 的好感度被设置为：%d",sender_id,user_id,love_level)
                yield event.plain_result(f"管理员 {sender_id} 设置好感度成功：{user_id} 的好感度被设置为 : {love_level}")

    @filter.command("search_love_level")
    async def search_love_level(self, event: AstrMessageEvent, user_id: str = "N",):
        """查询玩家的好感度"""
        if user_id == "N":
            user_id = event.get_sender_id()

        if user_id not in self.love_levels:
            logger.error("要查询的用户 %s 不在玩家名单中",user_id)
            yield event.plain_result(f"错误：要查询的用户 {user_id} 不在玩家名单中。")

        result = self.love_levels[user_id]
        logger.info("查询了 %s 的好感度为 %d",user_id,result)
        yield event.plain_result(f"查询成功：玩家 {user_id} 的好感度为 {result}")

    @filter.command("join")
    async def join_game(self,event: AstrMessageEvent):
        """新玩家加入游戏"""
        user_id = event.get_sender_id()
        if user_id in self.players:
            logger.error("%s 加入失败：已在玩家名单中", user_id)
            yield event.plain_result(f"加入失败：{user_id} 已在玩家名单中。")
        else:
            self.players.append(user_id)
            self.love_levels[user_id] = 0
            logger.info("玩家 %s 成功加入游戏。",user_id)
            yield event.plain_result(f"加入游戏成功：玩家 {user_id} 的初始好感度设置为 ：0。\r\n来和零奈聊天，触发事件增加好感度吧！")



