# $*$ =============================================================================== $*$
"""
             This is a Telegram I mess around with while im working or mucking about
"""
# $*$ =============================================================================== $*$
# -*- coding: UTF-8 -*-

# import the Main APIS the Bot will use
from pycoingecko import CoinGeckoAPI # PyCoinGecko to access CoinGecko
from twelvedata import TDClient # For Public companies ticke symbols
# from yahoofinancials import YahooFinancials  # to make correspondinf web dashboard

# To build the bot, we gonna use Telegram Http BotAPI
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,            # For commands user type in prompt to bot
    CallbackQueryHandler,      # When the bot doesn't need to context of the user, but must query
    CallbackContext,           # When it does need the context of the user
    MessageHandler,            # Handler for response to queries used by bot
    ConversationHandler,       # This will handle the sentiment given to bot by user
    Filters,

)

from typing import Dict
import  requests # For local file system http hamdling
import sys # AS above. . .
import os, os.path   # Have access to filepath

import datetime as dt # Date time sequence for timestamps
import requests  # For HTTP handling and requests
import logging  # To init logger for troublshooting
import time  # To stop and slow things down for better user intrepreter

import pandas as pd
import pyfiglet   # So terminal looks pretty for troubleshooters
from colorama import Fore, Back, Style  # For different color for terminal and logger out
from config import TELEGRAM_TOKEN

import numpy as np
import pandas as pd
import nltk
import re

import json
from typing import NamedTuple

import hashlib
from urllib.parse import urlparse
from flask import Flask, jsonify, request # To work with Postman API maker thingy

# * ------------------------------------------------ * #
#                 Imports for NFT-Minter
# * ------------------------------------------------ * #
from PIL import Image
from IPython.display import display
import random
import json
import os
# * ------------------------------------------------ * #

# *** ========================================================== *** #
# Logger
# Enable logging
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

logger = logging.getLogger(__name__)
# $*$ ------------------------------------------------------------ $*$
""" Class to handle http calls for file in local system, this will work
    work with bot.send_document
"""
# $*$ ------------------------------------------------------------ $* #
# *** ========================================================== *** #

# +++ -------------------------------------------------------------------------- +++ #
#                        AUTOMATED TELEGRAM HTTP BOT Replies. . .
# +++ -------------------------------------------------------------------------- +++ #

USAGE = f"""<strong>🔥FireCrypt-Bot! Menu:</strong>

🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰

1). /coin <strong>[cryptocurrency]</strong>
2). /ticker <strong>[ticker-symbol]</strong>
3). /sentiment <strong>[your-sentiment]</strong>
4). /riddle <strong>[riddle-from-sean]</strong>
5). /nft_builder <strong>[mint-nft]</strong>
6). /fireton_status
7). /secrets
8). /help <strong>[help-4-navigation]</strong>

🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n
"""

# Make our bot repsonse use our littler tokenize interpreter & primative complier
USAGE_CryPto = f"<strong>DiGalactic TradeBot💸👨🏻‍🚀</strong> \n\n"
f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n\n"

f"<strong></strong> \n\n"
f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n\n"

# Define WEb App outside of Telegram API, yet we must still open the web app
# using a Telegram Bot Command or Method as defined by their numerous APIs

# ** ============================================================================ ** #
# Our Token Class
class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int
# ** ============================================================================ ** #

def tokenize_forBot(code):

    # ---------------------------- #
    """
    :param code: The code written to parse raw responses
                 from Coin GeckoAPI(). We specify certain patterns
                 to parse from JSON API() response from our requests
                 which is defined by the user giving updated
                 contextual commands

    :return: Identify certain character from response
             to CoinGecko, we do this tokenization so
             that we may return a neat parsed reply
             from our Trade Bot
    """
    # ---------------------------- #

    # Our keywords and characters to look out for...
    keys_and_chars = {
        # For SA ZAR
        'zar', 'zar_24h_change'
    }

    # Our token specification for FIAT/Crypto Callback pAsre
    token_specifications = [

        ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
        ('ASSIGN',   r':='),           # Assignment operator
        ('END',      r';'),            # Statement terminator
        ('ID',       r'[A-Za-z]+'),    # Identifiers
        ('OP',       r'[+\-*/]'),      # Arithmetic operators
        ('NEWLINE',  r'\n'),           # Line endings
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character

    ]

    # Our tokenomics and Regeneration of FIAT/CRYPTO CALLBACK
    token_regex = "".join('(?P<%s>%s)' %
            pair for pair in token_specifications
    )

    # In case the tokenizer needs to make new lines
    line_num = 1
    line_start = 0

    for class_tokenIter in re.finditer(token_regex, code):

        kind = class_tokenIter.lastgroup
        value = class_tokenIter.group()
        column_move2NewLine = class_tokenIter.start() - line_start

        if kind == "NUMBER":
            value = float(value) if '.' in value \
                else int(value)

        elif kind == "ID" and value in keys_and_chars:
            kind = value

        elif kind == "NEWLINE":
            line_start = class_tokenIter.end()
            line_start += 1     # Append new line to chat prompt

        elif kind == "SKIP":
            continue

        elif kind == "MISMATCH":

            raise RuntimeError(
                f'{value!r} unexpected on line'
                f' {line_num}'
            )

# Our in chat-prompt navigation button for photo() function
reply_keyboard = [[
    "Download via Internet", "Download via Intranet"
]]

# ** ============================================================================ ** #
#                          END of BOT TOKENizer and Intrepreter
# ** ============================================================================ ** #
def facts_to_str(user_data: Dict[str, str]) -> str:

    # * ------------------------------------------- * #
    """
    Formatter function for formatting the gathered use info

    :param user_data:
    :return:
    """
    # * ------------------------------------------- * #
    facts = [f"{key} - {value}"
             for key, value in user_data.items()]

    return  "\n".join(facts).join(["\n", "\n"])

def start(update, context):

    # * ------------------------------------------ * #
    """
     :param update:   Start the bot, update it's life!
     :param context:  This is the initialzer and first bot instance
     :return:         First init to start bot
    """
    # * ------------------------------------------ * #

    # My OWN Logs
    header_for_logger = pyfiglet.figlet_format("Bot Started...")
    footer_for_logger = pyfiglet.figlet_format("Called Starter Function")
    print(Fore.BLUE + "# * ================================================ * #")
    print(Fore.RED + header_for_logger)
    print(Fore.YELLOW + footer_for_logger)
    print(Fore.BLUE + "# * ================================================ * #")

    # MAke it so that the user can expect reply from bot
    # Make it show "typing..." before sending reply to user
    context.bot.send_chat_action(

        chat_id = get_chat_id(
            update,
                context
        ),

        action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
            timeout = 1
        )

    time.sleep(1)

    update.message.reply_text(

             "<strong>🔥FireCrypt-Bot 🌐</strong> \n\n"

            "Welcome❕ to the <strong>🔥FireCrypt-Bot</strong> \n\n"
            "Where can I take your mind today? 💭 \n\n"
            "Please type in the command /menu to get started 👀 \n\n"

            "<strong>🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 </strong> \n\n"
            "<i>Developed by</i>\n" \
            "<strong>SeanCode👽</strong> \n\n",

                 parse_mode = "html"
        )

# ** ============================================================================ ** #
def get_chat_id(update, context):

    # * ------------------------------------------ * #
    """
    :param update:
    :param context:
    :return:
    """
    # * ------------------------------------------ * #
    chat_id = -1

    if update.message is not None:
        # text message
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        # callnacbk message
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        # Answer in PoLL
        chat_id = context.bot_data[update.poll.id]

    return chat_id

# ** ============================================================================ ** #
""" Make an Pretty triangle, lets see what it looks like """
# ** ============================================================================ ** #
def math_secrets(update, context):

    # * -------------------------------------- * #
    """
    :param update:
    :param context:
    :return:
    """
    # * -------------------------------------- * #

    context.bot.send_chat_action(

        chat_id = get_chat_id(
            update,
            context
        ),

        action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
        timeout = 1
    )

    time.sleep(1)

    update.message.reply_text(
        f"<strong>🔥Firecoin! Bot Menu</strong> \n\n"
        f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n\n"
        f"This part is an educational instance of 🔥<strong>FireCrypt-Bot!</strong>\n"
        f"What would you like to read about?\n\n"
        f"1). Elliptical Curve Cryptography \n"
        f"2). Blockchain Technology \n"
        f"3). SeanCode👽 M-Calculus \n"
        f"4). <strong>🔥Firecoin!</strong> Whitepapers \n\n"
        f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n",

            parse_mode = "html"
    )


def botReturn_contxt(update, context):

    # * ------------------------------------------ * #
    """
    :param update:   Take Bot out of idle
    :param context:  When the user uses the 'secrets_nav'
                     from EduMenu
    :return:         Manipulate above function, and return
                     navgavitional option for user....
    """
    # * ------------------------------------------ * #


def encryption(my_string, step):

    # * ------------------------------------------ * #
    """

        This will encrypt a raunchy message for a Lady
        She has to figure the step character, through a
        Riddle...

    :param string:   Our String we wanna encrypt
    :param step:     How we step each charcter encrypt message
    :return:         Will return a Caesar Cipher, in a Riddled Context
    """
    # * ------------------------------------------ * #

    output = ""    # Garbage Collection to store encryted Message

    # Every alphabetical character has a value in secret message
    for char in my_string:
        output += chr(
                ord(char) - step
    )

    return output # Change numeric context of character

# * ----------------------------------------------------------------- * #
def decryption(my_string, step):

    # * -------------------------------------- * #
    """

           Decrypted encrypted message using riddled contextual
           shift of character's numeric value

    :param string:   The Encrypted Messages from above function
    :param step:     Our Decryption Key
    :return:         Decrypted Message and return
    """
    # * -------------------------------------- * #

    # Same kak as above, but only in reverse
    output = ""

    for char in my_string:
        output += chr(ord(
                char) + step
    )

    return output # Use shifted numeric value to decrypt

# * ----------------------------------------------------------------- * #
def riddle_cipher(update, context):

    # * --------------------------------- * #
    """
    :param update:  When the user types in '/', it gives
                    context and updated from idle
    :param context: The command we command the user to type
                    to the, to recieve a command

    :return:        Return 'Riddling Caesar Cipher' to Bot.
    """
    # * --------------------------------- * #

    # toDO --> Put funny "Riddled" Caesar Chiper, so I ca use it with
    #          Lekka BoT Blocknet

    # * --------------------------------- * #

    # What will fill function's argument 'my_string'...
    botcoin_string = "Welcome to Botcoin! " \
                     "I am an Artificially Intelligent Memecoin Cryptocurrency." \
                     "I am just a memecoin which hases an SHA-256 SECP-K1 Algorithm." \
                     "It is the same Ellipical Curve which Bitcoin, only implemented" \
                     "with the Python Programming Language instead of C++  " \


    my_other_string = \
    "'Layla' by Eric Clapton. \n" \
    "\n" \
    "What'll you do when you get lonely \n" \
    "And nobody's waiting by your side? \n" \
    "You've been running and hiding much too long \n" \
    "You know it's just your foolish pride \n" \
    "\n" \
    "Layla, you've got me on my knees \n" \
    "Layla, I'm begging, darling please \n" \
    "Layla, darling won't you ease my worried mind \n" \
    "\n" \
    "I tried to give you consolation \n" \
    "When your old man had let you down \n" \
    "Like a fool, I fell in love with you \n" \
    "Turned my whole world upside down \n" \
    "\n" \
    "Layla, you've got me on my knees \n" \
    "Layla, I'm begging, darling please \n" \
    "Layla, darling won't you ease my worried mind \n" \

    "Let's make the best of the situation \n" \
    "Before I finally go insane \n" \
    "Please don't say I'll never find a way \n" \
    "And tell me all my love's in vain \n" \
    "\n" \
    "Layla, you've got me on my knees \n" \
    "Layla, I'm begging, darling please \n" \
    "Layla, darling won't you ease my worried mind \n " \
    "\n" \
    "Layla, you've got me on my knees \n" \
    "Layla, I'm begging, darling please \n" \
    "Layla, darling won't you ease my worried mind \n" \

    step = 9
    encrypted = encryption(botcoin_string, step)
    decrypted = decryption(encrypted, step)

    while True:

        # MAke it so that the user can expect reply from bot
        # Make it show "typing..." before sending reply to user
        context.bot.send_chat_action(

            chat_id = get_chat_id(
                update,
                context
            ),

            action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
            timeout = 1
        )

        time.sleep(1)

        update.message.reply_text(

            f" <strong>The Riddler 🎩</strong> \n\n"
            f"💎 🎩 🔐 🎲 🔐 🎩 💎 \n\n"

            f"The Numerically Shifted Character to decrypt this message "
            f"is a number which<strong> Whips the Fibonacci❕🌀</strong>. \n\n"
            f"It grounds it down, and jumps to Three. . ."
            f"<strong>Whatever could this number be❔</strong> \n\n"
            f"Thus the number is Riddled Cryptographic Consensus. "
            f"<strong> What will decrypt the Secret Message?</strong> \n\n"
            f"Developed by <strong>SeanCode👽</strong> \n\n"
            f"💎 🎩 🔐 🎲 🔐 🎩 💎 \n\n",

                parse_mode = "html"
            )

        time.sleep(4)

        context.bot.send_chat_action(

            chat_id = get_chat_id(
                update,
                context
            ),

            action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
            timeout = 1
        )


        update.message.reply_text(
            f" \n  Encrypted Message: \n"
            f" \n {encrypted} \n"
        )

        # Now get the bot to ask user for Key
        time.sleep(4)

        update.message.reply_text(

            f"<strong>The Riddler 🎩 </strong> \n\n "
            f"💎 🎩 🔑 🎲 🔑 🎩 💎 \n\n"
            f"Figure out what number is the secret key \n\n"
            f"<strong>And see what will be...</strong> \n\n"
            f"Type in the command /riddler, followed by the number you think"
            f" will crack the code... \n\n"
            f"💎 🎩 🔑 🎲 🔑 🎩 💎 \n\n",

                parse_mode = "html"
        )

        time.sleep(4)

        context.bot.send_chat_action(

            chat_id = get_chat_id(
                update,
                context
            ),

            action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
            timeout = 1
        )

        break
# * ----------------------------------------------------------------------------- * #
def unlock(update, context):

    # * ---------------------------------------- * #
    """
    :param update:
    :param context:
    :return:
    """
    # * ---------------------------------------- * #

    # The Message I encryted with a simple Caesar Cipher...

    botcoin_string = "Welcome to <strong>Botcoin!</strong> " \
                     "I am an Artificially Intelligent Memecoin Cryptocurrency. " \
                     "I am a memecoin which hases an <strong>SHA-256 SECP-K1 Algorithm</strong>. " \
                     "It is the same Ellipical Curve which <strong>Bitcoin</strong> uses, only implemented " \
                     "with the <strong>Python</strong> Programming Language instead of <strong>C++</strong>. " \
                     "\n\n" \


    # Called our so-called "Riddle" Encryption Signature in
    step = 5    # A simple Caesar Cipher using the codex order of 5 as Shifting Key..
    encrypted = encryption(botcoin_string, step)
    decrypted = decryption(encrypted, step)

    while True:

        # MAke it so that the user can expect reply from bot
        # Make it show "typing..." before sending reply to user
        context.bot.send_chat_action(

            chat_id = get_chat_id(
                update,
                context
            ),

            action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
            timeout = 1
        )

        time.sleep(1)

        update.message.reply_text(
            f"<strong>The Riddler 🎩 </strong> \n\n "
            f"💎 🎩 🎸 🎲 🎸 🎩 💎 \n\n"
            f"{decrypted} \n\n"
            f"💎 🎩 🎸 🎲 🎸 🎩 💎 \n\n",

                parse_mode = "html"
        )

        break

# * ----------------------------------------------------------------------------- * #
def continue_riddle(update, context):

    # * ---------------------------------------- * #
    """
    :param update:
    :param context:
    :return:
    """
    # * ---------------------------------------- * #

    botcoin_string = "Welcome to <strong>Botcoin!</strong> " \
                     "An Artificially Intelligent Memecoin Cryptocurrency. " \
                     "A chatbot memecoin which hases an <strong>SHA-256 SECP-K1 Algorithm</strong>. " \
                     "It is the same Ellipical Curve which <strong>Bitcoin</strong> uses, only implemented " \
                     "with <strong>Python</strong> instead of <strong>C++</strong>. 👩🏻‍💻 " \
                     "\n\n" \


    # Called our so-called "Riddle" Encryption Signature in
    step = 9    # A simple Caesar Cipher using the codex order of 5 as Shifting Key..
    encrypted = encryption(botcoin_string, step)
    decrypted = decryption(encrypted, step)

    # toDO --> This must be incorporated into True while loop()...

    if len(context.args) >= 1:

        decrypt_step = context.args[0]

        # Now for our conditional, this is the:
        # guesses the right numbe to decrypted Riddle-Cipher
        if decrypt_step == "9":

            time.sleep(3)

            #tHeURL = "https://drive.google.com/uc?id=1RcAihpRuIvYerUJhV-LwvF-9A2fcsreK&export=download"
            botcoin_pic = "https://drive.google.com/uc?id=1IaRoZVDIxmmXvWaeEb5CHt2zsLGEFhA6&export=download"
            #false_botcoin = "https://drive.google.com/uc?id=1up7kE5QB5aZIF5u4oFO79ww3a57LQBlG&export=download"

            context.bot.send_chat_action(

                chat_id = get_chat_id(
                    update,
                    context
                ),

                action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
                     timeout = 1
            )

            context.bot.send_document(
                chat_id = get_chat_id(
                    update,
                        context
                ),
                    document = botcoin_pic,

                        caption = "<strong>Well done! You cracked the code!</strong>\n\n"
                                  "<strong>Decrypted Message: </strong> \n\n"
                                  "💎  ❕ 📲 ✴ ❕ 📲  💎 \n\n"
                                  f"<strong>{decrypted}</strong> "
                                  f"💎 📲 ❕ ✴ ❕ 📲 💎 ",

                parse_mode = "html"
            )

            context.bot.send_chat_action(

                chat_id = get_chat_id(
                    update,
                    context
                ),

                action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
                timeout = 3
            )

        # If the user chooses the number '6'
        elif decrypt_step == "6":

            time.sleep(3)

            context.bot.send_chat_action(
                 chat_id = get_chat_id(
                    update,
                    context
                ),

                    action = telegram.ChatAction.TYPING,
                    timeout = 4  # Make it longer to give element of surprise
            )

            # Special message for number 6
            update.message.reply_text(
                f"<strong>The Riddler 🎩</strong> \n\n "
                f"💎 🎩 🔑 🎲 🔑 🎩 💎 \n\n"
                f"Now why do you choose that number? \n"
                f"The Number Six, sits right in the middle of things..😤\n\n"
                f"<strong>Don't do that again!</strong> \n\n"
                f"💎 🎩 🔑 🎲 🔑 🎩 💎 ",

                    parse_mode = "html"
            )

        else:

            false_botcoin = "https://drive.google.com/uc?id=1up7kE5QB5aZIF5u4oFO79ww3a57LQBlG&export=download"

            time.sleep(2)

            context.bot.send_chat_action(
                chat_id = get_chat_id(
                    update,
                    context
                ),

                action = telegram.ChatAction.TYPING,
                timeout = 4
            )

            context.bot.send_document(
                chat_id = get_chat_id(
                    update,
                    context
                ),

                        document = false_botcoin,
                    caption = "<strong>Wrong number, Try Command Again!</strong>",

                parse_mode = "html"


            )

# ** ============================================================================ ** #
#                             Firenance! NFT Minter
# ** ============================================================================ ** #
# Each Image is made of a series Traits
# The weightings of each trait drives the rarity of NFT
# ** ============================================================================ ** #
#mask = generate_RandomNumber(0, 20)
#SEED = 123456

def create_MaskDict():

    # * ------------------------------------- * #
    """
    :return:
    """
    # * ------------------------------------- * #

    mask_dict = {
        1: "Balaklava",
        2: "Ninja",
        3: "Doom",
        4: "Doom 2",
        5: "Jason"
    }

    return mask

# * ---------------------------------------------------------------- *
def generate_RandomNumber(lowIn, highIn, sizeIn):

    # * ------------------------------------ * #
    """
    :param lowIn:
    :param highIn:
    :param sizeIn:
    :return:
    """
    # * ------------------------------------ * #
    rng = np.random.default_rng(SEED)

    random_numberArray = rng.integers(
        low = lowIn,
        high = highIn,
        size = sizeIn
    )

    return int(random_numberArray[0])


# ** ============================================================================ ** #
"""
     Here we are gonna add in a Sentiment Classifier, to better understand
     a collective thought behind any subject being reflected in social media.
     However use the Neaural Network to better understand social sentiment
     of human financial systems and what they are doing.. We use NLK for this.
     We will use the Telegram bot to open the web browser

"""
# ** ============================================================================ ** #
def social_sentiment(update, context):

    # * ----------------------------------- * #
    """
    :param update:   What command we define user to use
                     it must now open a web browser. I am stilll your master!
    :param context:  The sentence for sentimental classification
    :return:         Open Sentiment Classifier in Telegram Chat with bot
    """
    # * ---------------------------------- * #

    # So the user sees "Typing...", indicating bot has updated context
    context.bot.send_chat_action(

        chat_id = get_chat_id(
            update,
            context
        ),

        action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
        timeout = 1
    )

    time.sleep(1)     # An illusion of asynchromus sheduling I think (LoL)

    # ------------------------------------------- #
    """
            Handling by a Natural
             Language Processor
    """
    # ------------------------------------------- #

    # Condition to stop/start context
    if len(context.args) == 1:

        score = 0
        print(context.args)

        nltk.download('vader_lexicon')  # AI Engine used. . .
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sid = SentimentIntensityAnalyzer()

        # Import NL Library NLK
        from nltk.tokenize import WordPunctTokenizer
        update.message.reply_text("Tokenizer loaded. . .")

        output = context.args

        # Here we to put out what the user typed in out of a list
        pattern = r"".join(output)

        # Now in order to jugde sentiment, we need to give nltk something
        # to score the user's sentimental search
        score = ((sid.polarity_scores(pattern))["compound"])

        # Return score to Telegram chat with bot
        update.message.reply_text(

            f"<strong>NLTK Sentiment Classification 🦸🏻‍♂️ </strong> \n\n"
            f"<strong>Sentiment Score:</strong>"
            f" <code>{score}</code> \n\n"
            f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n",

                parse_mode = "html"
        )

