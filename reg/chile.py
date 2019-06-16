"""Chile specific form helpers from django-flavors modified for this particular app"""

from __future__ import unicode_literals

from django.forms import ValidationError
from django.forms.fields import RegexField, Select
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

class CLRutField(RegexField):
    """
    Chilean "Rol Unico Tributario" (RUT) field.

    This is the Chilean national identification number.

    Samples for testing are available from
    https://palena.sii.cl/cvc/dte/ee_empresas_emisoras.html
    """

    default_error_messages = {
        'invalid': _('Ingresa un RUN válido'),
        'strict': _('Ingresa un RUN válido. El formato es XX.XXX.XXX-X'),
        'checksum': _('Este RUN no es válido'),
    }

    def __init__(self, *args, **kwargs):
        if 'strict' in kwargs:
            del kwargs['strict']
            super(CLRutField, self).__init__(r'^(\d{1,2}\.)?\d{3}\.\d{3}-[\dkK]$', error_messages={'invalid': self.default_error_messages['strict']}, *args, **kwargs)
        else:
            # In non-strict mode, accept RUTs that validate but do not exist in
            # the real world.
            super(CLRutField, self).__init__(r'^[\d\.]{1,11}-?[\dkK]$', *args, **kwargs)

    def clean(self, value):
        """Check and clean the Chilean RUT."""
        super(CLRutField, self).clean(value)
        if value in self.empty_values:
            return self.empty_value
        rut, verificador = self._canonify(value)
        if self._algorithm(rut) == verificador:
            return self._format(rut, verificador)
        else:
            raise ValidationError(self.error_messages['checksum'])


    def _algorithm(self, rut):
        """Takes RUT in pure canonical form, calculates the verifier digit."""
        suma = 0
        multi = 2
        for r in rut[::-1]:
            suma += int(r) * multi
            multi += 1
            if multi == 8:
                multi = 2
        return '0123456789K0'[11 - suma % 11]

    def _canonify(self, rut):
        """Turns the RUT into one normalized format. Returns a (rut, verifier) tuple."""
        rut = force_text(rut).replace(' ', '').replace('.', '').replace('-', '')
        return rut[:-1], rut[-1].upper()

    def _format(self, code, verifier=None):
        """
        Formats the RUT from canonical form to the common string representation.

        If verifier=None, then the last digit in 'code' is the verifier.
        """
        if verifier is None:
            verifier = code[-1]
            code = code[:-1]
        return f'{code}{verifier}'
