import {
  TelegramBot,
  UpdateType,
} from "https://deno.land/x/telegram_bot_api/mod.ts";

const TOKEN = Deno.env.get("TELEGRAM_TOKEN");
if (!TOKEN) throw new Error("No token provided");
const bot = new TelegramBot(TOKEN);

const regex = /tiktok\.com\/[-A-Za-z0-9+/=]+/;
bot.on(UpdateType.Message, async ({ message }) => {
  var link = "";
  message.entities?.forEach((entity) => {
    if (entity.type === "url") {
      link = message.text?.substr(entity.offset, entity.length) ?? "";
    }
  });
  if (regex.test(link)) {
    if (link.includes("m.tiktok")) {
      await fetch(link, {
        redirect: "follow",
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        },
      }).then(
        (response) => {
          if (response.status === 200) {
            link = response.url.split("?")[0];
          } else {
            bot.sendMessage({
              chat_id: message.chat.id,
              text:
                'Sorry could not convert url at this time, please use "www.tiktok.com/@<user>/video/<video id>"',
            });
          }
        },
      ).catch((e) => console.error(e));
    }
    const response = fetch("https://tik.fail/api/geturl", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `url=${link}`,
    });
    response.then((response) => {
      response.json().then((out) => {
        if (out.direct) {
          bot.sendVideo({
            chat_id: message.chat.id,
            video: out.direct,
          }).catch((e) => {
            bot.sendMessage({
              chat_id: message.chat.id,
              text: `Sending as video failed, here is a link ${out.webpage}`,
            });
          });
        }
      }).catch((e) => console.log(e));
    }).catch((e) => console.error(e));
  }
});

bot.run({
  polling: true,
});
