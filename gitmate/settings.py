"""
Django settings for the GitMate project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from ast import literal_eval
import os

import djcelery

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            ('s#x)wcdigpbgi=7nxrbqbd&$yri@2k9bs%v@'
                             '*szo#&)c=qp+3-'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = literal_eval(os.environ.get('DJANGO_DEBUG', 'False'))
if DEBUG and not literal_eval(os.environ.get('FORCE_CELERY',
                                             'False')):  # pragma: nocover
    # let celery invoke all tasks locally
    CELERY_ALWAYS_EAGER = True
    # make celery raise exceptions when something fails
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

HOOK_DOMAIN = os.environ.get('HOOK_DOMAIN', 'localhost:8000')

# django>=1.11 requires tests to use allowed hosts
ALLOWED_HOSTS = ['testing.com', 'localhost', '127.0.0.1', 'localhost:4200',
                 HOOK_DOMAIN]
ALLOWED_HOSTS += os.environ.get('DJANGO_ALLOWED_HOSTS', '').split()
CORS_ORIGIN_WHITELIST = ALLOWED_HOSTS
CORS_ALLOW_CREDENTIALS = True

GITMATE_PLUGINS = [
    'code_analysis',
    'welcome_commenter',
    'auto_label_pending_or_wip',
    'pr_size_labeller',
    'issue_labeller',
    'bug_spotter',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'gitmate_config',
    'djcelery',
    'rest_framework',
    'rest_framework_docs',
    'corsheaders',
] + ['gitmate_'+plugin for plugin in GITMATE_PLUGINS]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    )
}

SOCIAL_AUTH_URL_NAMESPACE = 'auth'

# python-social-auth settings
SOCIAL_AUTH_LOGIN_REDIRECT_URL = os.environ.get('SOCIAL_AUTH_REDIRECT',
                                                'http://localhost:4200')
SOCIAL_AUTH_LOGIN_URL = '/login'

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social.pipeline.user.user_details',
)

# Put gitmate's corresponding OAuth details here.
GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')
SOCIAL_AUTH_GITHUB_KEY = os.environ.get('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_SCOPE = [
    'admin:repo_hook',
    'repo',
]

SOCIAL_AUTH_GITLAB_KEY = os.environ.get(
    'SOCIAL_AUTH_GITLAB_KEY')
SOCIAL_AUTH_GITLAB_SECRET = os.environ.get('SOCIAL_AUTH_GITLAB_SECRET')
# This needs to be specified as is including full domain name.
# ex. gitlab.com/auth/complete/gitlab/
SOCIAL_AUTH_GITLAB_REDIRECT_URL = os.environ.get(
    'SOCIAL_AUTH_GITLAB_REDIRECT_URL')

SOCIAL_AUTH_BITBUCKET_KEY = os.environ.get('SOCIAL_AUTH_BITBUCKET_KEY')
SOCIAL_AUTH_BITBUCKET_SECRET = os.environ.get('SOCIAL_AUTH_BITBUCKET_SECRET')

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.gitlab.GitLabOAuth2',
    'social_core.backends.bitbucket.BitbucketOAuth',
    'django.contrib.auth.backends.ModelBackend'
)

MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gitmate.disable_csrf.DisableCSRF',
]

ROOT_URLCONF = 'gitmate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'gitmate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_ADDRESS', ''),
        'PORT': os.environ.get('DB_PORT', '')
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT',
                             os.path.join(BASE_DIR, 'static'))
STATIC_URL = '/static/'
STATICFILES_DIRS = ()


# CELERY CONFIG
djcelery.setup_loader()

# RABBITMQ server base URL
BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                            'amqp://admin:password@rabbit/')
