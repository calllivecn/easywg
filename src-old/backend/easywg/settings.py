"""
Django settings for easywg project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mj6u2ku8ni*e!5xrapqa(g8g%v%ap+e+ubcxjs%v=y)4#wot6#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    #'django.contrib.staticfiles',

    "wg.apps.WgConfig",
]
#CSRF_COOKIE_HTTPONLY = True
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "easywg.wgmiddleware.Body2Json",
]

ROOT_URLCONF = 'easywg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'easywg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# add $HOME/.easywg/
DB = os.path.expanduser("~/.easywg")
if os.path.exists(DB) and os.path.isdir(DB):
    pass
else:
    os.mkdir(DB)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': os.path.join(DB, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# 这是url里的静态文件路径前缀
STATIC_URL = '/static/'

WEB_ROOT = os.path.join(BASE_DIR, "web_root")

# 这是实际在文件系统里找静态文件的路径。
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]



# logging

ENV = os.environ.get("ENV")

if ENV == "DEBUG":
    LOGGER_LEVEL = "DEBUG"
else:
    LOGGER_LEVEL = "INFO"

# LOGGING
LOGGING = {
    'version' : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'httpRequest': {
            'format': '%(asctime)s.%(msecs)d %(levelname)s %(filename)s:%(lineno)d %(message)s',
            'datefmt': "%H:%M:%S",
            }
    },
    'handlers': {
        #'info': {
        #    'level': 'INFO',
        #    'class': 'logging.handlers.TimedRotatingFileHandler',
        #    'filename': os.path.join("..", "logs", "info.log"),
        #    'when': "midnight",
        #    'backupCount': 7,
        #    'formatter': 'httpRequest',
        #},
        #'error': {
        #    'level': 'ERROR',
        #    'class': 'logging.handlers.TimedRotatingFileHandler',
        #    'filename': os.path.join("..", "logs", "error.log"),
        #    'when': "midnight",
        #    'backupCount': 7,
        #    'formatter': 'httpRequest',
        #},
        'console': {
            #'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'httpRequest',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOGGER_LEVEL,
            'propagate': False,
        }
    }
}