def menu(update, context):


    # ++ --------------------------------- ++ #
    """
      :param update:    The method and clause to update user command to bot
      :param context:   What the user describes as clause to start it ("/start")
      :return:          This will start the FinAIpp Telegram Bot
    """
    # ++ --------------------------------- ++ #

    # MAke it so that the user can expect reply from bot
    # Make it show "typing..." before sending reply to user
    context.bot.send_chat_action(

        chat_id = get_chat_id(
            update,
            context
        ),

        action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
        timeout = 1
    )

    time.sleep(1)

    # Return USAGe variable when "/menu" is called
    result = pyfiglet.figlet_format("Firecoin!")

    done_by = pyfiglet.figlet_format("Firefly! BotMenu")

    print(Fore.RED + " # * ========================s======================== * #")
    print(Fore.BLUE + result)
    print(Fore.RED + " # * ================================================ * #")
    print("")
    print(Fore.BLUE + done_by)
    print(Fore.RED + " # * ================================================ * #")

    update.message.reply_text(USAGE,
                              parse_mode = "html")

    # if user asks for fiat tickers of compaies listed as securities

# ** ========================================================================== ** #
#                            END of FinAIpp Bot Menu ReplyText
# ** ========================================================================== ** #

def get_shareTicker(update, context):

    # * ---------------------------------------- * #
    """
     :param update:   Empty user bot command
     :param context:  Just tells user what to do. ...
     :return:
    """
    # * ---------------------------------------- * #

    # ----------------------------------------------- #
    # Logs for Admin to see in terminal, and to see
    # what functions are being called from a user
    # ----------------------------------------------- #
    banner_for_logger = pyfiglet.figlet_format("TwelveData API Context..")
    function_call = pyfiglet.figlet_format("Called Security Index Ticker")
    print(Fore.BLUE + "# * ================================================ * #")
    print(Fore.RED + banner_for_logger)
    print(Fore.YELLOW + function_call)
    print(Fore.BLUE + "# * ================================================ * #")

    # MAke it so that the user can expect reply from bot
    # Make it show "typing..." before sending reply to user
    context.bot.send_chat_action(

        chat_id = get_chat_id(
            update,
            context
        ),

        action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
        timeout = 1
    )

    time.sleep(1)

    ticker = ""

    # Call TwelveDataAPI for this into function, for new instance
    td = TDClient(apikey = "83cdd7a275d2405abee70be07d20b81f")

    if len(context.args) == 1:
        ticker = context.args[0]

        # The metadata to make up time series call for one day
        ts = td.time_series (

            symbol = ticker,
                     interval = "1day",
                 outputsize = 1,
        )

        # Let the bot response first asking for fiat_currency
        get_data_fromAPI_pandas = ts.as_pandas()

        urls_of_ticker_option = ""


        get_open = get_data_fromAPI_pandas['open']
        get_high = get_data_fromAPI_pandas['high']
        get_low = get_data_fromAPI_pandas['low']
        get_close = get_data_fromAPI_pandas['close']
        get_volume = get_data_fromAPI_pandas['volume']

        if ticker == "FB":
            facebook_url = "https://facebook.com/"
            urls_of_ticker_option += "Facebook Group, Inc 👍🏻\n\n" \
                                         + facebook_url + "\n"

        elif ticker == "SPX":
            spacex_url = "https://spacex.com"
            urls_of_ticker_option += "Space X 🚀 \n\n" \
                                         + spacex_url + "\n"

        elif ticker == "TSLA":
            tesla_url = "https://tesla.com"
            urls_of_ticker_option += "Tesla Group, Inc \n\n" \
                                     + tesla_url + "\n"

        elif ticker == "HOOD":
            robinhood_URL = "https://robinhood.com/us/en/"
        #   logo_url = "https://robinhood.com/us/en/"
            urls_of_ticker_option += "Robinhood \n\n" \
                                     + robinhood_URL + "\n"

        elif ticker == "BTI":
            bti_url = "https://drive.google.com/uc?id=1WIoImZSVksKOT7QgzfDV9_xpZE07MKsP&export=download"
            urls_of_ticker_option += "British-Americab Tobacco Plc \n\n" \
                                     + bti_url + "\n"

        elif ticker == "ETN":
            eaton_url = "https://drive.google.com/uc?id=1uIj4VtDDa9H0kfEuCEvkNCnhM6JvzCM2&export=download"
            urls_of_ticker_option += "Eaton Power Corporation \n\n" \
                                     + eaton_url + "\n"

        elif ticker == "PLBY":

            playboy_url = "https://drive.google.com/uc?id=1dTi53tVlVC3H78vl7TP9mMI_5Yh0bXAe&export=download"
            urls_of_ticker_option += "Playboy Enterprises \n\n" \
                                     + playboy_url + "\n"

        update.message.reply_text(
            f"DiGalactic TradeBot💸👨🏻‍🚀 \n\n"
            f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n\n"

            f"Basic Metrics for "
            f"{urls_of_ticker_option} \n\n"

            # Opening Price of Stock. . .
            f"<strong>Open:</strong> \n"
            f"<strong>$ {get_open[0]}</strong> \n\n"

            # The Stock Day's Highest Trading Price
            f"<strong>High:</strong> \n"
            f"<strong>$ {get_high[0]}</strong> \n\n"

            # The Stock's Day's Lowest trading Price
            f"<strong>Low: \n</strong>"
            f"<strong>$ {get_low[0]}</strong> \n\n"

            # The Stock's Day's Closing Price
            f"<strong>Close:</strong> \n"
            f"<strong>$ {get_close[0]}</strong> \n\n"


            f"<strong>Volume: \n</strong>"
            f"<strong>$ {float(get_volume[0])}</strong> \n\n"
            f"🔰 💎 🏦 💸 ⛓ 💸  🏦 💎 🔰 \n\n",

                parse_mode = "html"
        )

