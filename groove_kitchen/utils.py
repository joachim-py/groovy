import re, secrets, string
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+[^.]@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def generate_validation_code(length=10):
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_email(subject, body_text, body_html, from_email, to_email):
    send_mail(
           subject,
           body_text,
           from_email,
           [to_email],
           fail_silently=False,
           html_message=body_html
       )
    # msg = EmailMultiAlternatives(subject, body_text, from_email, [to_email])
    # msg.attach_alternative(body_html, "text/html")
        
    try:
        # msg.send()
        print(f'Email was sent to {to_email}!')
    except Exception as e:
        print(f'Email not sent to {to_email}: {str(e)} ')

