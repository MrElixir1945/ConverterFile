import os
import subprocess
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from PIL import Image

# --- KONFIGURASI ---
TOKEN = "Change_to_your_token"
TEMP_DIR = "temp_files"

# Setup Logging (Biar tau kalau ada error)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Pastikan folder temp ada
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- FUNGSI PROSES (THE CORE LOGIC) ---

def compress_pdf_logic(input_path, output_path):
    # Menggunakan Ghostscript (Setting 'ebook' = 150dpi, balance size/quality)
    cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    subprocess.run(cmd, check=True)

def convert_docx_logic(input_path, output_dir):
    # Menggunakan LibreOffice Headless
    cmd = [
        "libreoffice", "--headless", "--convert-to", "pdf",
        "--outdir", output_dir, input_path
    ]
    subprocess.run(cmd, check=True)

def compress_image_logic(input_path, output_path, format="JPEG"):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        # Quality 60 cukup drastis nurunin size tapi masih enak dilihat
        img.save(output_path, format=format, quality=60, optimize=True)

# --- HANDLERS BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Kirim file Gambar, PDF, atau Word (DOCX).\n"
        "Saya akan bantu kompres atau konversi formatnya."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1]
    
    # Kalau user kirim foto via "Send as File" (Document) atau Gallery (Photo)
    is_photo = False
    file_id = ""
    file_name = ""

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = f"{file_id}.jpg"
        is_photo = True
    else:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        
    # Download File
    new_file = await context.bot.get_file(file_id)
    input_path = os.path.join(TEMP_DIR, file_name)
    await new_file.download_to_drive(input_path)

    # Simpan path di context user buat diproses nanti
    context.user_data['input_path'] = input_path
    context.user_data['file_name'] = file_name

    # Tentukan Tombol berdasarkan tipe file
    keyboard = []
    fname_lower = file_name.lower()

    if fname_lower.endswith(('.jpg', '.jpeg', '.png', '.webp')) or is_photo:
        keyboard = [
            [InlineKeyboardButton("📉 Kompres JPG (Small)", callback_data="img_compress")],
            [InlineKeyboardButton("🔄 Convert to PDF", callback_data="img_to_pdf")]
        ]
    elif fname_lower.endswith('.pdf'):
        keyboard = [
            [InlineKeyboardButton("📉 Kompres PDF (eBook Quality)", callback_data="pdf_compress")]
        ]
    elif fname_lower.endswith('.docx'):
        keyboard = [
            [InlineKeyboardButton("📄 Convert Word to PDF", callback_data="docx_to_pdf")]
        ]
    else:
        await update.message.reply_text("Format file tidak didukung atau belum dikenali.")
        os.remove(input_path) # Hapus langsung kalau gak guna
        return

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"File diterima: {file_name}\nMau diapain?", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Biar loading di tombol ilang
    
    input_path = context.user_data.get('input_path')
    original_name = context.user_data.get('file_name')
    
    if not input_path or not os.path.exists(input_path):
        await query.edit_message_text("Maaf, file sudah kadaluarsa/terhapus. Kirim ulang ya.")
        return

    await query.edit_message_text("⏳ Sedang memproses... Tunggu bentar ya server kentang.")

    output_path = ""
    action = query.data

    try:
        # --- LOGIC PEMROSESAN ---
        if action == "img_compress":
            output_path = os.path.join(TEMP_DIR, f"compressed_{original_name}")
            compress_image_logic(input_path, output_path)
        
        elif action == "img_to_pdf":
            output_path = os.path.join(TEMP_DIR, f"{os.path.splitext(original_name)[0]}.pdf")
            img = Image.open(input_path).convert("RGB")
            img.save(output_path)

        elif action == "pdf_compress":
            output_path = os.path.join(TEMP_DIR, f"compressed_{original_name}")
            compress_pdf_logic(input_path, output_path)

        elif action == "docx_to_pdf":
            # LibreOffice outputnya otomatis nama sama dgn ekstensi pdf
            convert_docx_logic(input_path, TEMP_DIR)
            # Kita perlu tau nama output pastinya
            base_name = os.path.splitext(original_name)[0]
            output_path = os.path.join(TEMP_DIR, f"{base_name}.pdf")

        # --- KIRIM HASIL ---
        if os.path.exists(output_path):
            await context.bot.send_document(chat_id=query.message.chat_id, document=output_path, caption="✅ Nih hasilnya!")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="❌ Gagal memproses file.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await context.bot.send_message(chat_id=query.message.chat_id, text="❌ Terjadi error di server.")
    
    finally:
        # --- CLEANUP (Wajib Hapus File!) ---
        # Hapus file input
        if os.path.exists(input_path):
            os.remove(input_path)
        # Hapus file output
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Bot Tukang-Print Berjalan...")
    app.run_polling()