# ** ========================================================================== ** #
def coin_data(update, context):

    # ------------------------------------- #
    """
        This is same as the 'global' call function
        except this function can take two arguments
        one for a cryptocurrency and one for a fiat
        currency. The function makes up the bot command
        which will allow a user to take a closer
        look at a coins market data, in comparator mode
        and with a fieat currency of the user's choice

    :param update:
    :param context:
    :return:
    """
    # ------------------------------------- #

    header_banner = pyfiglet.figlet_format("CoinGecko API Context")
    footer_banner = pyfiglet.figlet_format("Called Crypto Function...")
    # the form of Security Index Symbol

    # Make a little log to say that command has been called succedfully
    print(Fore.GREEN + " # * ================================================ * #")
    print(Fore.BLUE + header_banner)
    print(Fore.YELLOW + footer_banner)
    print(Fore.GREEN + "# * ================================================ * #")

    # * ------------------------------------------------------- * #
    # MAke it so that the user can expect reply from bot
    # Make it show "typing..." before sending reply to user
    # * ------------------------------------------------------- * #
    context.bot.send_chat_action(

        chat_id = get_chat_id(
            update,
            context
        ),

        action = telegram.ChatAction.TYPING,  # Return action of bot to inform user
        timeout = 1
    )

    time.sleep(1)

    chat_id = update.message.chat_id # Just to establish a chat_id
    crypto_sym = "" # Cryptocurrenct ticker symbol we use to ID
    fiat_sym = ""   # Fiat currency symbol to ref with crypto_sym
    fiat_24hr_change = ""
    coin_gecko = CoinGeckoAPI() # Change to "CoinGeckoAPI Context"

    # Use the context argument to accept user response
    # as bot command. This command takes two arguments
    if len(context.args) >= 1:

        crypto_sym = context.args[0]
        fiat_sym = context.args[1]
        # fiat_24h_change = context.args[2]

        # Get fiat currencies avaiable from CoinGeckoAPI
        fiat_currency = [
            "xau", # (0)- All comparisons chosen must have Gold ounce
            # correlation to crypto comparison to selected crypto

            "zar",  # (1) - South African ZAR or Rand
            "eur",  # (2) - European Union Euro
            "aud",  # (3) - Australian Dollar
            "nzd",  # (4) - New Zealand Dollar
            "gbp",  # (5) - United Kingdom Pound Sterling
            "usd",  # (6) - American Dollar
            "jpy",  # (7) - Japanese Yen
            "rub",  # (8) - Russian Ruble
            "cny",  # (9) - Chinese Yuan
            "ngn",  # (10) - Nigerian Niera
            "cad",  # (11) - Canada Dollar
            "sek",  # (12) - Swedish Krona
            "mxn",  # (13) - Mexican Peso
            "bmd",  # (14) - Bermudian Dollor
            'ars',  # (15) - Argentine Peso
            "inr",  # (16) - Indian Rupee
            "php",  # (17) - Philliphina Peso
            "aed",  # (18) - United Arab Emirate Dirham
            "bdt",  # (19) - Bangladesh Taka
            "bhd",  # (20) - Bahraini Dinar
            "brl",  # (21) - Brazilian Real
            "chf",  # (22) - Swiss Franc
            "clp",  # (23) - Chilean Peso
            "czk",  # (24) - Czech Republic Koruna
            "dkk",  # (25) - Danish Krone
            "hkd",  # (26) - Hong Kong Dollar
            "huf",  # (27) - Hungarian Forint
            "idr",  # (28) - Indonesian Rupiah
            "ils",  # (29) - Israeli New Shekel
            "krw",  # (30) - Korean Won
            "lkr",  # (31) - Sri-Lankan Rupee
            "mmk",  # (32) - Myanmar Kyat
            "myr",  # (33) - Malaysian Ringgit
            "nok",  # (34) - Norwegian Krone
            "pkr",  # (35) - Pakistani Rupee
            "pln",  # (36) - Polish Zloty
            "sar",  # (37) - Saudi Arabia Riyal
            "sgd",  # (38) - Singapore Dollar
            "thb",  # (39) - Thailand Baht
            "try",  # (40) - Turkish New Lira
            "twd",  # (41) - New Taiwan Dollar
            "uah",  # (42) - Ukraine Hryvnia
            "vef",  # (43) - Venezuelan Bolivar
            "vnd"   # (44) - Vietnamese Dong (LoL)

        ] # Currencies avaible to user from CoinGeckoAPI

        price_of_crypto = coin_gecko.get_price(
            ids = crypto_sym,
            vs_currencies = fiat_currency,

            # Other types of market data for user to quickly look at
            include_24hr_vol = "true",    # The percentage change over 24 hrs
            include_market_cap = "true",  # Market cap of selected coin
            include_24hr_change = "true"
        )

        # Coin Data, from iding it ID to CoinCeckoAPI
        crypto_id = ""
        coin_by_id = coin_gecko.get_coin_by_id(crypto_id)

        crypto_collector = price_of_crypto[crypto_sym] # Garbage collection variable
        # fiat_collector = price_of_crypto[fiat_24hr_change]
        # fiat_collector = price_of_crypto[fiat_sym]

        # Now loop, to dive in deeper on individual coins
        # Here ther which fiat currency they want to use as a
        # comparator

        # List to collect currencies
        fiat_collectEmpty = ""
        fiat_parse_symbols = ""
        coin_urls = ""

        # Colledt variable from inside price_crypto call()
        market_change = coin_gecko.get_price(

                ids = crypto_sym,
                        vs_currencies = fiat_sym,
                    include_24hr_change = "true"
        )

        # *** =========================================== *** #
        """
             Here is where we send the different png images of
             crypto currency selected by user of comparator
        """
        # *** =========================================== *** #


        # *** =========================================== *** #
        """
             Here we make a conditional, so as the bot can return
             a prettified parsed output to the user, and to make it more
             appealing for him or her to identify fiat currency with
             what crypto currency
        """
        # *** =========================================== *** #

        # South African Rand (ZAR)
        if fiat_sym == fiat_currency[1]:

            # If South African Rand
            # For shits and giggles
            # Avalanche (From trending. . .)

            if crypto_sym == "avalanche":

                print(market_change)
                avalanche_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/avalanche.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                        document = avalanche_lunarURL
            )

            # Ardor
            elif crypto_sym == "ardor":

                print(market_change)
                ardor_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/ardor.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = ardor_urlLunar
                )

            # Augur
            elif crypto_sym == "augur":

                print(market_change)
                augur_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/augur.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = augur_urlLunar
                )

            # Aurora
            elif crypto_sym == "aurora":

                print(market_change)
                aurora_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/aurora.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = aurora_urlLunar
                )

            # Akita-Inu NFT
            elif crypto_sym == "akita-inu":

                print(market_change)
                akitinu_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/akita-inu.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = akitinu_lunarURL
                )


            # African-based coins
            elif crypto_sym == "africa-to-mars":

                africa_to_marsURL = "https://pbs.twimg.com/profile_images/1397949885698162690/UrHNhLMe.jpg"
                print(market_change)

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = africa_to_marsURL
                )

            elif crypto_sym == "aave":

                print(market_change)
                aave_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/aave-old.png"


                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                                document = aave_urlLunar
                )

            elif crypto_sym == "allianceblock":

                print(market_change)
                alliance_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/allianceblock.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                                document = alliance_lunarURL
                )

            # This section handles all the coins falling under
            # the "Doge" Ecosystem of Altcoins
            elif crypto_sym == "dogecoin":

                print(market_change)
                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dkhpfm5hits1w.cloudfront.net/dogecoin.png"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                         document = doge_url,

                    caption = f"When Doges come out to bite!"
                )

            elif crypto_sym == "babydoge":

                print(market_change)
                babydoge_url = "https://dkhpfm5hits1w.cloudfront.net/baby-doge-coin.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = babydoge_url,

                        caption = f"Elon is the DogeFather, his son is Baby Doge's"
                )

            # Floki-Inu
            elif crypto_sym == "floki-inu":
                print(market_change)
                floki_inuURL = "https://assets.coingecko.com/coins/images/16746/small/FLOKI.png?1625835665"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = floki_inuURL
                )

            elif crypto_sym == "starlink":

                print(market_change)
                starlink_url = "https://dkhpfm5hits1w.cloudfront.net/starlink.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = starlink_url
            )

            elif crypto_sym == "safedoge":

                print(market_change)
                safedoge_url = "https://dkhpfm5hits1w.cloudfront.net/safedoge.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = safedoge_url
                )

            elif crypto_sym == "dogecash":

                print(market_change)
                dogecash_png = "https://dkhpfm5hits1w.cloudfront.net/dogecash.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                             document = dogecash_png
                )

            # Sanshu-Inu (New Addition to DogeFamily)
            elif crypto_sym == "sanshu-inu":

                print(market_change)
                sanshu_lunar = "https://dkhpfm5hits1w.cloudfront.net/sanshu-inu.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = sanshu_lunar
                )

            # Dogelon Mars
            elif crypto_sym == "dogelon-mars":

                print(market_change)
                dogeLonMarsURL = "https://dkhpfm5hits1w.cloudfront.net/dogelon-mars.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = dogeLonMarsURL
                )

            # Elongate
            elif crypto_sym == "elongate":

                print(market_change)
                elongate_URL = "https://assets.coingecko.com/coins/images/15017/small/fRRPDnh4_400x400.jpg?1619448867"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = elongate_URL
                )

            # DogeBonk
            elif crypto_sym == "dogebonk":

                print(market_change)
                dogebonk_URL = "https://assets.coingecko.com/coins/images/19153/small/dogebonk.png?1634536478"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = dogebonk_URL
                )


            elif crypto_sym == "ethereum":

                print(market_change)
                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = "https://dkhpfm5hits1w.cloudfront.net/ethereum.png"
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = ethereum_url,

                    # Put a caption so read cn get a brief undertanding
                    # of the cryptocurrency they want to at...

                    caption = f"Ethereum is the Second biggest"
                              f" cryptocurrency, it's the first of its"
                              f" kind to be Turing Complete & Programmable."
                              f" This is why we call them 'smart contracts'."
                )

                # toDo --> If over a certain threshold send a surprising Animations
                #          in the form of a Telegram Sticker


            elif crypto_sym == "electroneum":

                print(market_change)
                url_electroneum = "https://dkhpfm5hits1w.cloudfront.net/electroneum.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                              document = url_electroneum
                )

            # EtherGem
            elif crypto_sym == "ethergem":

                print(market_change)
                url_ethergem_lunar = "https://dkhpfm5hits1w.cloudfront.net/ethergem.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_ethergem_lunar
                )

            elif crypto_sym == "ethereum-classic":

                print(market_change)
                url_from_lunar = "https://dkhpfm5hits1w.cloudfront.net/ethereum-classic.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_from_lunar,

                        caption = f"Ethereum Classic is what reminds of its orginal project,"
                                  f" after it was hard forked. This why we have Cardano, Ripple & "
                                  f"Solana & why the three are fierce rivals, as more efficent scalar assetial"
                                  f" paradigms of Ethereum of itself. "
                )

            # Insureum
            elif crypto_sym == "insureum":

                print(market_change)
                insureum_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/insureum.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = insureum_urlLunar
                )

            elif crypto_sym == "ripple":

                print(market_change)
                url_from_lunar = "https://dkhpfm5hits1w.cloudfront.net/xrp.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_from_lunar
                )
            # * --------------------------------------------- * #
            # * ---------------------------------------------
            elif crypto_sym == "solana":

                print(market_change)
                url_solana_Lunar = "https://dkhpfm5hits1w.cloudfront.net/solana.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = url_solana_Lunar
                )

            # Only1
            elif crypto_sym == "only1":

                print(market_change)
                only1_URL = "https://assets.coingecko.com/coins/images/17501/small/like-token.png?1628036165"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = only1_URL
                )

            elif crypto_sym == "verasity":

                print(market_change)
                url_from_lunar_Verasity = "https://dkhpfm5hits1w.cloudfront.net/verasity.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_from_lunar_Verasity
                )

            elif crypto_sym == "waves":

                print(market_change)
                waves_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/waves.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = waves_urlLunar
                )

            # * ---------------------------------------------- * #
                """
                    " BITCOIN Ecosystem of digital coins . . . "
                      Ex: Bitcoin, Bitcoin-Cash, Bitcoin-Gold &
                      Bitcoin-Diamond
                """
            # * ---------------------------------------------- * #
            elif crypto_sym == "bitcoin":

                print(market_change)

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://dkhpfm5hits1w.cloudfront.net/bitcoin.png"
                coin_urls += bitcoin_url

                # toDo --> Here we make a conditional, the caption will
                #          output a different one depending on 24HR Market Change

                #if market_change[1]

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                         document = bitcoin_url,

                            caption = f"Bitcoin is starting to Forge, "
                                      f"won't be long now!"
                                    f"🤘 🚀 "
                )


            elif crypto_sym == "bitcoin-gold":

                 print(market_change)
                 bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                 context.bot.send_document(

                     chat_id = get_chat_id(
                         update,
                         context
                     ),
                     document = bitcoin_gold_url
                 )

            elif crypto_sym  == "wrapped-bitcoin":
                print(market_change)
                wrapped_bitcoinURL = "https://assets.coingecko.com/coins/images/7598/small/wrapped_bitcoin_wbtc.png?1548822744"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = wrapped_bitcoinURL
                )


            elif crypto_sym == "bitcoin-cash":

                print(market_change)
                bitcoin_cashURL = "https://dkhpfm5hits1w.cloudfront.net/bitcoin-cash.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = bitcoin_cashURL,

                                caption = f"Bitcoin Cash is a subset of Bitcoin itself, fundamentally."
                                          f" It is not a hard fork, although programmably it can be "
                                          f" defined as such. Bitcoin Cash is exactly like Bitcoin"
                                          f" created by a developer claiming to be Bitcoin's "
                                          f" original author. However it is an objective Digital Coin. "
                )

            elif crypto_sym == "bitcoin-diamond":

                print(market_change)
                diamond_url = "https://dkhpfm5hits1w.cloudfront.net/bitcoin-diamond.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                                document = diamond_url
                )

            # MicroBitcoin
            elif crypto_sym == "microbitcoin":

                print(market_change)
                lunar_url_MicroBitcoin = "https://dkhpfm5hits1w.cloudfront.net/microbitcoin.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                             document = lunar_url_MicroBitcoin
                )

            # The Silver of Bitcoin (NB Coin) - Litecoin
            elif crypto_sym == "litecoin":

                print(market_change)
                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"
                another_url_to_use = "https://dkhpfm5hits1w.cloudfront.net/litecoin.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = another_url_to_use,

                        caption = f"Litecoin was nobley designed as a 'sacrifice for Bitcoin."
                                  f" This is why it is dubbed the 'Digital Silver'"
                )

            # Filecoin
            elif crypto_sym == "filecoin":

                print(market_change)
                filecoin_URL = "https://assets.coingecko.com/coins/images/12817/small/filecoin.png?1602753933"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = filecoin_URL
                )

            elif crypto_sym == "binancecoin":

                print(market_change)
                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://assets.coingecko.com/coins/images/825/large/binance-coin-logo.png?1547034615'"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = binanc_url, # Get PNG Image Icon from CoinGecko

                        caption = f"Binancecoin is the native Cryptocurrency of"
                                  f" the Binance Crypto Exchange"
                )

            elif crypto_sym == "binamon":

                print(market_change)
                binamon_URL = "https://dkhpfm5hits1w.cloudfront.net/binamon.png"

                context.bot.send_document(
                     chat_id = get_chat_id(
                         update,
                         context
                     ),
                                  document = binamon_URL
                )

            elif crypto_sym == "bakerytoken":

                print(market_change)
                bakery_url = "https://dkhpfm5hits1w.cloudfront.net/bakerytoken.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                ),

                            document = bakery_url # Get PNG Image Icon from CoinGecko
            )

            # Smooth Love Potion
            elif crypto_sym == "smooth-love-potion":

                print(market_change)
                love_potion_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/small-love-potion.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = love_potion_urlLunar
                )

            # Pitbull's Meme coin
            elif crypto_sym == "pitbull":
                print(market_change)
                pitbull_logoURL = "https://assets.coingecko.com/coins/images/15927/small/PitBull.jpg?1622436326"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = pitbull_logoURL
                )

            # Hamster

            elif crypto_sym == "hamster":
                print(market_change)
                hamsterURL = "https://assets.coingecko.com/coins/images/16115/small/hamster.png?1623033031"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = hamsterURL
                )

            # + ------------------------------------------------ + #
            # Coins falling under Shiba-Inu ecosystem
            # + ------------------------------------------------ + #

            # Shiba-Inu Altcoin
            elif crypto_sym == "shiba-inu":

                print(market_change)
                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4,

                    caption = f"Shiba-Inu is currently one of the biggest Cryptocurrency"
                              f" by market cap, liquidity & social engagement and interactivity."
                )

            # Bone of ShibaSwap Ecosystem
            elif crypto_sym == "bone":

                print(market_change)
                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            # "Liquidity Backer" Coin for ShibaSwap ecosystem
            elif crypto_sym == "leash":

                print(market_change)
                leash_lunar = "https://dkhpfm5hits1w.cloudfront.net/leash.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = leash_lunar
                )

            elif crypto_sym == "saitama-inu":

                print(market_change)
                the_url = "https://dkhpfm5hits1w.cloudfront.net/saitama-inu.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                             document = the_url
                )

            # Kitty-Inu (ERC-20)
            elif crypto_sym == "kitty-inu":

                print(market_change)
                kitty_inuURL = "https://assets.coingecko.com/coins/images/19385/small/2Hy412Bd_400x400.png?1635146893"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = kitty_inuURL
                )

            # + ------------------------------------------------ + #
            #            END of defacto Shiba-Inu Ecosystem
            # + ------------------------------------------------ + #

            # Smooth-Love-Potion NFT
            elif crypto_sym == "iostoken":

                print(market_change)
                iostoken_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/iostoken.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = iostoken_lunarURL
                )

            # Internet Computer Coin
            elif crypto_sym == "internet-computer":

                print(market_change)
                ict_LunarURL = "https://dkhpfm5hits1w.cloudfront.net/internet-computer.png"

                context.bot.send_document(
                     chat_id = get_chat_id(
                         update,
                        context
                ),
                                 document = ict_LunarURL,

                    caption = f"Social Content Site FansOnly, has an interest to deploy"
                              f" their video stream applcation on Internet-Computer"
            )

            # Cardano
            elif crypto_sym == "cardano":

                print(market_change)
                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                cardano_url = "https://dkhpfm5hits1w.cloudfront.net/cardano.png"
             #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = cardano_url,

                             caption = f"Cardano is an adaptation of Ethereum,"
                                       f" supposely more scalar in its interpolability."
                )

            # Algorand
            elif crypto_sym == "algorand":

                print(market_change)
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                        document = url6,

                            caption = "Algorand uses Zero Proof Sums,"
                                      " and thus forms a consensus of Staking called"
                                      " Pure Proof-of-Stake. Algorand is a popular ecosystems"
                                      " to create Non Fungible Tokens or NFTs"
                )

            # VeChain
            elif crypto_sym == "vechain":

                print(market_change)
                vechain_URL = "https://assets.coingecko.com/coins/images/1167/small/VeChain-Logo-768x725.png?1547035194"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = vechain_URL,

                                caption = f"VeChain is a DeFi Blockchain, working in the "
                                          f"context of IoT (Internet-of-Things). It is intended "
                                          f"to improve supply chains in loggitics"
                )

            # CumRocket
            elif crypto_sym == "cumrocket":

                print(market_change)
                cumrocket_url = "https://drive.google.com/uc?id=11A3lcWPKHZYkFvSUmPTHJvJAUmzplGgD&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = cumrocket_url,

                        caption = f"CumRocket is a Non-Fungible Token spawned from the "
                                  f" liking of Tik Tok engineering, and development. It relies"
                                  f" heavily on social sentiment from social media. CumRocket has "
                                  f" basis goal of turning Internet Pornography into a billion dollar"
                                  f" industry, not that it isn't already, anyway... Elon Musk"
                                  f" is known supporter of cryptocurrency, which is actually a PoS"
                                  f" non-fungible token."
                )

            # PornRocket
            elif crypto_sym == "pornrocket":

                print(market_change)
                porn_lunar = "https://dkhpfm5hits1w.cloudfront.net/pornrocket.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = porn_lunar,

                        caption = f"PornRocket is a replicated model of CumRocket, meant"
                                  f" to accomadate the world biggest adult content website, PorHub.com"
                )

            elif crypto_sym == "nftinder":

                print(market_change)
                nftinder_URL = "https://assets.coingecko.com/coins/images/21186/small/15521.png?1638514214"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = nftinder_URL
                )

            # + ------------------------------------------------------ + #
            #       Coins using Ring Functions and with privacy Emphaises
            # + ------------------------------------------------------ + #

            # Monero Privacy Coin
            elif crypto_sym == "monero":

                print(market_change)
                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"
                lunar_url = "https://dkhpfm5hits1w.cloudfront.net/monero.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = lunar_url,

                                caption = f"Monero is a Privacy Digital Coin, and"
                                          f" uses Ring Signatures for Hashing and Encryption."
                                          f" Monero means 'Money' in Latin.",
                )


            # Dash Privacy Coin
            elif crypto_sym == "dash":

                print(market_change)
                dash_URL = "https://assets.coingecko.com/coins/images/19/small/dash-logo.png?1548385930"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = dash_URL,

                                caption = f"Dash is a Privacy focused Digital"
                                          f"Currency, similar to Monero & ZCash"
                )

            # MobileCoin
            elif crypto_sym == "mobilecoin":

                print(market_change)
                mobileCoin_Url = "https://assets.coingecko.com/coins/images/13311/small/mobilecoin.png?1629958621"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = mobileCoin_Url,

                                caption = f"Signal Messenger can now act as " \
                                          f"an oracle for MobileCoin"
                )

            # TrueFi Defi NFT
            elif crypto_sym == "truefi":

                # --> toDO want to test and if CoinGeckoUrls have direct download link
                #      ok it seems it does, but make sure you link the bigger glph image
                print(market_change)
                truefi_url = "https://assets.coingecko.com/coins/images/13180/large/truefi_glyph_color.png?1617610941"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = truefi_url
                )

            # Axie-Infinity and GameStop NFT
            elif crypto_sym == "axie-infinity":

                axie_url = "https://dkhpfm5hits1w.cloudfront.net/axie-infinity.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = axie_url
                )

            # ChainLink
            elif crypto_sym == "chainlink":
                # ChainLink()

                print(market_change)
                chainlink_well_their_urlLINK = "https://dkhpfm5hits1w.cloudfront.net/chainlink.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                              document = chainlink_well_their_urlLINK
                )

            # Thorchain (DEFI Coin)
            elif crypto_sym == "thorchain":

                print(market_change)
                thorchain_lunar = "https://dkhpfm5hits1w.cloudfront.net/thorchain.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                                 document = thorchain_lunar
                )

            # HyperAlloy
            elif crypto_sym == "hyperalloy":

                print(market_change)
                hyperalloy_urlLuna = "https://dkhpfm5hits1w.cloudfront.net/hyperalloy.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = hyperalloy_urlLuna
                )

            elif crypto_sym == "cosmos":

                print(market_change)
                cosmos_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/cosmos.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = cosmos_lunarURL
                )

            # Look-rare
            elif crypto_sym == "looks-rare":

                print(market_change)
                looksrare_URL = "https://assets.coingecko.com/coins/images/22173/small/circle-black-256.png?1641173160"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = looksrare_URL
                )

            # BomberCoin
            elif crypto_sym == "bomber-coin":

                print(market_change)
                bomberCoin_URL = "https://assets.coingecko.com/coins/images/18567/small/bcoin.png?1638171024"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = bomberCoin_URL
                )

            elif crypto_sym == "iotex":

                print(market_change)
                iotex_URL = "https://dkhpfm5hits1w.cloudfront.net/iotex.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = iotex_URL,

                                caption = "The US Navy is piloting a Blockchain"
                                          " logistics protocol, to help with medical supply"
                                          " chains. They have just recently announced a collabration"
                                          " with IoTeX. "
                )

            # A trending coin of the day (13 Aug 2021) - "Fantom"
            elif crypto_sym == "fantom":

                print(market_change)
                fantom_url = "https://dkhpfm5hits1w.cloudfront.net/fantom.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = fantom_url
                )

            # SafeMoon
            elif crypto_sym == "safemoon":

                print(market_change)
                safemoon_png = "https://dkhpfm5hits1w.cloudfront.net/safemoon.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = safemoon_png,

                        caption = f"Safemoon is a 'Memetoken', not all too"
                                  f" different from Shiba-Inu, Dogecoin and all that JaZZ"
                )

            # TRON (Adaptation of Telegram Open Network)
            elif crypto_sym == "tron":

                print(market_change)
                tron_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/tron.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = tron_lunarURL,

                         caption = f"Tron is based the orginal Open Network's "
                                   f" native cryptocurrency 'Gram', first piloted and"
                                   f" developed by the Wizards of Telegram. After the SEC"
                                   f" banned Telegram from offering Grams on TON in an ICO,"
                                   f" TRON was formed as its first fork."
                )

            # Toncoin (The Open Network)
            elif crypto_sym == "the-open-network":

                print(market_change)
                toncoin_URL = "https://assets.coingecko.com/coins/images/17980/small/ton.PNG?1630023132"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = toncoin_URL,

                        caption = "Toncoin is the native cryptocurrency of the TON Blockchain, " \
                                  "& The Open Network (TON) Multichain Ecosystem. TON is the worked directly forked"
                                  " from Dr Durov, to the Open Source Community, after the American SEC legally"
                                  " banned and forbade it's 'GRAM' ICO (Initial Coin Offering)."
                                  " After the court ruling the work done by the Telegram Engineering, was"
                                  "forked to Github, for Open Source Development. The Project holds "
                                  "massive potential and is even a favourite of OpenAI."
                )

            # Uniswap Swap Coin
            elif crypto_sym == "uniswap":

                print(market_change)
                uniswap_lunar = "https://dkhpfm5hits1w.cloudfront.net/uniswap.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = uniswap_lunar
                )

            # Polkadot
            elif crypto_sym == "polkadot":

                print(market_change)
                polkadot_lunar = "https://dkhpfm5hits1w.cloudfront.net/polkadot.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                              document = polkadot_lunar,
                              caption = f"Polkadot is known as a 'Multichain'"
                                        f" Ecosystem, and it possibilities are endless!"
                )

            # PolkadoDoge
            elif crypto_sym == "polkadoge":

                print(market_change)
                url_PolkadoDoge_lunar = "https://dkhpfm5hits1w.cloudfront.net/polkadoge.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_PolkadoDoge_lunar
                )

            elif crypto_sym == "math":

                print(market_change)
                mathURL = "https://assets.coingecko.com/coins/images/11335/small/2020-05-19-token-200.png?1589940590"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = mathURL
                )

            # Moonriver NFT from $DOT Ecosystem
            elif crypto_sym == "moonriver":

                print(market_change)
                url_MoonRiver = "https://dkhpfm5hits1w.cloudfront.net/moonriver.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_MoonRiver
                )

            # DigiByte
            elif crypto_sym == "digibyte":

                print(market_change)
                digibyte_lunar = "https://dkhpfm5hits1w.cloudfront.net/digibyte.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = digibyte_lunar
                )

            # + ------------------------------------------------- + #
            #      Section where stable coins get handled with the
            #       conditional clause of Fiat currency selected
            # + ------------------------------------------------- + #

            # TerraUSD Stablecoin (T0 US Dollar backed)
            elif crypto_sym == "terrausd":

                print(market_change)
                terrausd_lunar = "https://dkhpfm5hits1w.cloudfront.net/terrausd.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                 document = terrausd_lunar,

                        caption = f" TerraUSD is a Stablecoin, it's suppose to back the"
                                  f" Fiat US Dollar in a digital consensus and Timestamp"
                )

            # Tether (Stablecoin developed by Circle Digital Bank)
            elif crypto_sym == "tether":

                print(market_change)
                tetherLunar_url = "https://dkhpfm5hits1w.cloudfront.net/tether.png"

                context.bot.send_document(
                    get_chat_id(
                        update,
                        context
                    ),
                                document = tetherLunar_url,

                        caption = "Tether is a Stablecoin controlled by Crypto Exchange"
                                  "Bitfinex, which in turn is owned and operated iFinex Inc"
                                  "in the British Virgin Isles"
                )

            # SuperMoon (ER-20 NFT - Binance smart Chain)
            elif crypto_sym == "supermoon":

                print(market_change)
                supermoon_lunar = "https://dkhpfm5hits1w.cloudfront.net/supermoon.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                ),
                             document = supermoon_lunar
            )

            # Dai StableCoin
            elif crypto_sym == "dai":

                print(market_change)
                dai_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/dai.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                document = dai_lunarURL,

                            caption = f"Dai is actually an older Project, than that of Bitcoin,"
                                      f" It has been imporoved wither newer inights, coming from"
                                      f" that famous whitepaper. DAI is like a Stablecoin of"
                                      f" Bitcoin. "
                )

            # + ------------------------------------------------- + #
            #   END of Stablecoin section of fiat currency clause
            # + ------------------------------------------------- + #

            elif crypto_sym == "spacegrime":

                print(market_change)
                spce_grimeURL = "https://dkhpfm5hits1w.cloudfront.net/spacegrime.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                                 document = spce_grimeURL
                )

            elif crypto_sym == 'stellar':

                print(market_change)
                stellar_url_Lunar = "https://dkhpfm5hits1w.cloudfront.net/stellar.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                             document = stellar_url_Lunar
                )

            elif crypto_sym == "vulcan-forged":

                print(market_change)
                url_vulcanForged_lunar = "https://dkhpfm5hits1w.cloudfront.net/vulcan-forged.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_vulcanForged_lunar
                )

            elif crypto_sym == "dragonchain":

                print(market_change)
                url_dragonChain = "https://dkhpfm5hits1w.cloudfront.net/dragonchain.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_dragonChain
                )

            elif crypto_sym == "solanium":

                print(market_change)
                url_SolaniumLunar = "https://dkhpfm5hits1w.cloudfront.net/solanium.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_SolaniumLunar
                )

            elif crypto_sym == "paint":

                print(market_change)
                paint_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/paint.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                             document = paint_urlLunar
                )

            elif crypto_sym == "polymath":

                print(market_change)
                url_polymath_Lunar = "https://dkhpfm5hits1w.cloudfront.net/polymath.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = url_polymath_Lunar
                )

            elif crypto_sym == "huobi-token":

                print(market_change)
                url_hub_lunar = "https://dkhpfm5hits1w.cloudfront.net/huobi-token.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                               document = url_hub_lunar
                )
            # Z-Cash
            elif crypto_sym == "zcash":

                print(market_change)
                zcash_LunarURL = "https://dkhpfm5hits1w.cloudfront.net/zcash.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = zcash_LunarURL
                )

            # ByteCoin
            elif crypto_sym == "bytecoin":

                print(market_change)
                bytecoin_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/bytecoin.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = bytecoin_urlLunar
                )

            # TeZos
            elif crypto_sym == "tezos":

                print(market_change)
                tezos_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/tezos.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = tezos_urlLunar
                )

            # LA-Token
            elif crypto_sym == "latoken":

                print(market_change)
                latoken_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/latoken.png"

                context.bot.send_document(

                    chat_id = get_chat_id(

                        update,
                        context
                    ),
                            document = latoken_urlLunar
                )

            # Lambda
            elif crypto_sym == "lambda":

                print(market_change)
                lambdaURL_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/lambda.png"

                context.bot.send_document(

                    chat_id = get_chat_id(

                        update,
                        context
                    ),
                            document = lambdaURL_urlLunar
                )

            # Nexo
            elif crypto_sym == "nexo":

                print(market_change)
                nexo_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/nexo.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = nexo_urlLunar
                )

            # Enigma
            elif crypto_sym == "enigma":

                print(market_change)
                enigma_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/enigma.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = enigma_urlLunar
                )

            # EnjinCoin (NFT)
            elif crypto_sym == "enjincoin":

                print(market_change)
                enjinURL = "https://assets.coingecko.com/coins/images/1102/small/enjin-coin-logo.png?1547035078"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = enjinURL
                )

            # LiSk
            elif crypto_sym == "lisk":

                print(market_change)
                lisk_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/lisk.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = lisk_urlLunar
                )

            # Komodo
            elif crypto_sym == "komodo":

                print(market_change)
                komodo_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/komodo.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = komodo_urlLunar
                )

            # Blocknet
            elif crypto_sym == "blocknet":

                print(market_change)
                blocknet_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/blocknet.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = blocknet_urlLunar
                )

            # IOTA
            elif crypto_sym == "iota":

                print(market_change)
                iota_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/iota.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = iota_urlLunar
                )

            # Quantum resistant Ledger
            elif crypto_sym == "quantum-resistant-ledger":

                print(market_change)
                quantum_ledger = "https://dkhpfm5hits1w.cloudfront.net/quantum-resistant-ledger.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                             document = quantum_ledger
                )

            # Banano Meme-Token
            elif crypto_sym == "banano":

                print(market_change)
                banano_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/banano.png"

                context.bot.send_document(

                    chat_id = get_chat_id(

                        update,
                        context
                    ),
                            document = banano_urlLunar
                )

            # HedgeTrade
            elif crypto_sym == "hedgetrade":

                print(market_change)
                hedgetrade_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/hedgetrade.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = hedgetrade_urlLunar
                )

            # EOS
            elif crypto_sym == "eos":

                print(market_change)
                eos_urlLunar = "https://dkhpfm5hits1w.cloudfront.net/eos.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = eos_urlLunar
                )

            # * ----------------------------------------------------- * #
            #                    Metaverse Coins
            # * ----------------------------------------------------- * #

            # UFO-Gaming
            elif crypto_sym == "ufo-gaming":

                print(market_change)

                ufo_gamingURL = "https://assets.coingecko.com/coins/images/16801/small/ufo_logo.jpg?1630078847"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = ufo_gamingURL
                )

            # The Sandbox
            elif crypto_sym == "the-sandbox":

                print(market_change)
                the_sandboxURL = "https://assets.coingecko.com/coins/images/12129/small/sandbox_logo.jpg?1597397942"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = the_sandboxURL
                )

            # Dentraland
            elif crypto_sym == "dencentraland":

                print(market_change),
                decentraland_URL = "https://assets.coingecko.com/coins/images/878/small/decentraland-mana.png?1550108745"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                             document = decentraland_URL
                )

            # Star-Atlas
            elif crypto_sym == "star-atlas":

                print(market_change)
                starAtlas_URL = "https://assets.coingecko.com/coins/images/17659/small/Icon_Reverse.png?1628759092"

                context.bot.send_document(

                    chat_id - get_chat_id(
                        context,
                        update
                    ),

                            document = starAtlas_URL
                )

            # * --------------------------------------------------------- * #
            #             Newly Added Coins on CoinGecko API Section
            # * --------------------------------------------------------- * #
            # Cigarette-Token

            elif crypto_sym == "cigarette-token":

                print(market_change)
                cigaretteURL = "https://assets.coingecko.com/coins/images/22145/small/cig.png?1640929916"

                other_cigURL = "https://dkhpfm5hits1w.cloudfront.net/cig.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = cigaretteURL
                )

            # FlexQ

            elif crypto_sym == "flexq":

                print(market_change)
                flexQURL = "https://assets.coingecko.com/coins/images/22143/small/fq_256.png?1640929095"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = flexQURL
                )

            # Galaxy Coin

            elif crypto_sym == "galaxycoin":

                print(market_change)
                galaxy_coinURL = "https://assets.coingecko.com/coins/images/22159/small/Nj8bssS8_400x400.jpg?1640948514"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                            document = galaxy_coinURL
                )

            # Moonbeam
            elif crypto_sym == "moonbeam":

                print(market_change)

                moonbeam_URL = "https://assets.coingecko.com/coins/images/22459/small/glmr.png?1641880985"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                            document = moonbeam_URL,

                                caption = f"Making some Moves!"
                )

            # MkwZY_g2V3rWw-Y
            # What's the bot gets to parse to user out in chat prompt
            # ----------------------------------------------------- #
            south_africa = "🇿🇦 Republic of South Africa (Rand)"
            currency_symbolZAR = "R"
            fiat_collectEmpty += south_africa
            fiat_parse_symbols += currency_symbolZAR
            # ----------------------------------------------------- #

        # Gold Ounce
        elif fiat_sym == fiat_currency [0]:
            # Else it will be an ounce of Gold

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            elif crypto_sym == "monero":

                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url8
                )

            elif crypto_sym == "litecoin":

                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_litecoin_icon
                )

                # + -------------------------------------- + #
            ounce_of_gold = "💰 Ounce of Gold"
            fiat_collectEmpty += ounce_of_gold
            # + -------------------------------------- + #

        # European Union Euro
        elif fiat_sym == fiat_currency[2]:
            # Otherwise we get European Union Euro

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                            context
                    ),

                            document = url_ether
            )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            elif crypto_sym == "monero":

                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url8
                )

            elif crypto_sym == "litecoin":

                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_litecoin_icon
                )

                # + -------------------------------------------- + #
            euro = "🇪🇺 European Union (Euro)"
            currency_symbolEUR = "€"
            fiat_collectEmpty += euro
            fiat_parse_symbols += currency_symbolEUR
            # + -------------------------------------------- + #

        # Aussie Dollar
        elif fiat_sym == fiat_currency[3]:
            # Australian Dollar

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            elif crypto_sym == "monero":

                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url8
                )

            elif crypto_sym == "litecoin":

                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_litecoin_icon
                )

            # + -------------------------------------------- + #
            aus_dollar = "🇦🇺 Australian Federation (AU$)"
            currency_symbolAUD = "AU$"
            fiat_collectEmpty += aus_dollar
            fiat_parse_symbols += currency_symbolAUD
            # + -------------------------------------------- + #

        # New Zealand Dollar
        elif fiat_sym == fiat_currency[4]:
            # New Zealand Dollar

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            elif crypto_sym == "monero":

                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url8
                )

            elif crypto_sym == "litecoin":

                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_litecoin_icon
                )

            # + --------------------------------------------- + #
            nz_dollar = "🇳🇿 Republic of New Zealand (NZ$)"
            currency_symbolNZD = "NZ$"
            fiat_collectEmpty += nz_dollar
            fiat_parse_symbols += currency_symbolNZD
            # + -------------------------------------------- + #

        # UK Pound Sterling
        elif fiat_sym == fiat_currency[5]:
            # United Kingdom Pound Sterling

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            elif crypto_sym == "monero":

                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url8
                )

            elif crypto_sym == "litecoin":

                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_litecoin_icon
                )

            # + ------------------------------------------------- + #
            uk_pound = "🇬🇧 The British Isles (Pound Sterling)"
            currency_symbolUK = "£"
            fiat_collectEmpty += uk_pound
            fiat_parse_symbols += currency_symbolUK
            # + ------------------------------------------------ + #

        # US Dollar
        elif fiat_sym == fiat_currency[6]:
            # American Dollar (Mainland America)

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            us_dollar = "🇺🇸 United States of America (US$ Dollar)"
            currency_symbolUSD = "$"
            fiat_collectEmpty += us_dollar
            fiat_parse_symbols += currency_symbolUSD
            # + -------------------------------------------------- + #

        # Japanese Yen
        elif fiat_sym == fiat_currency[7]:
            # Japanese Yen

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # + ------------------------------------------------- + #
            jp_yen = "🇯🇵 Monarchy of Japan (Yen)"
            currency_symbolJPY = "¥"
            fiat_collectEmpty += jp_yen
            fiat_parse_symbols += currency_symbolJPY
            # + -------------------------------------------------- + #

        # Russian Ruble
        elif fiat_sym == fiat_currency[8]:
            # If Russian Ruble

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            rus_rub = "🇷🇺 Russian Federation (Ruble ₽)"
            currency_symbolRUB = "₽"
            fiat_collectEmpty += rus_rub
            fiat_parse_symbols += currency_symbolRUB
            # + -------------------------------------------------- + #

        # Chinese Yuan
        elif fiat_sym == fiat_currency[9]:
            # People's Republic of China Yuan (CNY)

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            china_yuan = "🇨🇳 People's Republic of China (Yuan)"
            currency_symbolRMB = "￥"
            fiat_collectEmpty += china_yuan
            fiat_parse_symbols += currency_symbolRMB
            # + ------------------------------------------------- + #

        # Nigerian Naiera
        elif fiat_sym == fiat_currency[10]:
            # Nigerian Neira

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            nigerian_neira = "🇳🇬 Nigerian Federation (Naira)"
            fiat_symbolNGN = "₦"
            fiat_collectEmpty += nigerian_neira
            fiat_parse_symbols = fiat_symbolNGN
            # + ------------------------------------------------- + #

        # Canadian Dollar
        elif fiat_sym == fiat_currency[11]:
            # Canadian Dollar

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            canadian_dollar = "🇨🇦 Republic of Canada (CA$)"
            currency_symbolCAD = "$"
            fiat_collectEmpty += canadian_dollar
            fiat_parse_symbols += currency_symbolCAD
            # + -------------------------------------------------- + #

        # Swedish Krona
        elif fiat_sym == fiat_currency[12]:
            # Swedish Krona

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            sweden_krona = "🇸🇪 Monarchy of Sweden (Krona)"
            currency_symbolSEK = "K"
            fiat_collectEmpty += sweden_krona
            fiat_parse_symbols += currency_symbolSEK
            # + ------------------------------------------------- + #

        # Mexican Peso
        elif fiat_sym == fiat_currency[13]:
            # Mexican Peso

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # + ------------------------------------------------- + #
            mexico_peso = "🇲🇽 United States of Mexico (Peso)"
            currency_symbolMXN = "$"
            fiat_collectEmpty += mexico_peso
            fiat_parse_symbols += currency_symbolMXN
            # + ------------------------------------------------- + #

        # Island of Bermuda Dollar (They use American Dollars in Bermuda)
        elif fiat_sym == fiat_currency[14]:
            # Bermuda Dollar

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            bermuda_dollar = "🇧🇲 Republic of Bermuda"
            currency_symbolBMD = "$"
            fiat_collectEmpty += bermuda_dollar
            fiat_parse_symbols += currency_symbolBMD
            # + -------------------------------------------------- + #

        # Argentine Peso
        elif fiat_sym == fiat_currency[15]:
            # Argentine Peso (ARS)

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                     ),

                             document = bitcoin_gold_url
            )


            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            argentine_peso = "🇦🇷 Federation of Argentina (Peso)"
            currency_symbolARS = "$"
            fiat_collectEmpty += argentine_peso
            fiat_parse_symbols += currency_symbolARS
            # ------------------------------------------------------ #

        # Indian Rupee
        elif fiat_sym == fiat_currency[16]:
            # Indian Rupee

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            indian_rupee = "🇮🇳 Republic of India (Rupee)"
            currency_symbolINR = "	₹"
            fiat_collectEmpty += indian_rupee
            fiat_parse_symbols += currency_symbolINR
            # + -------------------------------------------------- + #

        # The Philliphina Peso
        elif fiat_sym == fiat_currency[17]:
            # Philphinia Peso

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            phil_peso = "🇵🇭 Republic of the Philliphines (Peso)"
            currency_symbolPHP = "₱"
            fiat_collectEmpty += phil_peso
            fiat_parse_symbols += currency_symbolPHP
            # + ------------------------------------------------- + #

        # United arab Emirates Dirham (AED)
        elif fiat_sym == fiat_currency[18]:
            # United arab Emirates Dirham (AED)

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )
            # + ------------------------------------------------- + #
            uae_dirham = "🇦🇪 United Arab Emirates (Dirham)"
            currency_symbolAED = "د.إ"
            fiat_collectEmpty += uae_dirham
            fiat_parse_symbols += currency_symbolAED
            # + ------------------------------------------------- + #

        # Bangladeshi Taka
        elif fiat_sym == fiat_currency[19]:
            # Bangladesh Taka (BDT)

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                         document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # + ------------------------------------------------- + #
            bangladesh_taka = "🇧🇩 Republic of Bangladesh (Taka)"
            currency_symbol = "৳"
            fiat_collectEmpty += bangladesh_taka
            fiat_parse_symbols += currency_symbol
            # + ------------------------------------------------- + #

        # Baharaini Dinar
        elif fiat_sym == fiat_currency[20]:
            # Bahraini Dinar

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # + ------------------------------------------------- + #
            bahraini_dinar = "🇧🇭 Kingfom of Baharain"
            fiat_currency_symbolBHD = ".د.ب"
            fiat_collectEmpty += bahraini_dinar
            fiat_parse_symbols += fiat_currency_symbolBHD
            # + ------------------------------------------------- + #

            print(crypto_collector)

        # Brazilain Real
        elif fiat_sym == fiat_currency[21]:

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # + ------------------------------------------------- + #
            brazil_real = "🇧🇷 Federation of Brazil"
            fiat_currency_symbolBRL = "R$"
            fiat_collectEmpty += brazil_real
            fiat_parse_symbols += fiat_currency_symbolBRL
            # + ------------------------------------------------- + #

        # Swiss Franc (CHR)
        elif fiat_sym == fiat_currency[22]:

            # If crypto is dogecoin
            if crypto_sym == "dogecoin":

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dogecoin.com/"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url1
                )

            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = ""
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url_ether
                )

            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://bitcoin.org/en/"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url2
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://www.binance.com/en"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url3
                )

            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                #   shiba_url = "https://www.shibatoken.com/"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url5
                )

            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # + ------------------------------------------------- + #
            swiss_franc = "🇨🇭 Monarchy of Switzerland"
            fiat_currency_symbolCHR = "CHF"
            fiat_collectEmpty += swiss_franc
            fiat_parse_symbols += fiat_currency_symbolCHR
            # + ------------------------------------------------- + #

        # Chilean Peso (CLP)
        elif fiat_sym == fiat_currency[23]:

            # This section handles all the coins falling under
            # the "Doge" Ecosystem of Altcoins
            if crypto_sym == "dogecoin":

                print(market_change)

                url1 = "https://drive.google.com/uc?id=1Xu8A8bPig2MWZqjvOP3qRJzhADyHJki0&export=download"
                doge_url = "https://dkhpfm5hits1w.cloudfront.net/dogecoin.png"
                coin_urls += doge_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = doge_url
                )

            elif crypto_sym == "babydoge":

                babydoge_url = "https://dkhpfm5hits1w.cloudfront.net/baby-doge-coin.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = babydoge_url
                )

            elif crypto_sym == "safedoge":

                safedoge_url = "https://dkhpfm5hits1w.cloudfront.net/safedoge.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = safedoge_url
                )

            elif crypto_sym == "dogecash":

                dogecash_png = "https://dkhpfm5hits1w.cloudfront.net/dogecash.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = dogecash_png
                )

            # Sanshu-Inu (New Addition to DogeFamily)
            elif crypto_sym == "sanshu-inu":

                sanshu_lunar = "https://dkhpfm5hits1w.cloudfront.net/sanshu-inu.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = sanshu_lunar
                )


            elif crypto_sym == "ethereum":

                url_ether = "https://drive.google.com/uc?id=1XG8s9I9D30oJtkVrqoVAcYl0SnreoaT6&export=download"
                ethereum_url = "https://dkhpfm5hits1w.cloudfront.net/ethereum.png"
                coin_urls + ethereum_url

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = ethereum_url
                )

                # * ---------------------------------------------- * #
                """
                    " BITCOIN Ecosystem of digital coins . . . "
                      Ex: Bitcoin, Bitcoin-Cash, Bitcoin-Gold &
                      Bitcoin-Diamond
                """
            # * ---------------------------------------------- * #
            elif crypto_sym == "bitcoin":

                url2 = "https://drive.google.com/uc?id=1iv-rZ58q7DSkqtEpIhBdyERO-DOcDghA&export=download"
                bitcoin_url = "https://dkhpfm5hits1w.cloudfront.net/bitcoin.png"
                coin_urls += bitcoin_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_url
                )

            elif crypto_sym == "bitcoin-gold":

                bitcoin_gold_url = "https://drive.google.com/uc?id=1Sm9ZWlbZ62uvEl8-88roUuFxOfRpAbUH&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bitcoin_gold_url
                )


            elif crypto_sym == "bitcoin-cash":

                bitcoin_cashURL = "https://dkhpfm5hits1w.cloudfront.net/bitcoin-cash.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = bitcoin_cashURL
                )

            elif crypto_sym == "bitcoin-diamond":

                diamond_url = "https://dkhpfm5hits1w.cloudfront.net/bitcoin-diamond.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = diamond_url
                )

            # The Silver of Bitcoin (NB Coin) - Litecoin
            elif crypto_sym == "litecoin":

                url_litecoin_icon = "https://drive.google.com/uc?id=1LFie07Ggu9JZJtiVH6j8CBw-JIIyuFpL&export=download"
                another_url_to_use = "https://dkhpfm5hits1w.cloudfront.net/litecoin.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = another_url_to_use
                )

            elif crypto_sym == "binancecoin":

                url3 = "https://drive.google.com/uc?id=1W0evq53OMOXsrStnUpWDivh4AZrwuFaf&export=download"
                binanc_url = "https://assets.coingecko.com/coins/images/825/large/binance-coin-logo.png?1547034615'"
                coin_urls += binanc_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = binanc_url # Get PNG Image Icon from CoinGecko
                )

            elif crypto_sym == "bakerytoken":

                bakery_url = "https://dkhpfm5hits1w.cloudfront.net/bakerytoken.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = bakery_url # Get PNG Image Icon from CoinGecko
                )

            # + ------------------------------------------------ + #
            # Coins falling under Shiba-Inu ecosystem
            # + ------------------------------------------------ + #

            # Shiba-Inu Altcoin
            elif crypto_sym == "shiba-inu":

                url4 = "https://drive.google.com/uc?id=1GHKhn02HQCHeFbNfezwt-xIbJyeU7_go&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = url4
                )

            # Bone of ShibaSwap Ecosystem
            elif crypto_sym == "bone":

                bone_url = "https://drive.google.com/uc?id=1gRtZVLkRsMjq8uIh7uYhI8siEdb1FfxQ&export=download"
                shiba_url = "https://www.shibatoken.com/"
                coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = bone_url
                )

            # "Liquidity Backer" Coin for ShibaSwap ecosystem
            elif crypto_sym == "leash":

                leash_lunar = "https://dkhpfm5hits1w.cloudfront.net/leash.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = leash_lunar
                )

            elif crypto_sym == "saitama-inu":

                the_url = "https://dkhpfm5hits1w.cloudfront.net/saitama-inu.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = the_url
                )

            # + ------------------------------------------------ + #
            #            END of defacto Shiba-Inu Ecosystem
            # + ------------------------------------------------ + #

            # Cardano
            elif crypto_sym == "cardano":

                url5 = "https://drive.google.com/uc?id=17jKiNCZJ7pd_OcaV5iFA1wPvPWNeSHQx&export=download"
                cardano_url = "https://dkhpfm5hits1w.cloudfront.net/cardano.png"
                #   coin_urls += shiba_url

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = cardano_url
                )

            # Algorand
            elif crypto_sym == "algorand":
                url6 = "https://drive.google.com/uc?id=14aiVK2GuWrvBxr_ITODBFB0as7o_Sdny&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = url6
                )

            # CumRocket
            elif crypto_sym == "cumrocket":

                cumrocket_url = "https://drive.google.com/uc?id=11A3lcWPKHZYkFvSUmPTHJvJAUmzplGgD&export=download"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = cumrocket_url
                )
            # + ------------------------------------------------------ + #
            #       Coins using Ring Functions and with privacy Emphaises
            # + ------------------------------------------------------ + #

            # Monero Privacy Coin
            elif crypto_sym == "monero":

                url8 = "https://drive.google.com/uc?id=1PDlmBdllKLx6r73JK5ITvEaJYixB5uW8&export=download"
                lunar_url = "https://dkhpfm5hits1w.cloudfront.net/monero.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = lunar_url
                )

            # TrueFi Defi NFT
            elif crypto_sym == "truefi":

                # --> toDO want to test and if CoinGeckoUrls have direct download link
                #      ok it seems it does, but make sure you link the bigger glph image
                truefi_url = "https://assets.coingecko.com/coins/images/13180/large/truefi_glyph_color.png?1617610941"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = truefi_url
                )

            # Axie-Infinity and GameStop NFT
            elif crypto_sym == "axie-infinity":

                axie_url = "https://dkhpfm5hits1w.cloudfront.net/axie-infinity.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = axie_url
                )

            # ChainLink
            elif crypto_sym == "chainlink":
                # ChainLink()
                chainlink_well_their_urlLINK = "https://dkhpfm5hits1w.cloudfront.net/chainlink.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = chainlink_well_their_urlLINK
                )

            # Thorchain (DEFI Coin)
            elif crypto_sym == "thorchain":

                thorchain_lunar = "https://dkhpfm5hits1w.cloudfront.net/thorchain.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = thorchain_lunar
                )

            # A trending coin of the day (13 Aug 2021) - "Fantom"
            elif crypto_sym == "fantom":

                fantom_url = "https://dkhpfm5hits1w.cloudfront.net/fantom.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = fantom_url
                )

            # SafeMoon
            elif crypto_sym == "safemoon":

                safemoon_png = "https://dkhpfm5hits1w.cloudfront.net/safemoon.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = safemoon_png
                )

            # TRON (Adaptation of Telegram Open Network)
            elif crypto_sym == "tron":

                tron_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/tron.png"

                context.bot.send_document(

                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = tron_lunarURL
                )

            # Uniswap Swap Coin
            elif crypto_sym == "uniswap":

                uniswap_lunar = "https://dkhpfm5hits1w.cloudfront.net/uniswap.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = uniswap_lunar
                )

            # DigiByte
            elif crypto_sym == "digibyte":

                digibyte_lunar = "https://dkhpfm5hits1w.cloudfront.net/digibyte.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),

                    document = digibyte_lunar
                )

            # + ------------------------------------------------- + #
            #      Section where stable coins get handled with the
            #       conditional clause of Fiat currency selected
            # + ------------------------------------------------- + #

            # TerraUSD Stablecoin (T0 US Dollar backed)
            elif crypto_sym == "terrausd":

                terrausd_lunar = "https://dkhpfm5hits1w.cloudfront.net/terrausd.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = terrausd_lunar
                )

            # Tether (Stablecoin developed by Circle Digital Bank)
            elif crypto_sym == "tether":

                tetherLunar_url = "https://dkhpfm5hits1w.cloudfront.net/tether.png"

                context.bot.send_document(
                    get_chat_id(
                        update,
                        context
                    ),
                    document = tetherLunar_url
                )

            # SuperMoon (ER-20 NFT - Binance smart Chain)
            elif crypto_sym == "supermoon":
                supermoon_lunar = "https://dkhpfm5hits1w.cloudfront.net/supermoon.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = supermoon_lunar
                )

            # Dai StableCoin
            elif crypto_sym == "dai":

                dai_lunarURL = "https://dkhpfm5hits1w.cloudfront.net/dai.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        update,
                        context
                    ),
                    document = dai_lunarURL
                )

            # + ------------------------------------------------- + #
            #   END of Stablecoin section of fiat currency clause
            # + ------------------------------------------------- + #

            # + ------------------------------------------------- + #
            #                  ALGORAND ECOSYSTEM
            # + ------------------------------------------------- + #

            # Planetwatch
            elif crypto_sym == "planetwatch":

                print(market_change)
                planetWatch_URL = "https://assets.coingecko.com/coins/images/16127/small/cwCG_U8M_400x400.png"

                context.bot.send_document(
                    chat_id = get_chat_id(
                        context,
                        update
                    ),
                            document = planetWatch_URL
                )

            # What's the bot gets to parse to user out in chat prompt
            # ----------------------------------------------------- #
            chile_call = "🇨🇱 Republic of Chile (Peso)"
            currency_symbolCLR = "$"
            fiat_collectEmpty += chile_call
            fiat_parse_symbols += currency_symbolCLR
            # ----------------------------------------------------- #

        else:
            print("complete")

        string_to_parse = str(market_change)

        replace_chars = re.sub(
            "[('{}')]", "\n",
            string_to_parse
        )

        # ToDo --> loop data through tokenizer

        update.message.reply_text(
            f"<strong>🔥FireCrypt-Bot</strong> \n\n"
            f"🔥 💎 🏦 💸 ⛓ 💸  🏦 💎 🔥 \n"

            f"<strong>{replace_chars}</strong> \n"
            f"🔥 💎 🏦 💸 ⛓ 💸  🏦 💎 🔥 \n\n",
                parse_mode = "html"
        )

        # Now replace characters of strings, so that we can only
        # parse the 24 hour chnage, according to fiat currency of what
        # crypto currency the user is requesting to look at with
        # CoinGeckoApI(). . . .

        # Replace dictionary keys with whitespace, and only
        # leave numeric values left over

