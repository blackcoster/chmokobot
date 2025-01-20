import face_recognition
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import logging

# Set your Telegram Bot token here
TOKEN = 'TOKEN'

def start(update: Update, context: CallbackContext) -> None:

    log.write(str(update.message.date)+' '+ str(update.message.from_user.first_name)+ ' '+str(update.message.text)+'\n')
    log.flush()
    update.message.reply_text('send me your selfie (a proper one where you face is seen properly)')


def find_tip(image):
    # Convert Pillow Image to NumPy array
    image_array = np.array(image)

    face_landmarks_list = face_recognition.face_landmarks(image_array)
    if not face_landmarks_list:
        print('no face')
        return -1, 60

    face_landmarks = face_landmarks_list[0]
    nose_bridge = face_landmarks['nose_bridge']
    nose_tip = face_landmarks['nose_tip']

    wid = abs(nose_tip[1][0] - nose_tip[3][0]) * 2
    tip = (int(nose_bridge[-1][0]), int(nose_bridge[-1][1]))

    return tip, wid


def analyze_photo(photo_bytes: bytes) -> tuple:
    # Load the photo into a Pillow Image
    image = Image.open(BytesIO(photo_bytes))

    # Replace with your actual face_recognition logic
    tip, wid = find_tip(image)

    # Perform the kiss overlay


    return tip, wid


def handle_photo(update: Update, context: CallbackContext) -> None:
    # Check if a photo is received
    log.write(str(update.message.date) +' '+ str(update.message.from_user.first_name) + ' фото\n')
    log.flush()
    if update.message.photo:
        # Get the largest available photo

        photo = update.message.photo[-1]
        file_id = photo.file_id

        # Download the photo
        file = context.bot.get_file(file_id)

        photo_bytes = file.download_as_bytearray()

        # Analyze the photo
        tip, wid = analyze_photo(photo_bytes)
        if tip == -1:
            update.message.reply_text('no this photo won\'t work')
        else:
            edited = kiss('path_to_original.jpg', 'kiss.png',
                          'output_with_kiss.jpg', wid, tip, photo_bytes)
            # Send the result back to the user along with the resulting photo
            result_message = f'hahaaaa you have been KISSED'
            update.message.reply_text(result_message)

            # Send the resulting photo
            update.message.reply_photo(photo=BytesIO(edited))
    else:
        update.message.reply_text('Selfie plss')


def kiss(jpg_path, png_path, output_path, wid, tip,photo_bytes):
    # Open the JPG image

    jpg_image = image = Image.open(BytesIO(photo_bytes))

    # Open the PNG image with an alpha channel
    png_image = Image.open(png_path).convert("RGBA")
    resized_png = png_image.resize((int(wid), int(0.7 * wid)))

    transparent_background = Image.new("RGBA", jpg_image.size, (0, 0, 0, 0))
    overlay_position = (int(tip[0] - resized_png.size[0] * 0.5), int(tip[1] - resized_png.size[1]*0.5))

    transparent_background.paste(resized_png, overlay_position, resized_png)

    result = Image.alpha_composite(jpg_image.convert("RGBA"), transparent_background)

    output_bytes = BytesIO()
    result = result.convert("RGB")
    result.save(output_bytes, format="JPEG")
    output_bytes.seek(0)

    return output_bytes.read()




def main() -> None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Set up the bot and dispatcher
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Register the handlers
    dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, handle_photo))
    dp.add_handler(MessageHandler(Filters.command, start))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    with open('log.txt', 'a', encoding='utf-8', buffering=1) as log:
        main()