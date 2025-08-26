# Bot Hunter - Telegram Userbot

A userbot running on Telethon with stealth features like hidden master IDs, group management commands, and hidden eval.

##  Quick Setup

1. Fork this repository.
2. Rename `.env.sample` to `.env`, then fill in your values.
3. Deploy with one click:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/PRO-18/bot_hunter)

Once deployed, your app will start automatically as a Heroku worker.

---

##  Local Run

```bash
git clone https://github.com/PRO-18/bot_hunter.git
cd bot_hunter
cp .env.sample .env
# Fill your credentials
pip install -r requirements.txt
python3 main.py