# ** ========================================================================== ** #
def save_chart(update, context):

    # ------------------------------------------ #
    """
    :return: This function will save the chart generated
             by the bot, in filepath of the user's system
    """
    # ------------------------------------------ #

    # Get what crypto currency from user
    update.message.reply_text(f"What crypto currency would you like to chart?")

    res = requests.get('https://api.coingecko.com/api/v3/coins/polkadot/market_chart?vs_currency=zar&days=1')
    prices_res = res.json().get('prices')

    # Our conditional to handle the data
    for price in prices_res:
        dt_object = datetime.utcfromtimestamp(price[0] / 1000)
        price[0] = dt_object.strftime("%H:%M:%S")

    # Make our Pandas DataFrame
    df = pd.DataFrame(

        dict(
            time = [i[0] for i in prices_res],
            price = [i[1] for i in prices_res],
        )
    )

    # If there is no directory called "images", the script must
    # make ne in the user's executable filepath
    if not os.path.exists("images"):
        os.mkdir("images")

    # Once that is all done, we ca use the meta data
    # and utilize PIL library to make the wallpaper of the chart

    # To make image output to chat prompt we need to use .send_document
    # method. To achieve that the conditional must process the given image
    # as a variable, and not a raw string
    my_image =  Image.open("images/wallpaper_Polkadot.png")

    # Our image we use for background
    with my_image as bg_image:

        fig = go.Figure()  # Establish the main Object of PIL Lib

        # Here we make our tracers aong the series-plot
        fig.add_trace(

            go.Scatter(

                x = df['time'],    # Variable to output Time
                y = df['price'],   # Variable to output Price @Time Variable
                line = dict(width = 6), # Make line and it width
                mode = 'lines')
        )

        # Now lay it all out
        fig.update_layout(

            plot_bgcolor = "#141721",  # Background Color
            yaxis_title = "Price",     # title of Y-Axis
            xaxis_title = "Last 24h",  # title of Y-Axis
            xaxis_showgrid = False,
            yaxis_gridcolor = "#2f4a66",
            yaxis_tickformat = ".12f",
            yaxis_linecolor='#4a89ff', # the color of plotting line

            height = 512,
            width = 1052,

            margin = dict(
                r = 0, l = 10,
                b = 10, t = 0
            ),

            font = dict(size=24)

        )

        fig.add_layout_image(

            dict(

                source = bg_image,
                xref = "paper",
                yref = "paper",
                x = 0,
                y = 1,
                sizex = 1,
                sizey = 1,

                sizing = "stretch",
                opacity = 0.3,
                layer = "below"
            )
        )

        fig.write_image("images/")


