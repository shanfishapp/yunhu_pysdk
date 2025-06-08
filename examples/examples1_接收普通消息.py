from yunhu_pysdk import BOT, sdk
sdk.init("你的机器人token")# 替换为你自己的token
bot = BOT()
# 在此段代码中，发送消息将返回"收到你的消息啦！"。当发送"ping"时，将同时返回"pong"
def deliver(data):
    if data.event == "message.receive.normal"：
        bot.send.text(data.id, data.type, "收到你的消息了啦！")
        if data.msg == "ping":
            bot.send.text(data.id, data.type, "pong")

if __name__ == "__main__":
    bot.add(deliver)
    bot.start()