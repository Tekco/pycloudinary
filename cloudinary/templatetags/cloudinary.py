from __future__ import absolute_import

import json
 
from django import template
from django.forms import Form

import cloudinary
from cloudinary import CloudinaryImage, utils, uploader
from cloudinary.compat import string_types
from cloudinary.forms import CloudinaryJsFileField, cl_init_js_callbacks

register = template.Library()

@register.simple_tag(takes_context=True)
def cloudinary_url(context, source, options_dict={}, **options):
    options = dict(options_dict, **options)
    try:
        if context['request'].is_secure() and 'secure' not in options:
            options['secure'] = True
    except KeyError:
        pass
    if isinstance(source, string_types):
        m = utils.API_URL_REGEX.search(source)
        if m:
            source = CloudinaryImage(m.group('public_id'), format=m.group('image_format'), version=m.group('version'),
                                     signature=m.group('signature'), type=m.group('image_type'))
    if not isinstance(source, CloudinaryImage):
        source = CloudinaryImage(source)
    return source.build_url(**options)

@register.simple_tag(name='cloudinary', takes_context=True)
def cloudinary_tag(context, image, options_dict={}, **options):
    options = dict(options_dict, **options)
    try:
        if context['request'].is_secure() and 'secure' not in options:
            options['secure'] = True
    except KeyError:
        pass
    if isinstance(image, string_types):
        m = utils.API_URL_REGEX.search(image)
        if m:
            image = CloudinaryImage(m.group('public_id'), format=m.group('image_format'), version=m.group('version'),
                                     signature=m.group('signature'), type=m.group('image_type'))
    if not isinstance(image, CloudinaryImage):
        image = CloudinaryImage(image)
    return image.image(**options)

@register.simple_tag
def cloudinary_direct_upload_field(field_name="image", request=None):
    form = type("OnTheFlyForm", (Form,), {field_name : CloudinaryJsFileField() })()
    if request:
        cl_init_js_callbacks(form, request)
    return unicode(form[field_name])

"""Deprecated - please use cloudinary_direct_upload_field, or a proper form"""
@register.inclusion_tag('cloudinary_direct_upload.html')
def cloudinary_direct_upload(callback_url, **options):
    params = utils.build_upload_params(callback=callback_url, **options)
    params = utils.sign_request(params, options)    
    
    api_url = utils.cloudinary_api_url("upload", resource_type=options.get("resource_type", "image"), upload_prefix=options.get("upload_prefix"))

    return {"params": params, "url": api_url}

@register.inclusion_tag('cloudinary_includes.html')
def cloudinary_includes(processing=False):
    return {"processing": processing}

CLOUDINARY_JS_CONFIG_PARAMS = ("api_key", "cloud_name", "private_cdn", "secure_distribution", "cdn_subdomain")
@register.inclusion_tag('cloudinary_js_config.html')
def cloudinary_js_config():
    config = cloudinary.config()
    return dict(
        params = json.dumps(dict(
          (param, getattr(config, param)) for param in CLOUDINARY_JS_CONFIG_PARAMS if getattr(config, param, None)
        ))
    )
