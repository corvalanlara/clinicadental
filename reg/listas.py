import datetime

genero_opciones = (
    ('cf', 'Femenino'),
    ('cm', 'Masculino'),
    ('tf','Transfemenino'),
    ('tm', 'Transmasculino'),
    ('nb','No binario'),
    ('nd','No declara'),
)

convenio_opciones = (
    ('fo', 'Fonasa'),
    ('is', 'Isapre'),
)

especialidades = (
    ('or', 'Ortodoncista'),
    ('ci', 'Cirujano'),
    ('od', 'Odontólogo'),
    ('hi', 'Higienista'),
)

años = sorted([x for x in range(datetime.date.today().year - 100, datetime.date.today().year + 1)], reverse=True)
