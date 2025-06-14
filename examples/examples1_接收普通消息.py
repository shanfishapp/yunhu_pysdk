import asyncio
from yunhu_pysdk import BOT, sdk
from yunhu_pysdk.logger import logger


async def deliver(data):
    sender = data.get("event", {}).get("sender", {})
    message = data.get("event", {}).get("message", {})

    recv_id = sender.get("senderId")
    recv_type = sender.get("senderType")
    text_content = message.get("content", {}).get("text", "").strip()

    if message.get("contentType") != "text":
        return

    logger.info(f"收到消息: {text_content}")

    if text_content == "ping":
        await bot.send.text(recv_id, recv_type, "pong")
    else:
        await bot.send.text(recv_id, recv_type, "收到你的消息啦！")


async def main():
    # 初始化 SDK Token，请替换为你自己的 token
    sdk.init("2439e944a5434716b6d4056c7029a0ab")

    # 创建机器人实例
    global bot
    bot = BOT(host="0.0.0.0", port=5888)
    bot.add(deliver)

    # 启动服务
    await bot.start()

    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())