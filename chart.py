# * $ * ======================================================================================================== * $ * #
"""
        This script makes up a simple crypto-seeker for FinAIpp AI Social-Agent
        It comes an article I read on Medium.com
"""
# * $ * ======================================================================================================== * $ * #
# import our shit
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timezone

import os
import requests
from PIL import Image

import logging

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

# *** ========================================================== *** #
# Logger
# set up logging
logging.basicConfig(
    level = logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# My Token from Telegram API
telegram_bot_token = "1674512739:AAGppjamnxhmJ57GSkeSySBwWMbaSojwJmA"

# ============================================================== #
#                      OuR INITIALIZER (/start)                  #
# ============================================================== #
def start(update, context):

    # ------------------------------- #
    """
    :param update:
    :param context:
    :return:
    """
    # ------------------------------- #
    update.message.text_reply("WElcome")

# ============================================================== #
def save_chart():

    # ------------------------------------------ #
    """
    :return: This function will save the chart generated
             by the bot, in filepath of the user's system
    """
    # ------------------------------------------ #

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

        fig.write_image("images/wallpaper_Polkadot.png")

def chart(update, context):

    # -------------------------------------------- #
    """
    :param update:
    :param context:
    :return:
    """
    # -------------------------------------------- #
    chat_id = update.effective_chat.id
    save_chart()  # Call the metadata

    # Inform the user that the bot is creating hers or his graph
    update.message.reply_text("Generating Time Graph for "
                              "<strong>Polkadot Native coin DOT. . .</strong>",
                              parse_mode = "html"
    )

    # Use Telegram API method to send pic to make wallpaper
    context.bot.send_photo(

        chat_id,
            photo = open(
                "images/wallpaper_Polkadot.png"  # The photo from bigwinit local machine
        ),
    )

    # Now we need to send the photo as a document,
    # Giving user choice to download generate Chart
    # So we use .bot.send_document. . .

    # toDO --> Ag fuuck man. It needs to send shit back as a
    #            a document, as a doc is noy the same thing thing as
    #            as .send_photo() method.
    #            Wrong contextial use of Telegram Bot HTTP API


# For Error Handling
def error(update, context):

    # * ------------------------------------------------------ * #
    """
    :param update:    Just in case some sort of error happens, the bot will
                      spit out this exception
    :param context:   The context? There is an error, the bot does not know what is
                      happening!! Spit out exception!!
    :return:          A special function for hadling an error generated by bot or user
    """
    # * ------------------------------------------------------ * #
    # Log the error in server terminal
    logger.warning("Update '%s' caused error '%s'",
                   update,
                   context.error
    )

    # Now the user the dumb prick user her or she made botty bot confused!
 #   update.message.reply_text("I'm sorry this is me spitting out an exception!"
 #                             "I don't understand what is happening. I have lost context! \n"
 #                             "Please enter your command. Probably a typo on your behalf."
 #   )

# ** ============================================================================ ** #
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
# ** ============================================================================ ** #

def main():

    # --------------------------------------- #
    """
    :return: The main application EventLoop()
    """
    # --------------------------------------- #
    updater = Updater(
        token = telegram_bot_token,
        use_context = True
    )

    dispatcher = updater.dispatcher

    # My error Handler
    dispatcher.add_error_handler(error)

    # Init
    dispatcher.add_handler(
        CommandHandler(
            "start", start
        )
    )

    # The chart will start when th user gives the command '/chart'
    dispatcher.add_handler(
        CommandHandler(
            "chart", chart
        )
    )

    # Now start listening for commands from user
    updater.start_polling()  # Start bot on BigWinIT.com Local machine
    updater.idle()

if __name__ == "__main__":
    # Wrap into even loop
    main()