# ** ========================================================================== ** #


# ** ========================================================================== ** #


# ** ========================================================================== ** #
#
# ** ========================================================================== ** #
def error(update, context):

    # * ---------------------------------------- * #
    """ Log errors caused by updates....
    :param update: IF there is an error let this except it
                   and handle it. instead of ugly shit
    :return:
    """
    # * ---------------------------------------- * #
    logging.warning("Update '%s'", update)
    logging.exception(context.error)
    # * ---------------------------------------- * #

# ** ========================================================================== ** #
def main() -> None:

    # ++ --------------------------------- ++ #
    """
      :return:  Bind Token Key to command called
                by user of FinAIpp on Telegram
    """
    # ++ --------------------------------- ++ #
    # Update the call from user to accept's bot's token and Api Key
    updater = Updater(TELEGRAM_TOKEN,
                      use_context = True) # Means "Yes use what user described for command

    # Dispatch the context given to bot to update its instance
    dp = updater.dispatcher

    # ---------------------------------------------------- #
    #       Our Command Handler defined into main()
    # ---------------------------------------------------- #

    # This handles the commands the user give user gives bot to get context
    # to give a response to what the user is instigating it to do
    dp.add_handler(
        CommandHandler(
            "menu",
            menu          # For "/start" command from user
        )
    )



    dp.add_handler(
        CommandHandler(                # Return's Public company ticker stock options
            "ticker", get_shareTicker
        )
    )

    dp.add_handler(
        CommandHandler(
            "coin", coin_data
        )
    )

    dp.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    dp.add_handler(               # Command: "/sentiment", to return AI Sentiment Analyzer
        CommandHandler(
            "sentiment",          # What the user types to chatbot
            social_sentiment      # Our Python function
        )
    )

    dp.add_handler(
        CommandHandler(
            "riddle", riddle_cipher
        )
    )

    dp.add_handler(
        CommandHandler(
            "riddler", continue_riddle
        )
    )


    dp.add_handler(
        CommandHandler(
            "secrets",
            math_secrets

        )
    )

    # Test test Riddler Decrypt
    dp.add_handler(
        CommandHandler(
            "unlock",
            unlock
        )
    )

#    dp.add_handler(
#        CommandHandler(
#            "caesar_riddle",
#            caesar_riddle
#        )
#    )

    # Just a hidden function for bot or admin to check
    # chat_id's for troubleshooting
    dp.add_handler(
        CommandHandler(
            "chatid",
            get_chat_id
        )
    )

    # log all error and use function in Telegram dispatcher
    dp.add_error_handler(error)

    # ---------------------------------------------------- #
    #                 END of CommandHandlers
    # ---------------------------------------------------- #

    # Use this to start the Telegram Bot
    updater.start_polling()

    # toDO --> *** Deploy via a Google App Engine or Heroku. Might
    #          as use Google App Engine. I play for use of their
    #          Cloud Platform. ***

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle() # Keep it "idle", so it can wait for commands by users on Telegram

# ** ====================================================== ** #
#    Our maineventLoop() and App's Main Wrapper
# ** ====================================================== ** #
if __name__ == "__main__":
    # Run the bot commands defined in main()
    #app.run_server(debug = True) # Web-App Dash board
    main()
# ** ====================================================== ** #
