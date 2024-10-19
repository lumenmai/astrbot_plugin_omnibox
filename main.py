import os
import random
import datetime
import asyncio
from util.log import LogManager
from logging import Logger
from util.plugin_dev.api.v1.types import Image, Plain, At, Poke

flag_not_support = False
try:
    from util.plugin_dev.api.v1.bot import Context, AstrMessageEvent, CommandResult
    from util.plugin_dev.api.v1.config import *
except ImportError:
    flag_not_support = True
    print("导入接口失败。请升级到 AstrBot 最新版本。")

logger: Logger = LogManager.GetLogger(log_name='astrbot')

class OmniboxPlugin:
    """
    AstrBot 会传递 context 给插件。
    
    - context.register_commands: 注册指令
    - context.register_task: 注册任务
    - context.message_handler: 消息处理器(平台类插件用)
    """
    def __init__(self, context: Context) -> None:
        self.context = context
        self.groups = self.load_groups()
        self.context.register_commands("Omnibox", "占卜", "发送占卜图片", 1, self.divination, False, True)
        self.context.register_commands("Omnibox", "签到", "每日签到", 1, self.checkin, False, True)
        self.context.register_task(self.daily_task(8, 0, "早上好喵~莲已经起床了喵~"), "早安")
        self.context.register_task(self.daily_task(23, 0, "大家晚安喵~"), "晚安")


    """
    指令处理函数。
    
    - 需要接收两个参数：message: AstrMessageEvent, context: Context
    - 返回 CommandResult 对象
    """
    def divination(self, message: AstrMessageEvent, context: Context):
        image = self.get_random_image("divination_pic")
        user_id = message.message_obj.sender.user_id
        if image:
            return CommandResult(
                message_chain=[
                    At(qq=user_id),
                    image
                ],
            )
        return CommandResult().message("我的脑子空空的，没有办法占卜啦！")

    def get_random_image(self, folder):
        """ 从文件夹随机选择一张图片"""
        current_dir = os.path.dirname(__file__)
        pic_dir = os.path.join(current_dir, folder)
        # 获取所有jpg和png文件
        images = [f for f in os.listdir(pic_dir) if f.lower().endswith(('.jpg', '.png'))]
        if images:
            random_image = random.choice(images)
            image_path = os.path.join(pic_dir, random_image)
            return Image.fromFileSystem(image_path)
        else:
            logger.warning("没有找到图片。")
            return None

    def load_groups(self):
        current_dir = os.path.dirname(__file__)
        json_path = os.path.join(current_dir, "group.json")
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                return data.get("groups", [])
        except Exception as e:
            logger.error(f"加载 group.json 失败: {str(e)}")
            return []

    async def daily_task(self, hour, minute, message):
        while True:
            now = datetime.datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if now >= target_time:
                target_time += datetime.timedelta(days=1)
            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            await self.send_message(message)
            await asyncio.sleep(60)

    async def send_message(self, message):
        command_result = CommandResult().message(message)
        for platform in self.context.platforms:
            if platform.platform_name == "aiocqhttp":
                for group_id in self.groups:
                    try:
                        target = {"group_id": int(group_id)}
                        await platform.platform_instance.send_msg(target, command_result)
                        logger.info(f"发送消息到群 {group_id}: {message}")
                    except Exception as e:
                        logger.error(f"发送消息到群 {group_id} 失败: {str(e)}")

    def checkin(self, message: AstrMessageEvent, context: Context):
        image = self.get_random_image("checkin_pic")
        user_id = message.message_obj.sender.user_id
        return CommandResult(
            message_chain=[
                At(qq=user_id),
                image,
                Plain("哼！我才不会给你签到喵！")
            ],
        )