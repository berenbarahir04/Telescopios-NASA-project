import sys
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from mailersend import emails
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import random
import pymysql
import logging

pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Cargar configuración desde el archivo config.py
app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)

# Configuración de MailerSend
api_key = app.config['MAILERSEND_API_KEY']
mailer = emails.NewEmail(api_key)

# Modelos de base de datos
class Suscriptor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)

class PDF(db.Model):
    __tablename__ = 'pdfs'  # Especifica el nombre real de la tabla en la base de datos
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Imagenes_del_Dia')
def imagenes_del_dia():
    api_url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': 'YCN3Afvnayoo7OtmqYFBpqLmxShN7ebAP2UYECDN',
        'count': 5
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        news_data = response.json()
    except requests.RequestException as e:
        news_data = []
        print(f"Error al obtener datos de la API de la NASA: {e}")
    return render_template('imagenes_del_dia.html', news=news_data)

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        if not Suscriptor.query.filter_by(email=email).first():
            nuevo_suscriptor = Suscriptor(email=email)
            db.session.add(nuevo_suscriptor)
            db.session.commit()
            enviar_confirmacion(email)  # Enviar correo de confirmación al suscriptor
            return redirect(url_for('thank_you'))
        else:
            return render_template('subscribe.html', error="Este correo ya está suscrito.")
    return render_template('subscribe.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

def enviar_confirmacion(email):
    mail_body = {}
    mail_from = {
        "name": "Juan David",
        "email": "noreply@trial-jy7zpl97ve5g5vx6.mlsender.net",
    }
    recipients = [
        {
            "name": email.split('@')[0],
            "email": email,
        }
    ]
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Confirmación de suscripción", mail_body)
    mailer.set_html_content("Gracias por suscribirte a nuestro newsletter!", mail_body)
    mailer.set_plaintext_content("Gracias por suscribirte a nuestro newsletter!", mail_body)
    try:
        response = mailer.send(mail_body)
        print("Correo de confirmación enviado exitosamente:", response)
    except Exception as e:
        print("Error al enviar correo de confirmación:", e)

def enviar_pdf():
    with app.app_context():
        suscriptores = Suscriptor.query.all()
        pdfs = PDF.query.all()
        if pdfs:
            pdf = random.choice(pdfs)
            for suscriptor in suscriptores:
                mail_body = {}
                mail_from = {
                    "name": "Juan David",
                    "email": "noreply@trial-jy7zpl97ve5g5vx6.mlsender.net",
                }
                recipients = [
                    {
                        "name": suscriptor.email.split('@')[0],
                        "email": suscriptor.email,
                    }
                ]
                mailer.set_mail_from(mail_from, mail_body)
                mailer.set_mail_to(recipients, mail_body)
                mailer.set_subject("Descubrimiento del Telescopio James Webb", mail_body)
                mailer.set_html_content(f"Hola, aquí tienes un artículo interesante: {pdf.title}\n\nPuedes descargarlo desde el siguiente enlace: {pdf.url}", mail_body)
                mailer.set_plaintext_content(f"Hola, aquí tienes un artículo interesante: {pdf.title}\n\nPuedes descargarlo desde el siguiente enlace: {pdf.url}", mail_body)
                try:
                    response = mailer.send(mail_body)
                    print(f"Correo enviado exitosamente a {suscriptor.email}:", response)
                except Exception as e:
                    print(f"Error al enviar correo a {suscriptor.email}:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(func=enviar_pdf, trigger="interval", hours=24)  # Ejecutar cada 30 segundos para pruebas
scheduler.start()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
