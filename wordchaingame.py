
# -*- coding: utf-8 -*-
# meta developer: @YourUsername
# meta banner: https://example.com/banner.jpg

from telethon import events
from .. import loader, utils

class WordChainGameMod(loader.Module):
    """Модуль для игры 'Словесная цепочка'"""
    strings = {"name": "WordChainGame"}

    def __init__(self):
        self.active_games = {}
        self.words_used = set()

    async def client_ready(self, client, db):
        self.client = client

    async def startchaincmd(self, message):
        """Начать игру 'Словесная цепочка'"""
        chat_id = utils.get_chat_id(message)
        if chat_id in self.active_games:
            await message.edit("Игра уже идет!")
            return

        self.active_games[chat_id] = {
            "last_word": None,
            "players": {}
        }
        self.words_used.clear()
        await message.edit(
            "🎮 Игра 'Словесная цепочка' началась!\n\nПервый игрок, напишите любое слово!"
        )

    @loader.unrestricted
    async def watcher(self, message):
        chat_id = utils.get_chat_id(message)
        if chat_id not in self.active_games:
            return

        game = self.active_games[chat_id]
        text = message.text.strip().lower()

        if game["last_word"]:
            last_letter = game["last_word"][-1]
            if text[0] != last_letter:
                await message.respond(f"❌ Слово должно начинаться на букву '{last_letter.upper()}'!")
                return

        if text in self.words_used:
            await message.respond("❌ Это слово уже использовалось!")
            return

        self.words_used.add(text)
        game["last_word"] = text
        user_id = message.sender_id
        game["players"][user_id] = game["players"].get(user_id, 0) + 1

        await message.respond(
            f"✅ {text.capitalize()} принято! Ваш ход записан.\n\nСледующий игрок должен придумать слово на букву '{text[-1].upper()}'."
        )

    async def stopchaincmd(self, message):
        """Остановить игру 'Словесная цепочка'"""
        chat_id = utils.get_chat_id(message)
        if chat_id not in self.active_games:
            await message.edit("Игра не запущена!")
            return

        game = self.active_games.pop(chat_id)
        results = "\n".join(
            [
                f"{(await self.client.get_entity(uid)).first_name}: {score} слов"
                for uid, score in game["players"].items()
            ]
        )
        await message.edit(f"Игра завершена! Итоги:\n\n{results}")
