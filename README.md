---
title: PopCorn Mirror Bot
emoji: 🍿
colorFrom: yellow
colorTo: red
sdk: docker
pinned: false
---

# 🍿 PopCorn Mirror Leech Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/PopCornTelegramApp/mirror-leech-telegram-bot&envs=BOT_TOKEN,TELEGRAM_API,TELEGRAM_HASH,OWNER_ID,TMDB_API_KEY,LEECH_DUMP_CHAT,POPCORN_CHANNEL_ID,POPCORN_POST_TO_CHANNEL&BOT_TOKENDesc=Telegram+Bot+Token&TELEGRAM_APIDesc=Telegram+API+ID+from+my.telegram.org&TELEGRAM_HASHDesc=Telegram+API+Hash&OWNER_IDDesc=Your+Telegram+User+ID&TMDB_API_KEYDesc=TMDB+API+Key&LEECH_DUMP_CHATDesc=Channel+ID+to+dump+files&POPCORN_CHANNEL_IDDesc=PopCorn+Private+Channel+ID&POPCORN_POST_TO_CHANNELDesc=Post+to+channel+after+upload)

بوت تيليغرام متكامل لتحميل الملفات ورفعها إلى قناتك الخاصة مع معلومات TMDB.

## المميزات
- 📥 تحميل من تورنت، روابط مباشرة، Google Drive، yt-dlp وغيرها
- 🎬 جلب معلومات الفيلم/المسلسل تلقائياً من TMDB
- 📢 نشر تلقائي في قناة PopCorn الخاصة مع البوستر والمعلومات
- 🌐 دعم العربية والإنجليزية

## المتغيرات البيئية المطلوبة

| المتغير | الوصف |
|---------|-------|
| `BOT_TOKEN` | رمز بوت تيليغرام |
| `TELEGRAM_API` | API ID من my.telegram.org |
| `TELEGRAM_HASH` | API Hash من my.telegram.org |
| `OWNER_ID` | معرّف حسابك على تيليغرام |
| `TMDB_API_KEY` | مفتاح TMDB API |
| `LEECH_DUMP_CHAT` | معرّف القناة لرفع الملفات |
| `POPCORN_CHANNEL_ID` | معرّف قناة PopCorn الخاصة |
| `POPCORN_POST_TO_CHANNEL` | `True` للنشر التلقائي |
