import os
import random
from util.log import LogManager
from logging import Logger

flag_not_support = False
try:
    from util.plugin_dev.api.v1.bot import Context, AstrMessageEvent, CommandResult
    from util.plugin_dev.api.v1.config import *
except ImportError:
    flag_not_support = True
    print("导入接口失败。请升级到 AstrBot 最新版本。")

logger: Logger = LogManager.GetLogger(log_name='astrbot')

class DivinationPlugin:
    """
    AstrBot 会传递 context 给插件。
    
    - context.register_commands: 注册指令
    - context.register_task: 注册任务
    - context.message_handler: 消息处理器(平台类插件用)
    """
    def __init__(self, context: Context) -> None:
        self.context = context
        self.context.register_commands("divination", "占卜", "内置测试指令。", 1, self.divination, False, True)

    """
    指令处理函数。
    
    - 需要接收两个参数：message: AstrMessageEvent, context: Context
    - 返回 CommandResult 对象
    """
    def divination(self, message: AstrMessageEvent, context: Context):
        image = self.get_random_image()
        if not image:
            return CommandResult().message("我的脑子空空的，没有办法占卜啦！")
        return CommandResult().file_image(image)
    
    def get_random_image(self):
        current_dir = os.path.dirname(__file__)
        pic_dir = os.path.join(current_dir, "pic")
        # 获取所有jpg和png文件
        images = [f for f in os.listdir(pic_dir) if f.lower().endswith(('.jpg', '.png'))]
        if images:
            random_image = random.choice(images)  # 随机选择一张
            return os.path.join(pic_dir, random_image)
        else:
            logger.warning("没有找到图片。")
            return None
