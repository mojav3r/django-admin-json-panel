import random
import uuid

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_meta_data(data, field):
    main_key = next(iter(data.keys()), None)
    if main_key is None:
        return ''

    def get_nested_value(data, keys):
        if not isinstance(data, dict):
            return ''
        keys_copy = keys[:]  # Create a copy of keys
        key = keys_copy.pop(0)
        value = data.get(key, {})
        if keys_copy:
            return get_nested_value(value, keys_copy)
        return value

    if '.' in field:
        keys = field.split('.')
        return get_nested_value(data.get(main_key, {}).get('Meta_Data', {}), keys)
    else:
        return data.get(main_key, {}).get('Meta_Data', {}).get(field, '')


# @register.filter
# def get_meta_data(data, field):
#     # Find the first key in the JSON object (this assumes there is only one top-level key)
#     if not isinstance(data, dict):
#         return ''
#
#     main_key = next(iter(data.keys()), None)
#     if main_key is None:
#         return ''
#
#     # Retrieve the value from the Meta_Data
#     return data.get(main_key, {}).get('Meta_Data', {}).get(field, '')



@register.simple_tag
def render_meta_data(data):
    def render_nested_data(meta_data, parent_key='', depth=0, parent_id=''):
        html = ''
        for key, value in meta_data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            accordion_id = f"{str(uuid.uuid4()).replace('-', '_')}_{depth}"  # Generate a unique ID for each accordion
            collapse_id = f"collapse_{accordion_id}"
            heading_id = f"heading_{accordion_id}"

            if isinstance(value, dict):
                # Create an accordion for nested data
                html += f"""
                <div class="card">
                    <div class="card-header" id="{heading_id}">
                        <h5 class="mb-0">
                            <button style="display:flex;" class="btn btn-link" type="button" data-toggle="collapse" data-target="#{collapse_id}" aria-expanded="true" aria-controls="{collapse_id}">
                                {key} <i class="ri-arrow-down-s-line"></i>
                            </button>
                        </h5>
                    </div>
                    <div id="{collapse_id}" class="collapse" aria-labelledby="{heading_id}" data-parent="#{parent_id}">
                        <div class="card-body">
                            {render_nested_data(value, full_key, depth + 1, collapse_id)}
                        </div>
                    </div>
                </div>
                """
            else:
                # Display the value directly
                html += f"<p><strong>{key}:</strong> {value}</p>"
        return html

    main_key = next(iter(data.keys()), None)
    if main_key is None:
        return ''

    meta_data = data.get(main_key, {}).get('Meta_Data', {})
    html_content = f"<div id='accordion_0' class='accordion'>{render_nested_data(meta_data, parent_id='accordion_0')}</div>"
    return mark_safe(html_content)


@register.simple_tag
def render_result_data(data):
    def render_nested_data(meta_data, parent_key='', depth=0, parent_id=''):
        html = ''
        for key, value in meta_data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            accordion_id = f"{str(uuid.uuid4()).replace('-', '_')}_{depth}"  # Generate a unique ID for each accordion
            collapse_id = f"collapse_{accordion_id}"
            heading_id = f"heading_{accordion_id}"

            if isinstance(value, dict):
                # Create an accordion for nested data
                html += f"""
                <div class="card">
                    <div class="card-header" id="{heading_id}">
                        <h5 class="mb-0">
                            <button class="btn btn-link" type="button" data-toggle="collapse" data-target="#{collapse_id}" aria-expanded="true" aria-controls="{collapse_id}">
                                {key}
                            </button>
                        </h5>
                    </div>
                    <div id="{collapse_id}" class="collapse" aria-labelledby="{heading_id}" data-parent="#{parent_id}">
                        <div class="card-body">
                            {render_nested_data(value, full_key, depth + 1, collapse_id)}
                        </div>
                    </div>
                </div>
                """
            else:
                # Display the value directly inside the accordion
                value_str = str(value).replace('\n', '<br>')  # Ensure newlines are converted to HTML breaks
                html += f"""
                <div class="card">
                    <div class="card-header" id="{heading_id}">
                        <h5 class="mb-0">
                            <button class="btn btn-link" type="button" data-toggle="collapse" data-target="#{collapse_id}" aria-expanded="true" aria-controls="{collapse_id}">
                                {key}
                            </button>
                        </h5>
                    </div>
                    <div id="{collapse_id}" class="collapse" aria-labelledby="{heading_id}" data-parent="#{parent_id}">
                        <div class="card-body">
                            {value_str}
                        </div>
                    </div>
                </div>
                """
        return html

    main_key = next(iter(data.keys()), None)
    if main_key is None:
        return ''

    result_data = data.get(main_key, {}).get('Results', {})
    html_content = f"<div id='accordion_0' class='accordion'>{render_nested_data(result_data, parent_id='accordion_0')}</div>"
    return mark_safe(html_content)
