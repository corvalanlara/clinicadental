from django import template

register = template.Library()

@register.filter
def absoluto(value):
    return abs(value)

@register.filter(name='en_grupo')
def en_grupo(usuario, grupo):
    return usuario.groups.filter(name=grupo).exists()
