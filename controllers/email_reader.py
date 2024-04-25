from flask import Blueprint, jsonify
from datetime import datetime, timedelta
import imaplib
import email
from email.header import decode_header
import os

email_reader_bp = Blueprint('email_reader', __name__)

@email_reader_bp.route('/email_reader', methods=['GET'])
def ler_email():
    try:
        mail = imaplib.IMAP4_SSL(os.getenv('IMAP_SERVER'))
        mail.login(os.getenv('EMAIL'), os.getenv('PASSWORD'))
    except imaplib.IMAP4.error as e:
        return jsonify({"message": f"Erro ao conectar ou fazer login: {e}"}), 500
    except Exception as e:
        return jsonify({"message": f"Erro desconhecido: {e}"}), 500

    mail.select("inbox")
    
    # status, data = mail.list()
    # for box in data:
    #     print(box)

    date_since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    status, data = mail.search(None, f"SINCE {date_since}")

    emails = []
    for num in data[0].split():
        status, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_header(msg["Subject"])[0][0]
        from_ = decode_header(msg.get("From"))[0][0]
        date_received = msg.get("Date")
        # Format received date
        date_received_datetime = datetime.strptime(date_received, "%a, %d %b %Y %H:%M:%S %z")

        # i know!!!!!!
        formatted_date = date_received_datetime.strftime("%d-%m-%Y_%H-%M-%S")
        formatted_date2 = date_received_datetime.strftime("%d-%m-%Y")
        formatted_date3 = date_received_datetime.strftime("%d/%m/%Y %H:%M:%S")

        email_info = {
            "subject": subject,
            "from": from_,
            "date_received": formatted_date3,
            "body": "",
            "attachments": 0,
            "pdfs": 0
        }

        # Create folder name with subject and date
        email_id = f"{formatted_date}-{subject}"

        folder_name = f"emails/{formatted_date2}/{email_id}" 
        os.makedirs(folder_name, exist_ok=True)

        with open(os.path.join(folder_name, "body.txt"), "w", encoding="utf-8") as text_file:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    filename = part.get_filename()
                    
                    if content_type == "text/plain" and not filename:
                        body = part.get_payload(decode=True).decode()
                        text_file.write(body)
                        email_info["body"] = body
                    else:
                        email_info["attachments"] += 1
                        
                    # if there is a pdf attached to the email then save it
                    if content_type == "application/pdf" and filename:
                        email_info["pdfs"] += 1
                        with open(os.path.join(folder_name, filename), "wb") as attachment_file:
                            attachment_file.write(part.get_payload(decode=True))
            else:
                body = msg.get_payload(decode=True).decode()
                text_file.write(body)
                email_info["body"] = body

            emails.append(email_info)

    mail.close()
    mail.logout()

    return jsonify({"emails": emails}), 200