import os
import datetime
import win32com.client

def get_current_directory():
    return os.path.abspath(os.getcwd())

def download_attachments_from_sender(sender_email, folder_name="Inbox", save_path="attachments"):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6 = Inbox

    if folder_name != "Inbox":
        inbox = inbox.Folders[folder_name]

    os.makedirs(save_path, exist_ok=True)
    # messages = inbox.Items
    # Filter emails from the last 2 days
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%m/%d/%Y %H:%M %p")
    restriction = f"[ReceivedTime] >= '{cutoff}'"
    messages = inbox.Items.Restrict(restriction)
    messages.Sort("[ReceivedTime]", True)

    print(f"Scanning messages from after: {cutoff}")

    # Optional: sort by date descending for performance
    messages.Sort("[ReceivedTime]", True)

    for message in messages:
        try:
            if message.Class == 43:  # MailItem
                # Match sender email
                if message.SenderEmailAddress.lower() == sender_email.lower():
                    attachments = message.Attachments
                    if attachments.Count > 0:
                        print("Count=" + str(attachments.Count))
                        for i in range(1, attachments.Count + 1):
                            attachment = attachments.Item(i)
                            file_path = os.path.join(save_path, attachment.FileName)
                            attachment.SaveAsFile(file_path)
                            print(f"Saved: {file_path}")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    download_attachments_from_sender(
        sender_email="sender-785@oracle.com",   # 🔁 Change to your target sender
        folder_name="Inbox",
        save_path=os.path.join(get_current_directory(), "DownloadedFiles")
    )
