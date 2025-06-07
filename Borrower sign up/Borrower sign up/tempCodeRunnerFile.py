from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Regexp
from datetime import datetime, date
import re
import json
import logging
from werkzeug.security import generate_password_hash
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib