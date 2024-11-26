from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import re

# Valida si un enlace es de TikTok, aceptando diferentes formatos
def is_valid_tiktok_url(url):
    # Patrón para cubrir varios formatos de enlaces de TikTok
    pattern = r"(https?://)?(www\.)?(tiktok\.com/.*|vm\.tiktok\.com/\w+)"
    return re.match(pattern, url)

# Descarga el video con yt-dlp y guarda el archivo localmente
def download_with_ytdlp(video_url, output_path):
    try:
        ydl_opts = {
            'format': 'best[filesize<=50M]',  # Asegura que el video sea menor a 50 MB
            'outtmpl': output_path,          # Nombre del archivo descargado
            'quiet': True,                   # Suprime mensajes en consola
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return output_path
    except Exception as e:
        print(f"Error en yt-dlp: {e}")
        return None

# Manejador de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if is_valid_tiktok_url(text):
        await update.message.reply_text("Descargando video de TikTok, por favor espera...")
        
        # Ruta temporal para almacenar el video
        output_path = "temp_video.mp4"
        
        # Descarga el video localmente
        video_path = download_with_ytdlp(text, output_path)
        
        if video_path and os.path.exists(video_path):
            try:
                # Abre el archivo en modo binario y envía el video
                with open(video_path, 'rb') as video_file:
                    await context.bot.send_video(chat_id=chat_id, video=video_file, caption="Aquí está tu video 🎥")
            except Exception as e:
                print(f"Error al enviar el video: {e}")
                await update.message.reply_text(
                    "No se pudo enviar el video. Asegúrate de que el tamaño sea menor a 50 MB o prueba con otro enlace."
                )
            finally:
                # Elimina el archivo local después de enviarlo
                if os.path.exists(video_path):
                    os.remove(video_path)
        else:
            await update.message.reply_text(
                "No se pudo descargar el video. Esto puede deberse a un enlace inválido, un video privado, "
                "o un problema técnico. Por favor, intenta con otro enlace."
            )
    else:
        await update.message.reply_text("Por favor, envíame un enlace válido de TikTok.")

# Función principal
def main():
    TOKEN = "7965523204:AAGJuyyBvT3FtE1eVZytOGr1CtKN1WmIppo"  # Reemplaza con tu token del BotFather
    app = ApplicationBuilder().token(TOKEN).build()

    # Agregar manejador de mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Ejecutar el bot
    app.run_polling()

if __name__ == '__main__':
    main()
