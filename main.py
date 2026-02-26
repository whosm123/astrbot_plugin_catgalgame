from slack_sdk.models.messages.message import message

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.message_event_result import MessageChain
from astrbot.core.provider.entities import ProviderRequest


@register("astrbot_plugin_catgalgame", "Makari", "一个基于 AstrBot 的猫娘galgame插件", "0.0.1")
class MyPlugin(Star):
    admins = ["2642677199"]
    players = []
    love_levels = {}

    def __init__(self, context: Context):
        super().__init__(context)

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令"""
        # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str  # 用户发的纯文本消息字符串
        message_chain = event.get_messages()  # 用户所发的消息的消息链
        # from astrbot.api.message_components import *
        logger.info("message_chain: %s", message_chain)
        yield event.plain_result(f"[system] Hello, {user_name}, 你发了 {message_str}!")  # 发送一条纯文本消息

    @filter.command_group("admin")
    def admin(self):
        """管理员指令组，仅管理员可使用"""
        pass

    @admin.group("love_level")
    def love_level(self):
        """管理玩家的好感度"""
        pass

    @love_level.command("set")
    async def set_love_level(self, event: AstrMessageEvent, user_id: str, love_level: int):
        """设置玩家的好感度"""
        sender_id = event.get_sender_id()

        if sender_id not in self.admins:
            logger.warn("QQ号 %s 访问管理员接口 love_level.set_love_level 失败：权限不足", sender_id)
            yield event.plain_result(f"[system] 您（{sender_id}）不是管理员，无权限设置好感度。")
            return

        if user_id is None:
            logger.error("管理员 %s 设置好感度失败：user_id 参数为空(None)", sender_id)
            yield event.plain_result("设置失败：user_id 不能为空。")
            return

        user_id = str(user_id).strip()
        if user_id == "":
            logger.error("管理员 %s 设置好感度失败：user_id 参数为空字符串", sender_id)
            yield event.plain_result("设置失败：user_id 不能为空。")
            return

        if user_id not in self.love_levels:
            logger.error("管理员 %s 设置好感度失败：用户 %s 不在玩家名单/好感度表中", sender_id, user_id)
            yield event.plain_result(f"[system] 设置失败：用户 {user_id} 不在玩家名单中。")
            return

        logger.info("正在将 %s 的好感度设置为 %d", user_id, love_level)

        if not -5 <= love_level <= 5:
            logger.info("管理员 %s 设置好感度失败：仅能设置-5 ~ 5之间的好感度。", sender_id)
            yield event.plain_result("设置失败：仅能设置-5 ~ 5之间的好感度。")
            return

        self.love_levels[user_id] = love_level
        logger.info("管理员 %s 设置好感度成功：%s 的好感度被设置为：%d", sender_id, user_id, love_level)
        yield event.plain_result(f"[system] 管理员 {sender_id} 设置好感度成功：{user_id} 的好感度被设置为 : {love_level}")

    @love_level.command("reset")
    async def reset_love_level(self, event: AstrMessageEvent, user_id: str):
        """重置玩家的好感度（重置为 0）"""
        sender_id = event.get_sender_id()

        if sender_id not in self.admins:
            logger.warn("QQ号 %s 访问管理员接口 love_level.reset_love_level 失败：权限不足", sender_id)
            yield event.plain_result(f"[system] 您（{sender_id}）不是管理员，无权限重置好感度。")
            return

        if user_id is None:
            logger.error("管理员 %s 重置好感度失败：user_id 参数为空(None)", sender_id)
            yield event.plain_result("[system] 重置失败：user_id 不能为空。")
            return

        user_id = str(user_id).strip()
        if user_id == "":
            logger.error("管理员 %s 重置好感度失败：user_id 参数为空字符串", sender_id)
            yield event.plain_result("[system] 重置失败：user_id 不能为空。")
            return

        if user_id not in self.love_levels:
            logger.error("管理员 %s 重置好感度失败：用户 %s 不在玩家名单/好感度表中", sender_id, user_id)
            yield event.plain_result(f"[system] 重置失败：用户 {user_id} 不在玩家名单中。")
            return

        old_level = self.love_levels[user_id]
        self.love_levels[user_id] = 0
        logger.info("管理员 %s 重置好感度成功：%s 的好感度 %d -> 0", sender_id, user_id, old_level)
        yield event.plain_result(f"[system] 管理员 {sender_id} 重置成功：玩家 {user_id} 的好感度已重置为 0。")

    @admin.group("player")
    def admin_player(self):
        """管理员：玩家管理"""
        pass

    @admin_player.command("add")
    async def admin_add_player(self, event: AstrMessageEvent, user_id: str):
        """管理员新增玩家（加入玩家名单并初始化好感度为 0）"""
        sender_id = event.get_sender_id()

        if sender_id not in self.admins:
            logger.warn("QQ号 %s 访问管理员接口 admin.player.add 失败：权限不足", sender_id)
            yield event.plain_result(f"[system] 您（{sender_id}）不是管理员，无权限新增玩家。")
            return

        if user_id is None:
            logger.error("管理员 %s 新增玩家失败：user_id 参数为空(None)", sender_id)
            yield event.plain_result("[system] 新增失败：user_id 不能为空。")
            return

        user_id = str(user_id).strip()
        if user_id == "":
            logger.error("管理员 %s 新增玩家失败：user_id 参数为空字符串", sender_id)
            yield event.plain_result("[system] 新增失败：user_id 不能为空。")
            return

        if user_id in self.players:
            logger.error("管理员 %s 新增玩家失败：%s 已在玩家名单中", sender_id, user_id)
            yield event.plain_result(f"[system] 新增失败：{user_id} 已在玩家名单中。")
            return

        self.players.append(user_id)
        # 如果 love_levels 里已经有残留值，这里统一覆盖为 0（更符合“新增玩家”初始化）
        self.love_levels[user_id] = 0

        logger.info("管理员 %s 新增玩家成功：%s 已加入玩家名单，好感度初始化为 0", sender_id, user_id)
        yield event.plain_result(f"[system] 管理员 {sender_id} 新增玩家成功：{user_id} 已加入游戏，好感度初始化为 0。")

    @admin_player.command("kick")
    async def admin_kick_player(self, event: AstrMessageEvent, user_id: str):
        """管理员踢出玩家（从玩家名单移除，并删除其好感度记录）"""
        sender_id = event.get_sender_id()

        if sender_id not in self.admins:
            logger.warn("QQ号 %s 访问管理员接口 admin.player.kick 失败：权限不足", sender_id)
            yield event.plain_result(f"[system] 您（{sender_id}）不是管理员，无权限踢出玩家。")
            return

        if user_id is None:
            logger.error("管理员 %s 踢出玩家失败：user_id 参数为空(None)", sender_id)
            yield event.plain_result("[system] 踢出失败：user_id 不能为空。")
            return

        user_id = str(user_id).strip()
        if user_id == "":
            logger.error("管理员 %s 踢出玩家失败：user_id 参数为空字符串", sender_id)
            yield event.plain_result("[system] 踢出失败：user_id 不能为空。")
            return

        existed_in_players = user_id in self.players
        existed_in_love = user_id in self.love_levels

        if not existed_in_players and not existed_in_love:
            logger.error("管理员 %s 踢出玩家失败：%s 不在玩家名单且无好感度记录", sender_id, user_id)
            yield event.plain_result(f"[system] 踢出失败：{user_id} 不在玩家名单中。")
            return

        if existed_in_players:
            self.players.remove(user_id)

        old_level = None
        if existed_in_love:
            old_level = self.love_levels[user_id]
            del self.love_levels[user_id]

        logger.info(
            "管理员 %s 踢出玩家成功：%s removed_from_players=%s removed_love=%s old_love=%s",
            sender_id,
            user_id,
            existed_in_players,
            existed_in_love,
            str(old_level),
        )
        yield event.plain_result(f"[system] 管理员 {sender_id} 踢出成功：玩家 {user_id} 已被移出游戏。")

    @filter.command("search_love_level")
    async def search_love_level(self, event: AstrMessageEvent, user_id: str = "N"):
        """查询玩家的好感度"""
        if user_id == "N":
            user_id = event.get_sender_id()

        if user_id is None:
            logger.error("查询好感度失败：user_id 参数为空(None)")
            yield event.plain_result("[system] 错误：user_id 不能为空。")
            return

        user_id = str(user_id).strip()
        if user_id == "":
            logger.error("查询好感度失败：user_id 参数为空字符串")
            yield event.plain_result("[system] 错误：user_id 不能为空。")
            return

        if user_id not in self.love_levels:
            logger.error("要查询的用户 %s 不在玩家名单中", user_id)
            yield event.plain_result(f"[system] 错误：要查询的用户 {user_id} 不在玩家名单中。")
            return

        result = self.love_levels[user_id]
        logger.info("查询了 %s 的好感度为 %d", user_id, result)
        yield event.plain_result(f"[system] 查询成功：玩家 {user_id} 的好感度为 {result}")

    @filter.command("join")
    async def join_game(self, event: AstrMessageEvent):
        """新玩家加入游戏"""
        user_id = event.get_sender_id()

        if user_id in self.players:
            logger.error("%s 加入失败：已在玩家名单中", user_id)
            yield event.plain_result(f"[system] 加入失败：{user_id} 已在玩家名单中。")
            return

        self.players.append(user_id)
        self.love_levels[user_id] = 0
        logger.info("玩家 %s 成功加入游戏。", user_id)
        yield event.plain_result(
            f"[system] 加入游戏成功：玩家 {user_id} 的初始好感度设置为 ：0。\r 来和零奈聊天，触发事件增加好感度吧！"
        )

    @filter.command("quit")
    async def quit_game(self, event: AstrMessageEvent):
        """玩家退出游戏（仅玩家本人可用）"""
        user_id = event.get_sender_id()

        existed_in_players = user_id in self.players
        existed_in_love = user_id in self.love_levels

        if not existed_in_players and not existed_in_love:
            logger.error("%s 退出失败：不在玩家名单且无好感度记录", user_id)
            yield event.plain_result(f"[system] 退出失败：{user_id} 不在玩家名单中。")
            return

        if existed_in_players:
            self.players.remove(user_id)

        old_level = None
        if existed_in_love:
            old_level = self.love_levels[user_id]
            del self.love_levels[user_id]

        logger.info(
            "玩家 %s 成功退出游戏：removed_from_players=%s removed_love=%s old_love=%s",
            user_id,
            existed_in_players,
            existed_in_love,
            str(old_level),
        )
        yield event.plain_result(f"[system] 退出游戏成功：玩家 {user_id} 已退出游戏。")



    @filter.on_llm_request()
    async def inject_lovelevel(self,event:AstrMessageEvent,req: ProviderRequest):
        """将玩家的好感度注入到prompt中"""
        sender_id = event.get_sender_id()
        if sender_id not in self.love_levels:
            logger.error(f"玩家 {sender_id} 未加入游戏中，无法与零奈对话。")
            message = MessageChain()
            message.message(f"[system] 玩家 {sender_id} 未加入游戏中，无法与零奈对话。可以发送/join来加入游戏。")
            await event.send(message)
            event.stop_event()
            return
        lovelevel = self.love_levels[sender_id]
        prompt_add = f"\n【注意】当前和你对话的人的好感度为：{lovelevel}\n"
        req.system_prompt += prompt_add

    @filter.llm_tool(name="add_love_level")  # 如果 name 不填，将使用函数名
    async def add_love_level(self, event: AstrMessageEvent, user_id: str) -> MessageEventResult:
        '''加好感度的tool，提供给AI调用

        Args:
            user_id(string): 要加好感度的用户QQ号
        '''
        if user_id not in self.love_levels:
            logger.error(f"要加好感度的用户 {user_id} 不在游戏名单中")
            message = event.make_result()
            message.at(user_id,user_id)
            message.message(f"[system] 要加好感度的用户 {user_id} 不在游戏名单中！")
            yield message
            return
        elif self.love_levels[user_id] == 5:
            logger.error(f"用户 {user_id} 好感度已满（5），无法再增加")
            message = event.make_result()
            message.at(user_id,user_id)
            message.message(f"[system] 用户好感度已满（5），无法再增加！")
            yield message
            return
        self.love_levels[user_id] += 1
        logger.info(f"用户 {user_id} 好感度 + 1，当前好感度为 {self.love_levels[user_id]}")
        message_chain = MessageChain().at(user_id,user_id).message(f"[system]好感度 + 1，当前好感度为 {self.love_levels[user_id]}")
        await self.context.send_message(event.unified_msg_origin, message_chain)
        # message = event.make_result()
        # message.at(user_id, user_id)
        # message.message(f"[system] 好感度 + 1，当前好感度为 {self.love_levels[user_id]}")
        # test = MessageChain()
        # test.message("111")
        # await event.send(test)
        # yield message


